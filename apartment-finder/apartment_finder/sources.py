"""Listing sources. Each adapter records a failure and continues."""

from __future__ import annotations

import re
import time
import urllib.parse

from apartment_finder.http_client import FetchError, fetch
from apartment_finder.models import Listing, SourceStatus
from apartment_finder.parse import (
    ad_city_filters,
    ad_price_param,
    ad_result_count,
    city_filter_wanted,
    classify,
    extras_from,
    looks_like_short_stay,
    parse_ad_detail,
    parse_ad_list,
    parse_homeless_board,
    parse_komo_detail,
    parse_komo_list,
    price_buckets,
)

KOMO_CITIES = (
    "תל אביב יפו",
    "רמת גן",
    "גבעתיים",
    "רמת השרון",
    "הרצליה",
    "בני ברק",
    "גבעת שמואל",
)

AD_CATEGORIES = (
    ("ad.co.il שותפים", "https://www.ad.co.il/nadlanpartner"),
    ("ad.co.il השכרה", "https://www.ad.co.il/nadlanrent"),
    ("ad.co.il סטודנטים", "https://www.ad.co.il/nadlanstudent"),
)

HOMELESS_CITIES = (
    "תל אביב",
    "רמת גן",
    "גבעתיים",
    "הרצליה",
    "רמת השרון",
    "בני ברק",
    "גבעת שמואל",
)

PROBES = (
    ("Yad2", "https://www.yad2.co.il/realestate/rent"),
    ("Madlan", "https://www.madlan.co.il/"),
    ("WinWin", "https://www.winwin.co.il/"),
    ("OnMap", "https://www.onmap.co.il/"),
)


def _pause(seconds: float) -> None:
    if seconds > 0:
        time.sleep(seconds)


