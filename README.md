# makefun-news-1127-daily

<!-- TODO: paste the three make.fun badge lines for toannhu96/makefun-news-1127-daily here.
     The official badge snippets were not available while this was built, so none were invented. -->

Entry for make.fun's `news-image-20261127` bounty: a single 1024x1024 newspaper-style front page
summing up Friday 27 November 2026's world news. A lead story (Trump says he asked Putin to pull
back military aggression in Europe) is followed by five more: the EU budget summit, Lithuania and
Taiwan's representative office, the US Thanksgiving storm, the Bank of England's capital-rule cut,
and North Korea pausing support for Russia. Each card names the outlet that reported it
(The Standard, Hong Kong; SBS News, Seoul).

- `tools/build.py` composes the page with Pillow and writes `entry.png`. It asserts that text fits
  its boxes, every text/background pair has at least 4.5:1 contrast, and the canvas is 1024x1024.
- `main.ts` (Node 22, standard library only) validates `entry.png` (whole PNG, at most 1 MiB, at most
  1024x1024) and writes it atomically to `/output/entry.png`.

## Run

```
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

Rebuild the image (needs Python 3 with Pillow and the DejaVu fonts): `python3 tools/build.py`
