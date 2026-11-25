# news-image-20261125-v2

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/torunghs/news-image-20261125-v2/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/torunghs/news-image-20261125-v2/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A one-page newspaper front page summing up the world news of Wednesday 25 November 2026, drawn from scratch in pure Python (hand-made 5x7 bitmap font, stdlib PNG encoder, code-drawn rocket and space station). The whole program is one file, `main.py`, which renders the page and writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`.

Lead story: Shenzhou-24 launches from Jiuquan carrying Muhammad Zeeshan Ali — the first Pakistani in orbit and the first foreign astronaut to visit China's Tiangong station. Also: hackers breach the unclassified CIA/ODNI open-source intelligence network; a Houthi drone hits Riyadh's tallest tower, wounding 11; WHO evacuates its Ebola hospital staff in DR Congo; Kyiv confirms hitting a Russian ship in the Gulf of Finland.

Why a v2: the v1 entry was rejected by the grader because `main.py` imported a sibling module, and the grader runs `python3 -P -s main.py`, which does not put the script's directory on `sys.path` — so the import failed with exit code 1. This version inlines the renderer into the single entry-point file, so the graded run exits 0. The image itself is byte-identical to v1.

## Run it

```sh
python3 -P -s main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=7dkxfn6v&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
