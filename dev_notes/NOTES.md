# Developer notes (for Claude Code / future work)

No ROM data belongs in this repo, in the web page or in any release. Only source, changed-byte tables and notes.
Work on `main` is released as numbered builds; `wip` is the scratch branch.
`CLAUDE.md` (repo root) is the short version Claude Code loads at the start of every session: owner rules, inputs,
build steps and MAME test setup. Keep it in step with these notes.

## Rules from the project owner
- CAVE MATSURI (first title entry) stays unpatched. Every gameplay change is for MATSURI ARRANGE (Ultra) only.
- Confirm a change with the owner before making it. When interrupted, stop and wait. Keep messages short.
- Never commit ROMs, MAME work dirs or zips. Never modify the original ROMs. Use MAME 0.289 only.
- Call the game `matsuri15`. If stuck on a hard part, say so (the owner may switch models).
- The owner tests on a MiSTer (MRA setname `mushimatsuriarr`) and confirms each build.

## Inputs, outputs, build
- Original: `matsuri15.zip` (Cave CV1000), u4 CRC `6af99f0e`. u4 stores 16-bit words byte-swapped; `build.py` edits the swapped ("natural") domain.
- `python3 -I src/build.py matsuri15.zip OUT_u4` assembles `src/title.s` (SH-3, needs `sh-elf` binutils), applies the `SITES` table and prints the patched u4 CRC.
- `python3 -I src/update_patchers.py matsuri15.zip OUT_u4 BUILD` embeds the changed bytes in `patch.py` and `index.html` and rewrites the CRC in the MRA. Then update the CRC line and the "Current build" line in README.
- Verify: `python3 -I patch.py matsuri15.zip --zip --mra` and the web page (Playwright: upload the zip, click each download) must give a u4 identical to `OUT_u4`. The MRA must differ from the previous one only in the CRC.
- Commits end with the attribution lines the session gives. Build N commit message style: "Build N: what changed".

## Build numbers
- **Every patched `index.html` that is made gets the next higher build number**, committed or not (owner rule, 2026-11-19). Never reuse a number, even for a quick fix of a build that was only tested.
- Build log (u4 CRC of the patched file):

| Build | What | u4 CRC | State |
|---|---|---|---|
| 1-18 | see git history | | committed |
| 19 | warning date 2026/11/12 | 0bc2595b | lost (uncommitted changes were reset) |
| 20 | warning date 2026/11/19 (made as "build 19") | 89fad22f | never committed |
| 21 | アレンジモード banner (made as "build 20"; tested on MiSTer) | b59a048f | never committed |
| 22 | banner also in the stage intro; patch.py rename; GOD step in index.html | 334b3e31 | never committed |
| 23 | removed unused code (bombfx_wrap, old counter literals, json import, needProps); same features as 22 | 52dc79a6 | never committed |
| 24 | warning screen and MRA date 2026/11/20; otherwise as 23 | c664efdb | committed (7b22893) |
| 25 | bullet graze: counter in gold digits under the + counter, 100 points per bullet per frame | 2b961153 | never committed |
| 26 | graze counter only shown with the game's + counter (follows it; hidden on CONTINUE / GAME OVER) | fa121c52 | never committed |
| 27 | banner bar red in MATSURI ARRANGE | bd9eb63b | never committed |
| 28 | graze counter no longer counts down; back to 0 when a new stage starts (kept through deaths and continues) | 050412f4 | never committed |
| 29 | grazing bullets drawn brightened (tint 0xFF) | 4ee8c8a9 | never committed |
| 30 | bright grazing bullets removed again (CPU cost); u4 identical to build 28 | 050412f4 | current |
- **Next build: 31.**

