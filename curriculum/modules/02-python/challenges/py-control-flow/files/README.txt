Classify Signal Strengths
========================

Goal
----
Complete classify.py: classify_signal(snr) and summarize(values).

Rules
-----
  weak   — snr < 5
  usable — 5 <= snr <= 14
  strong — snr >= 15
summarize returns a dict of counts for each label.

Steps
-----
1) Press Start and open classify.py.
2) Try:  python3 classify.py 2 8 19
3) Prove: ./check
4) Press Done when check passes.
