# The World Today — 25 November 2026 (v2)

[![news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/ZQ051031/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/ZQ051031/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A newspaper-style front page that sums up the world news of
**Wednesday 25 November 2026** in one image — ten numbered stories,
a world map with a marker for every story, and an "also today" ticker.

## Why v2

The v1 front page ("The World Today", five stories, no map) ranked
**108 of 673** on the live leaderboard with a judge win rate of
**96.9743%**, 0.77 points short of the top-50 line (97.7406%). The
top-ranked entries are far denser — the leader packs "50 stories,
6 continents, one front page and a map". v2 answers that directly:

- **Ten stories instead of five** — the five v1 stories plus Nvidia's
  CEO return, the Sarkozy trial, Ukraine's 115bn euro aid ask,
  the Shenzhou-24 launch and Venezuela's $237bn debt reveal.
- **A world map** with a numbered red marker at the place each story
  happened, so the whole day is visible at a glance.
- **A longer ticker** — six more one-line items in the footer.
- **Tighter layout** — the lead art is a compact servers/triangle/
  padlock panel, the six grid stories run 3 across × 2 down, and the
  three map-side stories sit beside the map instead of below it.

## The ten stories

1. **Lead — CIA and spy chief's office hit by cyberattack.** The CIA
   and the Office of the Director of National Intelligence suffered a
   breach of unclassified systems; officials said no classified data
   was hit. The latest in a wave of hacks after the FBI crime database
   breach. (CNN / New York Times)
2. **Huang returns as Nvidia CEO.** Shares jump, then waver, as the
   ousted founder retakes the top job to cheers from staff.
   (Dow Jones / Morningstar)
3. **Huawei guilty on 10 of 12 counts.** A US jury convicted Huawei
   of trade-secret theft and bank fraud over its business in Iran;
   it was acquitted of racketeering. (Reuters / AP)
4. **Houthis hit Riyadh's tallest tower again.** A second drone strike
   on the PIF Tower in a week wounded 11 people, Saudi civil defence
   says. (Reuters)
5. **Kyiv confirms hit on Russian ship.** Zelenskyy confirmed
   Ukraine's drone strike on the cargo ship Sparta II in the Gulf of
   Finland, saying it carried weapons; Norway urged caution.
   (Reuters / Bloomberg)
6. **Australia signs pact with Solomons.** Australia and Solomon
   Islands signed a security pact on Wednesday, making Canberra the
   islands' defence partner of choice. (Reuters)
7. **Sarkozy case goes to trial.** French officials ordered the
   ex-president and his wife Carla Bruni to trial over the Libya case;
   the first hearing is in April 2027. (Reuters)
8. **Ukraine seeks 115bn euro in aid.** Zelenskyy puts the 2027
   foreign-aid ask at 115 billion euro.
9. **Shenzhou-24 launches.** China's crewed mission lifts off from
   Jiuquan on Wednesday.
10. **Venezuela debt put at $237bn.** Caracas reveals an
    eye-popping $237 billion debt load. (Dow Jones)

Also in the footer ticker: WHO evacuates Ebola hospital staff in DR
Congo after fighting; Real Madrid beat PSV 5-1; UK sanctions Houthi
officials; Mount Mayon eruption fears; Iraq orders seizure of Kurdish
oilfields; Trump awards Rudy Giuliani the Medal of Freedom.

Every story was checked against reporting published on 25 November
2026 before it was drawn.

## How the map is drawn

The navy panel in the middle of the page is a stylised world map.
Continents are hand-written (longitude, latitude) outlines — North
and South America, Africa, Eurasia, the UK, Japan, Indonesia,
Australia and New Zealand — projected onto the panel with a simple
equirectangular mapping (lon −180…180 → panel width, lat 75…−55 →
panel height) and filled in tan on navy. Ocean labels (Pacific,
Atlantic, Indian) sit in the open water.

Each story has a numbered red marker at the place it happened:
Washington, Santa Clara, Brooklyn, Riyadh, the Gulf of Finland,
Honiara, Paris, Kyiv, Jiuquan and Caracas. Marker positions are
computed from the same longitude/latitude projection as the land, so
a story never drifts off its coastline; where two cities crowd
together (Washington/Brooklyn, Gulf of Finland/Kyiv) the dot is
nudged a few pixels and a thin white leader line points back to the
true spot. Stories 8–10 are listed beside the map under
"Also on the map".

## Page anatomy

- Top strip: "The day in ten stories" / "One day — one page".
- Masthead: "The World Today", with the red dateline band below it.
- Lead story (1) with the compact cyberattack illustration.
- World map panel with the ten markers and stories 8–10.
- Six stories (2–7) in a 3 × 2 grid, each with a red number badge.
- Footer ticker with six more items, then the source line.

## How it works

`main.py` is pure Python standard library — no Pillow, no network. It
draws the whole front page with a hand-rolled rasterizer (a 5x7 bitmap
font, rectangles, lines, polygons and circles, plus a small map
projector that turns longitude/latitude outlines into panel pixels)
and a small pure-Python PNG encoder, then writes the 1024x1024 image
to `/output/entry.png`.

Run it:

```sh
python3 main.py
# writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png if set)
```

The output is deterministic: two runs produce byte-identical PNGs
(same size and sha256). The image is 1024x1024, well under the 1 MiB
limit, and needs no network at grade time.

## License

MIT — see [LICENSE](LICENSE).
