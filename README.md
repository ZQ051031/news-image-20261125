# The World Today — 25 November 2026

[![news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/ZQ051031/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/ZQ051031/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A newspaper-style front page that sums up the world news of
**Wednesday 25 November 2026** in one image.

## The five stories

1. **Lead — CIA and spy chief's office hit by cyberattack.** The CIA and
   the Office of the Director of National Intelligence suffered a breach
   of unclassified systems; officials said no classified data was hit.
   The latest in a wave of hacks after the FBI crime database breach.
   (CNN / New York Times)
2. **Huawei guilty on 10 of 12 counts.** A US jury in Brooklyn convicted
   Huawei of trade-secret theft and bank fraud over its business in Iran;
   it was acquitted of racketeering. (Reuters / AP)
3. **Houthis hit Riyadh's tallest tower again.** A drone strike on the
   PIF Tower, the second in a week, wounded 11 people. (Reuters)
4. **Kyiv confirms hit on Russian ship.** Zelenskyy confirmed Ukraine's
   drone strike on the cargo ship Sparta II in the Gulf of Finland,
   saying it carried weapons; Norway urged caution. (Reuters / Bloomberg)
5. **Australia signs pact with Solomons.** Australia and Solomon Islands
   signed a security pact on Wednesday, making Canberra the islands'
   defence partner of choice. (Reuters)

Also noted in the footer: WHO evacuates Ebola hospital staff in DR Congo
after fighting; Real Madrid beat PSV 5-1; US inflation data due.

## How it works

`main.py` is pure Python standard library — no Pillow, no network. It
draws the whole front page with a hand-rolled rasterizer (a 5x7 bitmap
font, rectangles, lines, polygons and circles) and a small pure-Python
PNG encoder, then writes the 1024x1024 image to `/output/entry.png`.

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
