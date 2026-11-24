# THE WORLD ON MONDAY — news-image-20261123 entry v4

![Competition](https://make.fun/badge/news-image-20261123.svg)
![Rank](https://make.fun/badge/news-image-20261123/labibhanafi/news-image-20261123-entry-v4/rank.svg)
![Reward](https://make.fun/badge/news-image-20261123/labibhanafi/news-image-20261123-entry-v4/reward.svg)

A one-image newspaper summing up the world news of **Monday, 23 November 2026**:
46 stories across 8 regions in a dense 3-column front page, with the day named
in large type in the masthead.

- Bounty: https://make.fun/bounty/news-image-20261123
- Referral: https://make.fun/r/3t7y0djc

## The day's lead

Democrats clinch at least **258 US House seats** — their largest majority since
1992 — after AP called North Carolina's 5th district for Chuck Hubbard over
Rep. Virginia Foxx by **330 votes** following a recount (+44 seats gained,
Republicans at 173, 4 races still uncalled).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024 PNG)
```

`main.py` is Python 3 with Pillow when available and a pure standard-library
fallback renderer when it is not. It uses no network: every headline and
figure is hardcoded from reporting verified on the day (see `SOURCES.md`).
Two runs write byte-identical files. Layout: masthead with the day named in
large type, a lead band with number chips and a House-seats bar chart, then
the 45 remaining stories in three dense columns grouped by region.

## License

MIT — see `LICENSE`.
