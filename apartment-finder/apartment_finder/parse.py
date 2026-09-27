"""HTML parsers and small text helpers. No network."""

from __future__ import annotations

import html
import re
from datetime import datetime, timezone

from apartment_finder.models import Listing

_PHONE = re.compile(
    r"(?:\+?972[-\s]?|0)(?:5\d|[23489])[-\s]?\d{3}[-\s]?\d{4}"
)


def unescape(text: str) -> str:
    return html.unescape(text or "").replace("\xa0", " ").replace("&nbsp;", " ")


def parse_ils(text: str) -> int | None:
    cleaned = unescape(text)
    match = re.search(r"(\d[\d,]*)", cleaned)
    if not match:
        return None
    digits = match.group(1).replace(",", "")
    if not digits.isdigit():
        return None
    return int(digits)


def strip_phones(text: str) -> str:
    return _PHONE.sub("[phone omitted]", text)


def collapse(text: str) -> str:
    return re.sub(r"\s+", " ", unescape(text)).strip()


def extras_from(*chunks: str) -> str:
    text = "\n".join(unescape(c) for c in chunks if c)
    text = re.sub(r"<[^>]+>", " ", text)
    lines = []
    for raw in re.split(r"[\n\r]+", text):
        line = collapse(raw)
        if not line:
            continue
        if any(word in line for word in ("ארנונה", "ועד", "חשמל", "מים", "כולל", "ש\"ח", "₪")):
            lines.append(line)
    seen = []
    for line in lines:
        if line not in seen:
            seen.append(line)
    blob = strip_phones(" | ".join(seen))
    return blob[:420]


def looks_like_short_stay(text: str) -> bool:
    """True when the ad is priced per night or Shabbat rather than per month."""
    blob = unescape(text)
    if any(token in blob for token in ("לחודש", "שכ\"ד", "שכר דירה", "שכירות")):
        return False
    return any(token in blob for token in ("ללילה", "לשבת", "לסופ\"ש", "ליום"))


def classify(text: str, source: str) -> str:
    blob = unescape(text)
    if "שותפ" in blob or "חדר" in blob or "partner" in source:
        if "יחידת דיור" in blob or "סטודיו" in blob:
            return "יחידת דיור / סטודיו"
        return "חדר בדירת שותפים"
    if "סטודיו" in blob or "יחידת דיור" in blob:
        return "יחידת דיור / סטודיו"
    if "דירה" in blob:
        return "דירה"
    return "השכרה"


def freshness(date_text: str, now: datetime, max_age_days: int = 180) -> bool:
    """A listing is current when its newest stated date is inside the window.

    Missing or unrecognized dates stay in the candidate pool: the live board
    is still showing them, and the report says the date was not published.
    """
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    text = collapse(date_text)
    if not text:
        return True
    relative = re.search(
        r"(\d+)\s*(שעה|שעות|יום|ימים|שבוע|שבועות|חודש|חודשים|שנה|שנים)",
        text,
    )
    if relative:
        amount = int(relative.group(1))
        unit = relative.group(2)
        days = {
            "שעה": amount / 24,
            "שעות": amount / 24,
            "יום": amount,
            "ימים": amount,
            "שבוע": amount * 7,
            "שבועות": amount * 7,
            "חודש": amount * 30,
            "חודשים": amount * 30,
            "שנה": amount * 365,
            "שנים": amount * 365,
        }[unit]
        return days <= max_age_days
    parsed: list[datetime] = []
    for day, month, year in re.findall(r"(\d{1,2})/(\d{1,2})/(\d{4})", text):
        try:
            parsed.append(datetime(int(year), int(month), int(day), tzinfo=timezone.utc))
        except ValueError:
            continue
    if not parsed:
        return True
    latest = max(parsed)
    return (now - latest).days <= max_age_days


def dedupe_key(listing: Listing) -> tuple:
    def norm(value: str) -> str:
        value = value.replace("־", " ").replace("-", " ")
        value = re.sub(r"[\"'׳״]", "", value)
        value = re.sub(r"\s+", " ", value).strip().lower()
        return value

    street = norm(listing.street)
    hood = norm(listing.neighborhood)
    if street:
        return ("addr", listing.price_ils, street, hood)
    return ("url", listing.url.split("?")[0].rstrip("/"), listing.price_ils)


