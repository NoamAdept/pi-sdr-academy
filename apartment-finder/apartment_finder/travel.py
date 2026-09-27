"""Travel estimates to campus.

Public transit routing is not available from this environment. Walking uses
OSRM's foot profile. When the walk is longer than the cap, a free-flow drive
from OSRM is used only as a proxy, and the report names that mode.
"""

from __future__ import annotations

import json
import math
import time
import urllib.parse
import urllib.request

from apartment_finder.http_client import BROWSER_UA, FetchError, fetch

# Main TAU campus, Ramat Aviv (Chaim Levanon / Brodetsky area).
TAU_ANCHOR = (32.1133, 34.8044)
NOMINATIM = "https://nominatim.openstreetmap.org/search"
# router.project-osrm.org's "foot" profile returns driving speeds, so walking
# times come from the OSM.de foot router instead.
FOOT_ROUTER = "https://routing.openstreetmap.de/routed-foot/route/v1"
DRIVE_ROUTER = "https://router.project-osrm.org/route/v1"
NOMINATIM_UA = "tau-apartment-finder/1.0 (student housing search; educational)"


def _fold(value: str) -> str:
    return (
        value.replace("־", "")
        .replace("-", "")
        .replace(" ", "")
        .replace("׳", "")
        .replace("'", "")
    )


def _tokens_match(display: str, tokens: tuple[str, ...]) -> bool:
    folded = _fold(display)
    return any(_fold(token) in folded for token in tokens)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def assess_travel(
    walk_min: float | None,
    drive_min: float | None,
    straight_km: float | None,
    max_minutes: int,
    walk_source: str = "OSM foot router",
) -> tuple[bool, str, float | None]:
    """Decide whether a place is plausibly within the transit cap.

    Returns (keep, label, sort_minutes).
    """
    if walk_min is not None and walk_min <= max_minutes:
        return True, f"walking {round(walk_min)} min ({walk_source})", walk_min
    # Free-flow driving on this router is about 45 km/h with no traffic, so a
    # long drive can look short while a bus takes much longer. Keep a driving
    # result only when the place is also within 4.5 km, where a direct bus
    # from the TAU area is still plausibly inside the cap.
    if (
        straight_km is not None
        and straight_km <= 4.5
        and drive_min is not None
        and drive_min <= 15
    ):
        drive_bit = f", driving {round(drive_min)} min (OSRM, free-flow)" if drive_min is not None else ""
        walk_bit = f", walking {round(walk_min)} min ({walk_source})" if walk_min is not None else ""
        sort_value = drive_min if drive_min is not None else straight_km / 4.5 * max_minutes
        return (
            True,
            (
                f"straight-line {straight_km:.1f} km{drive_bit}{walk_bit}; "
                f"transit not routed; kept as plausibly ≤{max_minutes} min transit"
            ),
            sort_value,
        )
    bits = []
    if walk_min is not None:
        bits.append(f"walking {round(walk_min)} min ({walk_source})")
    if drive_min is not None:
        bits.append(f"driving {round(drive_min)} min (OSRM)")
    if straight_km is not None:
        bits.append(f"straight-line {straight_km:.1f} km")
    detail = "; ".join(bits) if bits else "no coordinates"
    sort_value = walk_min
    if sort_value is None and drive_min is not None:
        sort_value = drive_min + 12
    if sort_value is None and straight_km is not None:
        sort_value = straight_km / 5 * max_minutes
    return False, detail, sort_value


TRAVEL_RULE = (
    "No public transit journey planner was available. Walking time is from the "
    "OpenStreetMap foot router (about 4.8 km/h). A listing is kept when that walk "
    "is within the cap, or when straight-line distance is ≤4.5 km and free-flow "
    "driving is ≤15 min, which is still a plausible bus trip from the TAU area. "
    "Free-flow driving alone is not used: that router treats an 11 km trip as "
    "about 15 minutes. The mode is named on each row."
)


class TravelClient:
    def __init__(self, pause: float = 1.05):
        self.pause = pause
        self._geo_cache: dict[str, tuple[float, float, str] | None] = {}
        self._route_cache: dict[tuple, tuple[float, float] | None] = {}
        self._last_nominatim = 0.0

    def geocode_campus(self, query: str) -> tuple[float, float, str]:
        hit = self.geocode(query, expect_tokens=("תל אביב", "Tel Aviv", "אוניברסיט"))
        if hit is None:
            return (*TAU_ANCHOR, "fallback coordinate for the TAU main campus; geocoder missed")
        lat, lon, label = hit
        if haversine_km(lat, lon, TAU_ANCHOR[0], TAU_ANCHOR[1]) > 1.5:
            return (
                *TAU_ANCHOR,
                f"geocoder returned {label} away from the main campus; using the Ramat Aviv anchor",
            )
        return lat, lon, label

    def geocode(self, query: str, expect_tokens: tuple[str, ...] = ()) -> tuple[float, float, str] | None:
        key = query.strip().lower()
        if key in self._geo_cache:
            return self._geo_cache[key]
        wait = self.pause - (time.monotonic() - self._last_nominatim)
        if self._last_nominatim and wait > 0:
            time.sleep(wait)
        url = NOMINATIM + "?" + urllib.parse.urlencode(
            {"format": "jsonv2", "limit": "5", "q": query}
        )
        self._last_nominatim = time.monotonic()
        request = urllib.request.Request(
            url,
            headers={"User-Agent": NOMINATIM_UA, "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            self._geo_cache[key] = None
            return None
        chosen = None
        for item in payload:
            display = item.get("display_name", "")
            if expect_tokens and not _tokens_match(display, expect_tokens):
                continue
            try:
                chosen = (float(item["lat"]), float(item["lon"]), display)
            except (KeyError, TypeError, ValueError):
                continue
            break
        self._geo_cache[key] = chosen
        return chosen

    def route_leg(
        self, profile: str, origin: tuple[float, float], dest: tuple[float, float]
    ) -> tuple[float, float] | None:
        """Return (minutes, kilometers) for a foot or driving route."""
        key = (profile, round(origin[0], 5), round(origin[1], 5), round(dest[0], 5), round(dest[1], 5))
        if key in self._route_cache:
            return self._route_cache[key]
        base = FOOT_ROUTER if profile == "foot" else DRIVE_ROUTER
        # OSRM expects lon,lat.
        path = f"{origin[1]},{origin[0]};{dest[1]},{dest[0]}"
        url = f"{base}/{profile}/{path}?overview=false"
        try:
            body, _final = fetch(url, timeout=20, user_agent=BROWSER_UA)
            payload = json.loads(body)
            route = payload["routes"][0]
            minutes = float(route["duration"]) / 60.0
            kilometers = float(route["distance"]) / 1000.0
            leg = (minutes, kilometers)
        except (FetchError, json.JSONDecodeError, KeyError, IndexError, TypeError, ValueError):
            leg = None
        self._route_cache[key] = leg
        return leg
