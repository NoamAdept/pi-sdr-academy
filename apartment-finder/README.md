# Apartment finder

Searches public Israeli rental boards for rooms and whole apartments near a campus, then keeps listings whose listed monthly rent is inside a budget and whose trip to campus is inside a time cap.

Defaults match a student at Tel Aviv University (רמת אביב):

- rent 2300–2600 ₪
- campus `אוניברסיטת תל אביב, רמת אביב`
- 30 minutes

The tool does not log in, pay, or solve bot checks. If a site returns a block page, that source is recorded as failed and the search continues.

## Run

From this directory, with system `python3` (no extra packages):

```bash
python3 finder.py \
  --min-rent 2300 \
  --max-rent 2600 \
  --campus "אוניברסיטת תל אביב, רמת אביב" \
  --max-minutes 30 \
  --output /cursor/stores/self/docs/apartment-candidates.md
```

The latest candidate list from the run that shipped with this tool is that markdown file (outside this git repo, in the project notes). Rerunning overwrites it if you pass the same path.

## What it queries

- Komo apartment rentals (`apartments-for-rent`) for Tel Aviv-Yafo, Ramat Gan, Givatayim, Ramat HaSharon, Herzliya, Bnei Brak, and Givat Shmuel, with the price range in the query.
- ad.co.il roommate, rental, and student boards, using each page's own city and price filters.
- A single public request each to Yad2, Madlan, Homeless, WinWin, and OnMap. Those often answer with a block page, a redirect, or a client-rendered shell. Nothing is invented to fill the gap.

Travel uses OpenStreetMap Nominatim for the address and OSRM for walking, then driving if the walk is over the cap. There is no live transit itinerary; the report names the mode. See the travel rule printed at the top of the output.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Run that from this directory.
