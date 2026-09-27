"""Command-line search."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from apartment_finder.models import Listing, SearchResult
from apartment_finder.parse import dedupe_key, freshness
from apartment_finder.report import render
from apartment_finder.sources import Collector
from apartment_finder.travel import TRAVEL_RULE, TravelClient, assess_travel, haversine_km


def _richer(candidate: Listing, current: Listing) -> bool:
    return (
        bool(candidate.date_text),
        bool(candidate.extras),
        len(candidate.street),
    ) > (
        bool(current.date_text),
        bool(current.extras),
        len(current.street),
    )


def dedupe(listings: list[Listing]) -> list[Listing]:
    chosen: dict[tuple, Listing] = {}
    for listing in listings:
        key = dedupe_key(listing)
        previous = chosen.get(key)
        if previous is None or _richer(listing, previous):
            chosen[key] = listing
    return list(chosen.values())


def _expect_tokens(city: str) -> tuple[str, ...]:
    tokens = [city] if city else []
    if "תל אביב" in city or city.startswith("תל"):
        tokens.append("תל אביב")
        tokens.append("Tel Aviv")
    if "רמת גן" in city:
        tokens.append("רמת גן")
        tokens.append("Ramat Gan")
    if "גבעתיים" in city:
        tokens.append("Givatayim")
    if "הרצליה" in city:
        tokens.append("Herzliya")
    if "רמת השרון" in city:
        tokens.append("Ramat HaSharon")
    if "בני ברק" in city:
        tokens.append("Bnei Brak")
    return tuple(dict.fromkeys(token for token in tokens if token))


def geocode_listing(listing: Listing, client: TravelClient) -> tuple[tuple[float, float, str] | None, str]:
    city = listing.city
    tokens = _expect_tokens(city)
    queries: list[tuple[str, str]] = []
    if listing.street and city:
        if listing.neighborhood:
            queries.append((f"{listing.street}, {listing.neighborhood}, {city}", "street"))
        queries.append((f"{listing.street}, {city}", "street"))
    if listing.neighborhood and city:
        queries.append((f"{listing.neighborhood}, {city}", "neighborhood"))
    seen: set[str] = set()
    for query, level in queries:
        if query in seen:
            continue
        seen.add(query)
        hit = client.geocode(query, expect_tokens=tokens)
        if hit:
            note = ""
            if level == "neighborhood":
                note = "Placed at the neighborhood (the street geocode missed)."
            return hit, note
    return None, ""


def apply_travel(
    listings: list[Listing],
    client: TravelClient,
    campus: tuple[float, float],
    max_minutes: int,
    now: datetime,
) -> None:
    for listing in listings:
        listing.current = freshness(listing.date_text, now)
        hit, precision = geocode_listing(listing, client)
        if hit is None:
            listing.included = False
            listing.exclude_reason = "could not geocode inside the stated city"
            listing.travel_text = "not measured"
            continue
        lat, lon, _label = hit
        listing.latitude = lat
        listing.longitude = lon
        km = haversine_km(campus[0], campus[1], lat, lon)
        walk_leg = client.route_leg("foot", campus, (lat, lon))
        walk_source = "OSM foot router"
        if walk_leg is None:
            walk = km * 1.35 / 4.8 * 60
            walk_source = "straight-line estimate at 4.8 km/h"
        else:
            walk, walked_km = walk_leg
            if walk > 0 and (walked_km / (walk / 60.0)) > 8:
                walk = walked_km / 4.8 * 60
                walk_source = "road distance at 4.8 km/h (router duration was not a walking speed)"
        drive = None
        keep, text, minutes = assess_travel(walk, None, km, max_minutes, walk_source)
        if not keep:
            drive_leg = client.route_leg("driving", campus, (lat, lon))
            drive = drive_leg[0] if drive_leg else None
            keep, text, minutes = assess_travel(walk, drive, km, max_minutes, walk_source)
        if precision:
            text = f"{precision} {text}"
        listing.travel_text = text
        listing.travel_minutes = minutes
        if not listing.current:
            listing.included = False
            listing.exclude_reason = "listing date older than 180 days"
            continue
        listing.included = keep
        listing.exclude_reason = "" if keep else "outside the travel window"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Find rental listings near a campus from public Israeli boards."
    )
    parser.add_argument("--min-rent", type=int, default=2300, help="Minimum monthly rent in ILS")
    parser.add_argument("--max-rent", type=int, default=2600, help="Maximum monthly rent in ILS")
    parser.add_argument(
        "--campus",
        default="אוניברסיטת תל אביב, רמת אביב",
        help="Campus name passed to the geocoder",
    )
    parser.add_argument("--max-minutes", type=int, default=30, help="Travel cap in minutes")
    parser.add_argument("--output", required=True, help="Markdown file to write")
    parser.add_argument("--pause", type=float, default=0.35, help="Seconds between listing requests")
    parser.add_argument("--max-pages", type=int, default=6, help="Pages per city or filter")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.min_rent > args.max_rent:
        print("min rent is above max rent", file=sys.stderr)
        return 2
    if args.max_minutes < 1:
        print("max minutes must be positive", file=sys.stderr)
        return 2

    now = datetime.now(timezone.utc)
    print("Searching Komo and ad.co.il, then probing the other boards...", file=sys.stderr)
    collector = Collector(args.min_rent, args.max_rent, pause=args.pause, max_pages=args.max_pages)
    collector.run()
    raw_count = len(collector.listings)
    listings = dedupe(collector.listings)
    print(
        f"Fetched {raw_count} priced rows, {len(listings)} after dedupe. Measuring travel...",
        file=sys.stderr,
    )

    client = TravelClient()
    campus_lat, campus_lon, campus_note = client.geocode_campus(args.campus)
    apply_travel(listings, client, (campus_lat, campus_lon), args.max_minutes, now)

    result = SearchResult(
        listings=listings,
        sources=collector.statuses,
        campus_label=args.campus,
        campus_lat=campus_lat,
        campus_lon=campus_lon,
        campus_note=campus_note,
        travel_rule=TRAVEL_RULE,
    )
    text = render(result, now, args.min_rent, args.max_rent, args.max_minutes)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    kept = sum(1 for row in listings if row.included)
    print(f"Wrote {kept} candidates to {output}", file=sys.stderr)
    return 0
