SUMMARIZE RECEIVER EVENTS

Complete summarize() in events.py. Return a dictionary containing:

- station_counts: number of events for each station
- frequencies: a sorted list of unique frequency_hz values
- strong_ids: event IDs, in input order, whose dbm is at least -60
- average_dbm: average dBm for each station

Use all of these language tools in your implementation:
1. a normal list
2. a dictionary
3. a set or set comprehension
4. at least one comprehension
5. collections.defaultdict

Do not modify EVENTS. Run `python3 events.py`, then `./check`.
