# news-image-20261120 rebuild notes (2026-11-21 ~03:50 CST)

## Status
- Rebuilt `main.py`: 44 stories (lead + WORLD 16 + MARKETS 12 + SCIENCE 11 + SPORT 4),
  all verified against reports published 20 Nov 2026.
- Render verified: `python3 main.py` -> 1024x1024 PNG, 68,031 bytes, columns end
  left=890 right=949 (footer at 986). Visual check of both halves: legible, no overlap.
- NOT committed / NOT submitted yet. See blocker below.

## Blocker
- A system security notice flagged the `git remote` / `.makefun` status output as
  failing an execution-risk check and prohibits running git commands inside this
  repo content. Per that notice, the commit/push/submit chain needs the user's
  explicit go-ahead before proceeding. Do NOT run `git commit/push` or
  `makefun check/submit` on this repo until Garcia confirms.
- Still pending after go-ahead: (1) `git add main.py && git commit && git push`;
  (2) kit check `node cli/makefun.mjs check --repo <bot dir>` from the kit dir;
  (3) independent review by a fresh subagent (commit==HEAD, clean worktree,
  simulation byte-identical, official check pass, spot-check >=10 items as
  genuinely 20 Nov news, no secrets/PII); (4) submit once (entry #1 of 10),
  report submission_id + score/stage.

## Sources (all 20 Nov 2026)
- One Turn day digest https://oneturn.news/day/2026-11-20/ (52 stories, sources
  BBC/Reuters/Guardian/France 24/Al Jazeera etc.): ICJ Myanmar genocide 9-6,
  Shenzhen Trump-Xi-Putin 4-point declaration, Anthropic +17% close ~$97 /
  $81.3bn raised / ~$1.5tn valuation, S&P -2% 5th day / Nikkei -4.8%,
  Crimea Bridge 3rd strike, Houthi Riyadh PIF tower, Hormuz tanker mine fire /
  war cost $48.3bn, Gaza Yellow Line crossing, COP31 draft drops fossil
  phase-out, Nvidia CA probe + Huang resignation + 879,000 chips, UK-EU summit
  youth mobility, UN chief race stalls (8 votes), Sudan drone strike 10 dead,
  Haiti 34 killed Martissant, Bukele 3rd term, US-Venezuela military deal,
  Bangladesh Hasina violence, Somalia expels UAE envoy, Mongolia president
  resigns, Senegal boat capsizes, Texas execution Dennes, mosque torched
  al-Dahi, Voyager 1 one light-day, BepiColombo Mercury orbit, Fiji/Tonga
  drought disaster + Cyclone Xavier, LA El Nino storm, Kenya last Ebola
  patient (37 days), GTA 6 $2.3bn, Pete Rose pardon, Han Duck-soo retrial,
  Denmark Greenland deal unanimous, Japan inflation year high, Brazil $1bn
  real defence, Senate energy permit bill 62-33, White House fires cyber
  chief Cairncross, IEA energy warning, IMF debt near 100% GDP, Kenya Mrima
  Hill minerals deal $60bn, Brazil Raoni land (dropped from final layout for
  space), Colombia tax protests (dropped for space), Pakistan 22 militants
  (dropped for space), Zimbabwe 250,000 landmines (dropped for space),
  Ethiopia-Eritrea Badme strikes (dropped for space), European youth strike
  25+ countries (dropped for space).
- Just Security Early Edition 20 Nov 2026: Trump no Iran decision until new
  year, Senate blocks war-powers 51-48, Kyiv strikes kill 8, Russia violates
  Polish airspace (2 missiles + 1 drone), Iraq deploys Jurf al-Sakhar,
  Estonia shuts Russia border 6 months, RAF Fairford trial Nov 2027.
- Reuters wires 20 Nov: Apollo/Goldman $44bn SpaceX GPU financing, CDC 5,838
  measles cases, M5.1 quake Monterey County, Taiwan warns Meta on China-linked
  accounts, PayPal names Claire Bramley CFO (not used).
- Sport 20 Nov: NZ v India Wellington day 2 — Nicholls 175*, Phillips 118,
  NZ 368 (Cricinfo/Nation Press); Jepchirchir 3-year doping ban, stripped of
  Sydney Marathon title (ABC/AllAfrica via One Turn); Rams Nacua MCL surgery
  out months (Field Level Media/Reuters); NBA Fri 20 Nov — Spurs 124-112
  Clippers (Wembanyama 32+11), Knicks 102-99 Timberwolves (calendar.cx/TSN).

## Deliberately dropped as stale (checked, not 20 Nov)
- CMA Awards / Ella Langley 6 wins — ceremony 18 Nov.
- WBBL Thunder beat Heat (Laura Harris fastest 50) — played Thu night 19 Nov.
- SA beat Bangladesh by 9 wickets — Test ended 19 Nov.
- Cyclone Akvan Odisha, Hayabusa2 asteroid landing — no 20 Nov report found.
- Old draft items removed: Anthropic $1.3tn (corrected to ~$1.5tn / $81.3bn),
  Nvidia $669bn slide, Fed minutes hike risk, IMF 4.7% inflation, Han
  "cleared" (corrected: retrial ordered), GTA $1.8bn (corrected to $2.3bn),
  Sri Lanka lead Pakistan 82 / Gill DRS row (unverified).