class Collector:
    def __init__(self, min_rent: int, max_rent: int, pause: float = 0.35, max_pages: int = 6):
        self.min_rent = min_rent
        self.max_rent = max_rent
        self.pause = pause
        self.max_pages = max_pages
        self.statuses: list[SourceStatus] = []
        self.listings: list[Listing] = []

    def _in_budget(self, price: int) -> bool:
        return self.min_rent <= price <= self.max_rent

    def run(self) -> None:
        self._komo()
        self._ad()
        self._homeless()
        self._probes()

    def _komo(self) -> None:
        found = 0
        errors: list[str] = []
        for city in KOMO_CITIES:
            try:
                batch = self._komo_city(city)
            except FetchError as exc:
                errors.append(f"{city}: {exc}")
                continue
            found += len(batch)
            self.listings.extend(batch)
            _pause(self.pause)
        detail = f"{found} listings in {self.min_rent}–{self.max_rent} ₪ before the travel filter"
        if errors:
            detail += "; partial errors: " + "; ".join(errors[:4])
        failed = bool(errors) and found == 0 and len(errors) >= len(KOMO_CITIES)
        self.statuses.append(SourceStatus("Komo", not failed, detail if not failed else "; ".join(errors[:6])))

    def _komo_city(self, city: str) -> list[Listing]:
        collected: list[Listing] = []
        seen: set[str] = set()
        for page in range(1, self.max_pages + 1):
            params = {
                "nehes": "1",
                "cityName": city,
                "fromPrice": str(self.min_rent),
                "toPrice": str(self.max_rent),
            }
            if page > 1:
                params["currPage"] = str(page)
            url = "https://www.komo.co.il/code/nadlan/apartments-for-rent.asp?" + urllib.parse.urlencode(params)
            body, _final = fetch(url)
            rows = [row for row in parse_komo_list(body) if self._in_budget(row.price_ils)]
            fresh = [row for row in rows if row.url not in seen]
            if not fresh:
                break
            for row in fresh:
                seen.add(row.url)
                self._enrich_komo(row)
                if looks_like_short_stay(row.extras):
                    continue
                collected.append(row)
                _pause(self.pause)
            if len(rows) < 10:
                break
            _pause(self.pause)
        return collected

    def _enrich_komo(self, listing: Listing) -> None:
        try:
            body, _final = fetch(listing.url)
        except FetchError:
            return
        detail = parse_komo_detail(body)
        if detail["date_text"]:
            listing.date_text = detail["date_text"]
        if detail["rooms"]:
            listing.rooms = detail["rooms"]
        if detail["extras"]:
            listing.extras = detail["extras"]
        blob = " ".join(
            part
            for part in (detail["blob"], listing.neighborhood, listing.street, detail["description"])
            if part
        )
        listing.kind = classify(blob, listing.source)
        if detail["sqm"]:
            note = f"{detail['sqm']} מ״ר"
            if note not in listing.extras:
                listing.extras = (listing.extras + " | " + note).strip(" |")

    def _ad(self) -> None:
        for name, base in AD_CATEGORIES:
            try:
                count = self._ad_category(name, base)
            except FetchError as exc:
                self.statuses.append(SourceStatus(name, False, str(exc)))
                continue
            self.statuses.append(
                SourceStatus(
                    name,
                    True,
                    f"{count} listings in {self.min_rent}–{self.max_rent} ₪ before the travel filter",
                )
            )

    def _ad_category(self, name: str, base: str) -> int:
        body, _final = fetch(base + "?view=list")
        price_param = ad_price_param(body)
        if price_param:
            price_sets = [{price_param: f"{self.min_rent},{self.max_rent}"}]
        else:
            buckets = price_buckets(body, self.min_rent, self.max_rent)
            price_sets = [{"pricerange": bucket} for bucket in buckets]
        if not price_sets:
            raise FetchError("price filter not found on the search page", base)
        filters = [
            (spid, optid, label)
            for spid, optid, label in ad_city_filters(body)
            if city_filter_wanted(label)
        ]
        if not filters:
            raise FetchError("no Tel Aviv-area city filter found", base)
        seen: set[str] = set()
        added = 0
        for spid, optid, _label in filters:
            for price_query in price_sets:
                for page in range(1, self.max_pages + 1):
                    params = {"view": "list", spid: optid, **price_query}
                    if page > 1:
                        params["pageindex"] = str(page)
                    url = base + "?" + urllib.parse.urlencode(params)
                    page_body, _final = fetch(url)
                    rows = [
                        row
                        for row in parse_ad_list(page_body, name)
                        if self._in_budget(row.price_ils) and row.url not in seen
                    ]
                    if not rows:
                        break
                    for row in rows:
                        seen.add(row.url)
                        self._enrich_ad(row)
                        if looks_like_short_stay(" ".join((row.extras, row.kind))):
                            continue
                        self.listings.append(row)
                        added += 1
                        _pause(self.pause)
                    total = ad_result_count(page_body)
                    if total is not None and page * 20 >= total:
                        break
                    if len(rows) < 10:
                        break
                    _pause(self.pause)
                _pause(self.pause)
        return added

    def _enrich_ad(self, listing: Listing) -> None:
        try:
            body, _final = fetch(listing.url)
        except FetchError:
            return
        detail = parse_ad_detail(body)
        if detail["date_text"]:
            listing.date_text = detail["date_text"]
        if detail["extras"]:
            listing.extras = detail["extras"]
        elif detail["description"]:
            listing.extras = extras_from(detail["description"])
        blob = detail["blob"]
        listing.kind = classify(blob + " " + listing.neighborhood, listing.source)

    def _homeless(self) -> None:
        found = 0
        errors: list[str] = []
        for city in HOMELESS_CITIES:
            url = "https://www.homeless.co.il/mate/city=" + urllib.parse.quote(city)
            try:
                body, _final = fetch(url)
            except FetchError as exc:
                errors.append(f"{city}: {exc}")
                continue
            default_city = "תל אביב יפו" if city == "תל אביב" else city
            rows = [
                row
                for row in parse_homeless_board(body, "Homeless שותפים", default_city)
                if self._in_budget(row.price_ils)
            ]
            for row in rows:
                self._enrich_homeless(row)
                if looks_like_short_stay(row.extras):
                    continue
                self.listings.append(row)
                found += 1
                _pause(self.pause)
            _pause(self.pause)
        detail = (
            f"{found} roommate listings in {self.min_rent}–{self.max_rent} ₪ "
            "before the travel filter (דירות לשותפים). The general rent board was not paged; "
            "its price query does not stick."
        )
        if errors:
            detail += "; partial errors: " + "; ".join(errors[:4])
        failed = bool(errors) and found == 0 and len(errors) >= len(HOMELESS_CITIES)
        self.statuses.append(SourceStatus("Homeless", not failed, detail if not failed else "; ".join(errors[:6])))

    def _enrich_homeless(self, listing: Listing) -> None:
        try:
            body, _final = fetch(listing.url)
        except FetchError:
            return
        detail = parse_ad_detail(body)
        if detail["extras"]:
            listing.extras = detail["extras"]
        entry = re.search(r"כניסה:\s*([0-9./]+)", detail.get("blob", ""))
        if entry and entry.group(1) not in listing.extras:
            note = f"כניסה {entry.group(1)}"
            listing.extras = (listing.extras + " | " + note).strip(" |")

    def _probes(self) -> None:
        for name, url in PROBES:
            try:
                body, final = fetch(url, timeout=20)
            except FetchError as exc:
                self.statuses.append(SourceStatus(name, False, str(exc)))
                continue
            host = urllib.parse.urlparse(final).netloc.lower()
            if name == "WinWin" and "winwin" not in host:
                self.statuses.append(
                    SourceStatus(name, False, f"redirected to {final} and does not serve a rental search")
                )
                continue
            detail = "no listing parser; nothing extracted"
            if name == "OnMap":
                detail = "page is a client-rendered shell; no listing rows in the HTML"
            self.statuses.append(SourceStatus(name, False, detail))