def split_komo_title(title: str) -> tuple[str, str, str]:
    parts = [collapse(p) for p in unescape(title).split(",") if collapse(p)]
    if len(parts) >= 3:
        return parts[0], parts[1], ", ".join(parts[2:])
    if len(parts) == 2:
        return parts[0], "", parts[1]
    if parts:
        return parts[0], "", ""
    return "", "", ""


def parse_komo_list(html_text: str, source: str = "Komo") -> list[Listing]:
    listings: list[Listing] = []
    parts = re.split(r'id="modaa(?:RowDv|PPC)(\d+)"', html_text)
    for index in range(1, len(parts), 2):
        ad_id = parts[index]
        chunk = parts[index + 1]
        # Stop at the next card if the split did not.
        chunk = chunk.split('id="modaa', 1)[0]
        title_match = re.search(r'class="title">([^<]+)', chunk)
        price_match = re.search(r'class="price">([^<]+)', chunk)
        if not title_match or not price_match:
            continue
        price = parse_ils(price_match.group(1))
        if price is None:
            continue
        desc_match = re.search(r'class="description">([\s\S]*?)</div>', chunk)
        description = desc_match.group(1) if desc_match else ""
        rooms_match = re.search(r"(\d+(?:\.\d+)?)\s*חדרים", unescape(description))
        city, neighborhood, street = split_komo_title(title_match.group(1))
        listings.append(
            Listing(
                source=source,
                url=f"https://www.komo.co.il/code/nadlan/details/?modaaNum={ad_id}",
                price_ils=price,
                city=city,
                neighborhood=neighborhood,
                street=street,
                rooms=rooms_match.group(1) if rooms_match else "",
                kind=classify(description + " " + title_match.group(1), source),
            )
        )
    return listings


def _first_info(html_text: str, title_prefix: str) -> re.Match[str] | None:
    return re.search(
        rf'class="firstInfo"\s*>\s*([^<]+?)\s*</div>\s*<div class="firstInfoTitle"\s*>\s*{title_prefix}',
        html_text,
    )


def parse_komo_detail(html_text: str) -> dict[str, str]:
    update = re.search(r'class="m_updateDate[^"]*"[^>]*>([^<]+)', html_text)
    teur = re.search(r'id="teurWrap">([\s\S]*?)</div>', html_text)
    furniture = re.search(r'class="furnitureDesc">([\s\S]*?)</div>', html_text)
    rooms = _first_info(html_text, "חד")
    sqm = _first_info(html_text, "מ")
    description = unescape(teur.group(1)) if teur else ""
    furn = unescape(furniture.group(1)) if furniture else ""
    return {
        "date_text": collapse(update.group(1)) if update else "",
        "rooms": collapse(rooms.group(1)) if rooms else "",
        "sqm": collapse(sqm.group(1)) if sqm else "",
        "description": collapse(description),
        "furniture": collapse(furn),
        "extras": extras_from(description, furn),
        "blob": description + "\n" + furn,
    }


def split_ad_title(title: str) -> tuple[str, str]:
    title = collapse(title)
    cities = (
        "תל אביב יפו",
        "תל אביב",
        "רמת גן",
        "גבעתיים",
        "הרצליה",
        "רמת השרון",
        "בני ברק",
        "גבעת שמואל",
        "חולון",
        "בת ים",
        "פתח תקווה",
        "רמת גן - גבעתיים",
    )
    for city in cities:
        if title.startswith(city):
            return city, title[len(city) :].strip(" -")
    return title, ""


