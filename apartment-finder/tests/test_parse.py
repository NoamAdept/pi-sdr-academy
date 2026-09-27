import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apartment_finder.models import Listing
from apartment_finder.parse import (
    city_filter_wanted,
    dedupe_key,
    freshness,
    looks_like_short_stay,
    parse_ad_list,
    parse_homeless_board,
    parse_ils,
    parse_komo_detail,
    parse_komo_list,
)
from apartment_finder.run import dedupe
from apartment_finder.travel import assess_travel


KOMO_CARD = """
<div id="modaaRowDv4924301" class="modaaRowAd">
  <a href="/code/nadlan/details/?modaaNum=4924301">
    <h2 class="title">תל אביב יפו, נווה אביבים, אינשטיין 27</h2>
  </a>
  <div class="price">2,575&nbsp;&#8362;</div>
  <div class="description">דירה&nbsp;4.0 חדרים (90 מ"ר)</div>
</div>
"""

KOMO_DETAIL = """
<div class="m_updateDate md_c_183 ">עודכן לפני: 11 שעות  </div>
<div class="firstInfo" > 4.0 </div>
<div class="firstInfoTitle" > חד'</div>
<div id="teurWrap">תשלום קבוע של 200 ש"ח - ארנונה, אינטרנט וכבלים.</div>
<div class="furnitureDesc">מתפנים 2 חדרים בדירת 4 שותפות</div>
"""

AD_CARD = """
<div class="card-block" data-id="14599093" onclick="clickad(14599093)">
  <a href="/ad/14599093"><h2 class="card-title mb-1">תל אביב יפו רמת אביב ג</h2></a>
  <p class="card-text my-1 mb-1 mt-0">ברזאני 7</p>
  <div class="card-description mb-lg-2"><p class="mb-0">המחיר כולל ועד בית.</p></div>
  <i class="fa gray fa-bed"></i>
  <span class="ms-1">4<span class="d-none">&nbsp;חד'</span></span>
  <div class="price ms-1">2,600 ₪</div>
</div>
<div class="card-block footer-cards" onclick="clickad(1, true)">
  <h2 class="card-title mb-1">ignore me</h2>
  <div class="price text-start">1,200 ₪</div>
</div>
"""


HOMELESS_CARD = """
<img src="https://uploads.homeless.co.il/mate/202608/300/nvFile.jpg">
<a title="דירה לשותפים 1 חדרים בהצפון הישן תל אביב יפו, יהושע בן נון, 2500 שח תל-אביב צפון" href="/mate/viewad,240787.aspx"></a>
"""


class ParseTests(unittest.TestCase):
    def test_homeless_card(self):
        rows = parse_homeless_board(HOMELESS_CARD, "Homeless שותפים", "תל אביב יפו")
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row.price_ils, 2500)
        self.assertEqual(row.street, "יהושע בן נון")
        self.assertEqual(row.neighborhood, "הצפון הישן")
        self.assertIn("2026-08", row.date_text)
        self.assertIn("240787", row.url)
    def test_parse_ils(self):
        self.assertEqual(parse_ils("2,575 ₪"), 2575)
        self.assertIsNone(parse_ils("אין מחיר"))

    def test_komo_card(self):
        rows = parse_komo_list(KOMO_CARD)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row.price_ils, 2575)
        self.assertEqual(row.neighborhood, "נווה אביבים")
        self.assertEqual(row.street, "אינשטיין 27")
        self.assertEqual(row.rooms, "4.0")
        self.assertIn("4924301", row.url)

    def test_komo_detail(self):
        detail = parse_komo_detail(KOMO_DETAIL)
        self.assertIn("11 שעות", detail["date_text"])
        self.assertEqual(detail["rooms"], "4.0")
        self.assertIn("ארנונה", detail["extras"])

    def test_ad_card_skips_footer(self):
        rows = parse_ad_list(AD_CARD, "ad.co.il שותפים")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].price_ils, 2600)
        self.assertEqual(rows[0].street, "ברזאני 7")
        self.assertEqual(rows[0].neighborhood, "רמת אביב ג")
        self.assertEqual(rows[0].rooms, "4")
        self.assertIn("ועד", rows[0].extras)

    def test_freshness(self):
        now = datetime(2026, 9, 27, tzinfo=timezone.utc)
        self.assertTrue(freshness("עודכן לפני: 11 שעות", now))
        self.assertFalse(freshness("נוצר 13/10/2022; הוקפץ 13/10/2022", now))
        self.assertTrue(freshness("נוצר 01/08/2026", now))
        self.assertTrue(freshness("", now))

    def test_short_stay(self):
        self.assertTrue(looks_like_short_stay("מחיר ללילה 400"))
        self.assertFalse(looks_like_short_stay("2,500 לחודש כולל ארנונה"))

    def test_city_filter(self):
        self.assertTrue(city_filter_wanted("תל אביב יפו"))
        self.assertTrue(city_filter_wanted("רמת גן - גבעתיים"))
        self.assertFalse(city_filter_wanted("רמת גן מרכז העיר ב'"))
        self.assertFalse(city_filter_wanted("חיפה וחוף הכרמל"))

    def test_dedupe_merges_abbreviated_street(self):
        komo = Listing("Komo", "https://komo.example/1", 2450, "רמת גן", "נחלת גנים", 'רש"י 23')
        homeless = Listing("Homeless", "https://homeless.example/2", 2450, "רמת גן", "נחלת גנים", "רשי")
        other = Listing("Komo", "https://komo.example/3", 2300, "רמת גן", "גפן", "ביאליק 86")
        rows = dedupe([homeless, komo, other])
        self.assertEqual(len(rows), 2)
        kept = [row for row in rows if row.price_ils == 2450][0]
        self.assertIn("23", kept.street)

    def test_dedupe_key_ignores_quotes(self):
        a = Listing("Komo", "https://example/a", 2500, "תל אביב יפו", "נווה אביבים", "אינשטיין 27")
        b = Listing("ad", "https://example/b", 2500, "תל אביב יפו", "נווה אביבים", "אינשטיין  27")
        self.assertEqual(dedupe_key(a), dedupe_key(b))

    def test_travel_rules(self):
        keep, label, _minutes = assess_travel(18, None, 1.2, 30)
        self.assertTrue(keep)
        self.assertIn("walking", label)
        keep, label, _minutes = assess_travel(57, 8, 3.0, 30)
        self.assertTrue(keep)
        self.assertIn("straight-line", label)
        keep, _label, _minutes = assess_travel(126, 14.5, 7.9, 30)
        self.assertFalse(keep)
        keep, _label, _minutes = assess_travel(40, None, 3.0, 30)
        self.assertFalse(keep)
        keep, _label, _minutes = assess_travel(50, 28, 4.2, 30)
        self.assertFalse(keep)


if __name__ == "__main__":
    unittest.main()