## How the patch runs
- A boot stub copies the patch to RAM `0x0C7C0000` and applies the sites table (address, expected old long, new long) in `build.py`. A site whose old long does not match aborts the build.
- Patch variables at `0x0C7CF000`: +0 title stamp, +4 coin stamp, +8 mode (1 = ARRANGE), +16 hidden gem counter, +20 cancel busy, +24 4th-button previous state, +28 scan early-reject window (64 from the chain cancel, 0x7FFF from the bomb cancel), +32 graze counter (0..999999), +36 the stage the graze counter belongs to (stage number, 0 = stage 1), +40/+44 dst x/y of this frame's + sign main draw (the game's + counter), +52 list address right after the banner text draw, +56 = 1 when the + counter was drawn this frame. +0x100..+0x177 graze digit draws are built there before being inserted.
- Hooks wrap pool literals. `active` = (mode == 1 and game mode word `0x0C1FB630` == 2). Every wrapper must fall through to the original routine when not `active`.
- Main hooks: `hud_wrap` (0x0C0ABFC0, per frame), `gem_wrap` (0x0C05B6FC wraps 0x0C05FCF0), `spawn_c_wrap` / `spawn_g_wrap` (gem spawners 0x0C0A6790 small crystal, 0x0C0A6C30 gold), poll wraps, the bomb hooks below, and `end_wrap` (builds 21-22, banner).
- **Banner (builds 21-22).** `end_wrap` replaces the literal at `0x0C054160` (the frame renderer `0x0C0540F0` closes its blitter list with `0x0C049E24(0xFFFFFFFF)`). When active and the picture is present it walks the list (`0x0C049B30` start, `0x0C049B3C` write pointer; ops 0x1 draw 20 bytes, 0x2 upload 16 + w*h*2, 0xC clip 4), points the two ウルトラモード draws (src 1304,768, w-1 7, h-1 63: shadow attr 0x1300 and text 0x1100) at VRAM 1320,840, and (build 27) turns the banner's glowing bar red: the draw right before the shadow draw is the bar (src 4880,512, 16x224, attr 0x1300, alpha 0x40FF, additive, tint R/G/B 0x00/0x00/0x80 = the purple); its tint is set to 0x0080 / 0x0000 (R 0x80). Then, only if it found the banner draws, it appends an upload of the picture there (so frames without the banner, e.g. the title menu, get no upload; build 21 first required the gameplay HUD to have run, which left ウルトラモード showing during the stage intro) (`2000 0000 9999 9999 x y w-1 h-1` + 512 pixels, 8 px wide as all uploads must be a multiple of 8 wide on the MiSTer core).
- **Graze (build 25).** `graze` (called from `hud_wrap` when `active`) walks the active bullet list and counts bullets within 24 px of player 1 (player x/y = player block +0x4C/+0x50, 16.16, same space as the bullets; the shield is ignored). Count > 0: counter += count (max 999999), `0x0C05A390(0x0C1FBC30, count * 100)` adds the points. Since build 28 the counter never counts down: when the stage number (`0x0C1FB634`, next to the game mode word, 0 = stage 1; it changes when the next stage starts, not at the tally) differs from VARS+36 it is set to 0 and +36 updated; deaths and continues keep it. `gznum` also hides it while the stage differs (next stage's intro). `title_wrap` and the boot code reset both. `gznum` (from `end_wrap`, only in frames with the banner) builds one draw per digit (no leading zeros) from the white 16x16 point digits at VRAM 5888,16d (d = 0..9; `+` at 5888,160) with attr 0x1300, alpha 0xFF00 and the score pop-up tint 0x00BF / 0x8040 (gold), and inserts them right after the banner text draw (the rest of the list is moved down), so they are layered like the HUD. Drawn only in frames where the game drew its own + counter (build 26), placed from the + sign's main draw (src 5992,160, alpha 0xFF00): first cell at that dst + (-14, +6), 8 px apart. The game's + counter (white digits at VRAM 5992,16d, + at 5992,160; shadow alpha 0x807F tint 0, main alpha 0xFF00) is not drawn on CONTINUE / GAME OVER, and when idle it is drawn off the left edge (dst y about -86) and slides in when points come; the graze counter follows it.
- **Bright grazing bullets (build 29, removed in build 30).** Tried: a second pass over the list tinting enemy-bullet draws (bullet sheet VRAM x 3328..4095, y 256..511) within 24 px of the player to 0x00FF/0xFFFF. It worked (hot magenta, not white: the tint only multiplies) but cost a second full list walk per frame, about 3-6% of a frame together with the other passes, so the owner dropped it. Mapping if needed again: screen = (game x - 6, 319 - game y); a draw's screen centre = (Y - by + 84 + h/2, bx + 23 - X - w/2), (bx, by) = banner text dst.
- **Score.** 12 digits at player block +0x24 (`0x0C1FBC30`), ones digit first (that is why a plain search for the score finds nothing). `0x0C05A390(r4 digits, r5 points)` adds a 32-bit value (it converts it with `0x0C05A520` into the temp digits at `0x0C1F8980`, then adds with carry). The game's own caller is at `0x0C05FA60`.
- **Banner picture.** u4 natural offset `0x1FF000` (CPU `0xA01FF000`): `ARG1` + 12 zero bytes + 8x64 ARGB1555 big-endian words (stored sideways like all VRAM art). It is NOT in the repo or the patchers: `patch.py` / `index.html` cut it from the user's 360 GOD package (`5F9DF6331EAE85814989`, /res/DISKDATA/C/h20.bin, Cave archive entry `0_00_B.tga`, Cave LZSS, 4096x4096 ARGB1555 bottom-up; アレンジモード at x 3153-3168, y 2708-2829, halved 2x2: opaque when 2+ of 4 opaque, grey = their average). `update_patchers.py` leaves that area out of the embedded data; the CRC covers it. Without the magic the banner stays ウルトラモード.
- VRAM facts (MAME dump, 8192x4096): system sheets are uploaded once at boot and never change; the stage-graphics area (about y 2304-3000) and the framebuffers (top left, x 7424-7935 at the top) are rewritten. ウルトラモード is at 1304-1311 x 768-831; 1320-1327 x 840-903 (after オリジナルモード, where the 360 puts アレンジモード) is empty.

## Game addresses found
- Player block `0x0C1FBC0C`: +8 lives, +12 bombs, +16 power, +20 level, +24 active weapon, +0xD4 protection counter (respawn sets 255; non-zero = invulnerable and the shield bubble is drawn), +0xEC object pointer. Object +124+44 is the 64-frame bomb-active timer.
- Bullet manager pointer `0x0C19CC40` (list head +0x7E004); remove routine `0x0C08F140`.
- Hit / bomb routine `0x0C05FE40` (r8 = player block, r10 = 1 on the hit path). It calls `0x0C0E3B90` (launches the thrown bomb ball, whose blast is the cyan cloud) and `0x0C05DB30` (start). Sites: `0x0C05FEB8` -> `bombgo_wrap` (returns 1 without launching the ball when active), `0x0C05FEBC` -> `bomb_wrap` (bombcancel into small crystals, shout unless the hit path, sets player+0xD4 to 90 only if lower).
- Sound: request wrapper `0x0C0E36F0` -> queue `0x0C05923C`. Bomb shout helper `0x0C0E2330` (type 7, id 0x91). Weapon change uses type 6 id 0x5B. Some voices use a second queue that is not visible at 0x0C05923C. The voice the owner wants on the bomb refill is the やった one (README To Do #2, id 0x92 per the owner); not located by code search yet.
- Stage number: `0x0C1FB634` (0 = stage 1). Found with an invulnerable run (Lua keeps player block +0xD4 at 200 every frame, fire held): stage 1 boss beaten about frame 14500, tally until about 19500, stage 2 from about 20000.
- Score: the Ultra table seeds 30,000,000 down to 26,000,000. The on-screen score is not a plain integer in RAM (a search for HUD values found nothing), so score-related tests could not be forced by poking RAM.

## Lessons
- **Do not hook shared routines blindly.** Build 10 hooked `0x0C0602A0` thinking it was the bomb blast. It also runs when the player dies, which broke the game-over path and removed name entry (found by bisecting builds 8, 12, 10, 9 on a real MiSTer; fixed in build 17). The cyan cloud was the thrown ball, not this routine. If a hook is needed on a routine with several callers, check every caller in the disassembly first.
- Bisecting works well: each old build's `index.html` and MRA can be taken from git history and given to the owner to test.
- Continue resets the on-screen score in some paths; name entry compares against the table for the mode.

## MAME test environment
- Set up with the `IAmTheChuckster/mame0.289_claude` repo (the `learn-cv1000-game` skill describes it): MAME 0.289, CV1000 BIOS, a Lua harness. Games run headlessly; run in the background and poll.
- The harness used here took environment variables: `BT_SCHED` (input schedule, lines like `FRAME KEYS`), `BT_SNAP` (screenshot every N frames), `BT_DUMP` / `BT_DUMPF` (RAM ranges at given frames), `BT_POKE` (`[frame:]addr=val` every frame). These scripts were in the previous session's workspace and are not in this repo; recreate them as needed.
- The ROM dir needs the other CV1000 roms plus the built u4 (name it as the set expects). A CRC warning for u4 is normal when it is patched.
- Breakpoints and watchpoints do not fire reliably under MAME's DRC. Use RAM dumps, screenshots and Lua polling instead. Patch changes need a fresh run (no saved states built with another build).
- Typical flow: coin, start, pick ARRANGE, play to a boss, press B (bomb) and look at screenshots every 4 frames.

## Open items
- To Do list in README: force Ultra MAX by removing the mode select, the bomb-refill voice (やった), mode select highlight in gold.
- The true last boss (Aki) condition: the owner was going to report play results.
- After a MATSURI ARRANGE game, mode (+8) stays 1 until the next coin, so the next Ultra attract demo counts as `active` (ARRANGE features, the アレンジモード banner and, since build 25, grazing and the graze counter in the demo). Seen in MAME, build 21; not changed yet (owner to decide).
- Blitter in MAME 0.289: `cv1k_v.cpp` (upload/draw formats documented there). The list kick is `0x0C049BE0` (vblank callback `0x0C049BBC`); begin-list `0x0C049DFC`; the 42 op emitters all write through `0x0C049B3C`.
- MAME notes: `-state` with `-autoboot_script` does not run the script, so tests run from boot with a schedule. Debugger watchpoints never fire in this headless setup, and Lua write taps miss DRC writes (with `-nodrc` they fire but the 64-bit mask crashes the Lua binding); find writers in the disassembly instead. The blitter's VRAM can be dumped from Lua with `emu.item(manager.machine.devices[":blitter"].items["0/m_bitmaps"])` (`read_block` counts bytes).