def parse_ad_list(html_text: str, source: str) -> list[Listing]:
    listings: list[Listing] = []
    parts = re.split(r'<div class="card-block" data-id="(\d+)"', html_text)
    for index in range(1, len(parts), 2):
        ad_id = parts[index]
        chunk = parts[index + 1]
        if chunk.lstrip().startswith("footer") or "footer-cards" in chunk[:80]:
            continue
        chunk = chunk.split('<div class="card-block"', 1)[0]
        title_match = re.search(r'class="card-title[^"]*">([^<]+)', chunk)
        price_match = re.search(r'class="price[^"]*">\s*([^<]+)', chunk)
        if not title_match or not price_match:
            continue
        price = parse_ils(price_match.group(1))
        if price is None:
            continue
        street_match = re.search(r'class="card-text[^"]*">([^<]+)', chunk)
        rooms_match = re.search(
            r'fa-bed[\s\S]{0,180}?class="ms-1">\s*(\d+(?:\.\d+)?)',
            chunk,
        )
        desc_match = re.search(r'class="card-description[\s\S]*?<p[^>]*>([\s\S]*?)</p>', chunk)
        description = desc_match.group(1) if desc_match else ""
        city, neighborhood = split_ad_title(unescape(title_match.group(1)))
        street = collapse(street_match.group(1)) if street_match else ""
        listings.append(
            Listing(
                source=source,
                url=f"https://www.ad.co.il/ad/{ad_id}",
                price_ils=price,
                city=city,
                neighborhood=neighborhood,
                street=street,
                rooms=rooms_match.group(1) if rooms_match else "",
                kind=classify(unescape(title_match.group(1)) + " " + description, source),
                extras=extras_from(description),
            )
        )
    return listings


def parse_ad_detail(html_text: str) -> dict[str, str]:
    text = re.sub(r"<script[\s\S]*?</script>", " ", html_text, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = unescape(re.sub(r"<[^>]+>", "\n", text))
    lines = [collapse(line) for line in text.splitlines()]
    lines = [line for line in lines if line]
    blob = "\n".join(lines)
    created = re.search(r"תאריך יצירה:\s*([0-9/]+)", blob)
    bumped = re.search(r"תאריך הקפצה אחרון:\s*([0-9/]+)", blob)
    updated = re.search(r"תאריך עדכון:\s*([0-9/]+)", blob)
    bits = []
    if created:
        bits.append(f"נוצר {created.group(1)}")
    if bumped:
        bits.append(f"הוקפץ {bumped.group(1)}")
    if updated:
        bits.append(f"עודכן {updated.group(1)}")
    # The description sits just before furniture / contact on partner ads.
    description = ""
    for line in lines:
        if len(line) < 40 or line.startswith("תאריך"):
            continue
        if any(word in line for word in ("ארנונה", "ועד", "חדר", "לחודש", "שותפ")):
            description = line
            break
    return {
        "date_text": "; ".join(bits),
        "description": description,
        "extras": extras_from(description),
        "blob": blob,
    }


def ad_price_param(html_text: str) -> str | None:
    for match in re.finditer(
        r'nav-link-text">([^<]+)</span>[\s\S]{0,500}?id="filter-(rp\d+)"',
        html_text,
    ):
        if collapse(match.group(1)) == "מחיר":
            return match.group(2)
    return None


def ad_result_count(html_text: str) -> int | None:
    match = re.search(r"<h5[^>]*>\s*(\d+)\s+מודעות\s*</h5>", html_text)
    if not match:
        return None
    return int(match.group(1))


def ad_city_filters(html_text: str) -> list[tuple[str, str, str]]:
    found: list[tuple[str, str, str]] = []
    for match in re.finditer(
        r'data-spid="(sp\d+)"\s+data-optid="(\d+)"[\s\S]{0,350}?<label[^>]*>([^<]+)</label>',
        html_text,
    ):
        found.append((match.group(1), match.group(2), collapse(match.group(3))))
    return found


CITY_TARGETS = (
    "תל אביב",
    "רמת גן",
    "גבעתיים",
    "הרצליה",
    "רמת השרון",
    "בני ברק",
    "גבעת שמואל",
)


def city_filter_wanted(label: str) -> bool:
    name = collapse(label)
    allowed_rest = {"", "יפו", "והסביבה", "גבעתיים", "הרצליה"}
    pieces = [collapse(part) for part in re.split(r"\s+-\s+", name)]
    if len(pieces) > 1:
        return all(city_filter_wanted(part) for part in pieces)
    for target in CITY_TARGETS:
        if name == target:
            return True
        if name.startswith(target + " ") or name.startswith(target + "-"):
            rest = name[len(target) :].strip(" -")
            if rest in allowed_rest:
                return True
    return False
