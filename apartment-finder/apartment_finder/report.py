"""Markdown report for one search run."""

from __future__ import annotations

from datetime import datetime

from apartment_finder.models import Listing, SearchResult


def _ils(amount: int) -> str:
    return f"{amount:,} ₪"


def _block(listing: Listing, index: int | None = None) -> str:
    title = listing.place or listing.url
    heading = f"### {index}. {title}" if index else f"### {title}"
    lines = [
        heading,
        "",
        f"- Price: {_ils(listing.price_ils)}",
        f"- Type: {listing.type_label}",
        f"- Place: {listing.place or 'not stated'}",
        f"- Travel: {listing.travel_text or 'not measured'}",
        f"- Source: {listing.source}",
        f"- URL: {listing.url}",
        f"- Listed: {listing.date_text or 'date not shown on the listing'}",
    ]
    if listing.extras:
        lines.append(f"- Extras stated on the listing: {listing.extras}")
    if listing.exclude_reason:
        lines.append(f"- Not counted because: {listing.exclude_reason}")
    return "\n".join(lines)


def _section(title: str, rows: list[Listing], numbered: bool, limit: int | None = None) -> str:
    shown = rows if limit is None else rows[:limit]
    extra = ""
    if limit is not None and len(rows) > limit:
        extra = f"\n\n{len(rows) - limit} more not shown."
    if not shown:
        body = "_None._"
    elif numbered:
        body = "\n\n".join(_block(row, i) for i, row in enumerate(shown, start=1))
    else:
        body = "\n\n".join(_block(row) for row in shown)
    return f"## {title}\n\n{body}{extra}\n"


def render(result: SearchResult, when: datetime, min_rent: int, max_rent: int, max_minutes: int) -> str:
    tried = ", ".join(status.name for status in result.sources) or "none"
    failed = [status for status in result.sources if not status.ok]
    worked = [status for status in result.sources if status.ok]
    failed_lines = (
        "\n".join(f"- {status.name}: {status.detail}" for status in failed) if failed else "- none"
    )
    worked_lines = (
        "\n".join(f"- {status.name}: {status.detail}" for status in worked) if worked else "- none"
    )
    candidates = [row for row in result.listings if row.included]
    outside = [row for row in result.listings if row.exclude_reason == "outside the travel window"]
    stale = [row for row in result.listings if row.exclude_reason.startswith("listing date")]
    unplaced = [row for row in result.listings if row.exclude_reason.startswith("could not geocode")]
    candidates.sort(key=lambda row: (row.travel_minutes if row.travel_minutes is not None else 10**6, row.price_ils))
    outside.sort(key=lambda row: (row.travel_minutes if row.travel_minutes is not None else 10**6, row.price_ils))

    campus = result.campus_label or "unknown"
    if result.campus_lat is not None and result.campus_lon is not None:
        campus += f" ({result.campus_lat:.5f}, {result.campus_lon:.5f})"

    header = "\n".join(
        [
            "# Rental candidates near TAU",
            "",
            f"Searched at: {when.isoformat()}",
            "",
            f"- Monthly listed rent: {min_rent}–{max_rent} ₪ (rooms in shared apartments and whole apartments/studios).",
            f"- Campus: {campus}",
            f"- Campus note: {result.campus_note or 'n/a'}",
            f"- Max travel: {max_minutes} minutes",
            f"- Travel rule: {result.travel_rule}",
            f"- Sources tried: {tried}",
            f"- Candidates: {len(candidates)}",
            "",
            "Sources that returned listings:",
            "",
            worked_lines,
            "",
            "Sources that failed:",
            "",
            failed_lines,
            "",
            "Vaad and arnona are copied only when the listing states them. A missing extra is not a reason to drop the row.",
            "These are advertisements, not confirmed vacancies. Contact the advertiser before making plans.",
            "",
            "",
        ]
    )
    return (
        header
        + _section("Candidates", candidates, numbered=True)
        + "\n"
        + _section("Price matches outside the travel window", outside, numbered=False, limit=20)
        + "\n"
        + _section("On the board, but the listing date is older than 180 days", stale, numbered=False, limit=15)
        + "\n"
        + _section("Price matches that could not be placed on the map", unplaced, numbered=False, limit=15)
    )
