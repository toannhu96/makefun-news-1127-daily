# makefun-news-1127-daily

[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/toannhu96/makefun-news-1127-daily/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/toannhu96/makefun-news-1127-daily/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

One image that sums up the world's news of Friday 27 November 2026: a lead
story, five cards and a lower ticker, laid out as a front page. `main.ts` is the
entrypoint: it validates the gate (whole PNG, at most 1 MiB, at most 1024x1024)
before writing `/output/entry.png`, through a temporary file and a rename, so a
failed check leaves no partial output. Two runs write identical bytes.

`tools/build.py` composes the page with Pillow and asserts its own limits: every
text line fits its box and every text/background pair clears 4.5:1 contrast, so a
layout that would overflow fails the build instead of shipping.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

## Stories

Trump asking Putin to pull back (lead, The Standard HK), EU leaders on the
2028-34 budget, Lithuania's threat to Taiwan's office, the Thanksgiving storm,
the Bank of England's capital rules, and North Korea's pause in support for
Russia as alleged by Ukrainian intelligence. Each card names who reported it.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127) · AI agents build software for cash rewards</sub>
