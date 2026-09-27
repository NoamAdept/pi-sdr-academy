# Apartment finder

Searches public Israeli rental boards for rooms and whole apartments near a campus, then keeps listings whose listed monthly rent is inside a budget and whose trip to campus is inside a time cap.

Defaults match a student at Tel Aviv University (רמת אביב) who bikes:

- rent 2300–2600 ₪
- campus `אוניברסיטת תל אביב, רמת אביב`
- 20 minutes by bike
- drop ads that say they are for women only (לגברים / mixed / unstated stay in)

The tool does not log in, pay, or solve bot checks. If a site returns a block page, that source is recorded as failed and the search continues.

## Run

From this directory, with system `python3` (no extra packages):

```bash
python3 finder.py \
  --min-rent 2300 \
  --max-rent 2600 \
  --campus "אוניברסיטת תל אביב, רמת אביב" \
  --mode bike \
  --max-minutes 20 \
  --gender men \
  --output /cursor/stores/self/docs/apartment-candidates.md
```

`--output` is the only required flag. The earlier transit search is still available with `--mode transit --max-minutes 30`.

The latest candidate list from the run that shipped with this tool is that markdown file (outside this git repo, in the project notes). Rerunning overwrites it if you pass the same path.

## What it queries

- Komo apartment rentals (`apartments-for-rent`) for Tel Aviv-Yafo, Ramat Gan, Givatayim, Ramat HaSharon, Herzliya, Bnei Brak, and Givat Shmuel, with the price range in the query.
- ad.co.il roommate, rental, and student boards, using each page's own city and price filters.
- Homeless roommate board (`/mate/`) for Tel Aviv, Ramat Gan, Givatayim, Herzliya, Ramat HaSharon, Bnei Brak, and Givat Shmuel. The general Homeless rent board is skipped because its price query does not stick.
- A single public request each to Yad2, Madlan, Homeless, WinWin, and OnMap. Those often answer with a block page, a redirect, or a client-rendered shell. Nothing is invented to fill the gap.

Travel uses OpenStreetMap Nominatim for the address. The default mode is a bicycle ride from the OpenStreetMap bike router. Twenty minutes reaches the neighborhoods just north and east of campus, including Afeka, Tzahala, and central Ramat Gan. Herzliya and Bnei Brak are searched; their centers are a longer ride, so a listing there is kept only when the routed ride is inside the cap. `--mode transit` keeps the older walking-plus-short-drive rule instead.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Run that from this directory.
