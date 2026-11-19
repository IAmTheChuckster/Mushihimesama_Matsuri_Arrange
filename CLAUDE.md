# CLAUDE.md

Mushihimesama Matsuri Arrange: a gameplay patch for the Cave CV1000 game `matsuri15` (Mushihime-Sama Ver 1.5,
2011/5/23 CAVEMATSURI VER1.5). The patch changes only the program ROM u4. It is shipped as two patchers that
rebuild the u4 from the user's own dumps: `index.html` (web patcher, GitHub Pages) and `patch.py` (Python,
standard library only), plus a MiSTer MRA in `mister/`.

Read **`dev_notes/NOTES.md`** first: how the patch works, game addresses, hooks, lessons, MAME notes and the
build log. `README.md` is the user-facing description.

## Owner rules (always)
- **No ROM data or game assets in the repo, the patchers or any release.** Only source, changed-byte tables and
  notes. `roms/`, `*.zip`, `*_u4` and `.images/` are ignored; never add them. Never modify the original ROMs.
- **CAVE MATSURI (the first title-menu entry) stays the unpatched game.** Every gameplay change is for
  MATSURI ARRANGE (Ultra) only, and every hook must fall through to the original code when not `active`.
- **Confirm a change with the owner before making it.** When interrupted, stop and wait. Keep messages short.
- **Never ask whether to commit or push.** The owner says when ("commit", "commit to github" = commit and push).
- **Every patched `index.html` that is made gets the next higher build number**, committed or not. Never reuse a
  number. Take "Next build" from the build log in `dev_notes/NOTES.md`, then add the row and bump it.
- **Update `README.md` and `dev_notes/NOTES.md` every time** something changes (build, feature, fix, rename,
  finding): README "Current build" line + CRC and Change Notes; NOTES build log, hooks/addresses, lessons.
- Use MAME 0.289 only. Call the game `matsuri15`. If stuck on a hard part, say so.
- The owner tests every build on a MiSTer (CV1k core, MRA setname `mushimatsuriarr`) and confirms it.
- Commit message style: `Build N: what changed`, ending with the attribution lines the session gives.

## Inputs (owner's machine)
- `roms/matsuri15.zip` (original u4 CRC `6af99f0e`).
- `roms/435A07E3.zip`: the owner's Xbox 360 Mushihimesama Games-on-Demand package (holds
  `5F9DF6331EAE85814989` + `.data`). The アレンジモード banner picture is cut from it at patch time, so both
  patchers and `build.py` need it. The GOD file can have any name, be .zip or .7z, with the files in any folder.

## Build a new version
The assembler runs in WSL (Ubuntu-24.04), which has `sh-elf` binutils; `build.py` calls `sh4-linux-gnu-*`, so put
symlinks `sh4-linux-gnu-{as,objcopy,nm}` -> `/usr/bin/sh-elf-*` in a temp dir at the front of `PATH`.
1. Edit `src/title.s` (patch code, runs from RAM 0x0C7C0000) and/or `src/build.py` (warning text, `SITES` hook
   table, glyph area).
2. `python3 -I src/build.py roms/matsuri15.zip OUT_u4 roms/435A07E3.zip` prints the patched u4 CRC.
3. Test in MAME (see below): MATSURI ARRANGE and CAVE MATSURI, and the game-over path when hooks change.
4. `python3 -I src/update_patchers.py roms/matsuri15.zip OUT_u4 BUILD` (BUILD = next build number) updates
   `patch.py`, `index.html` and writes the MRA to the repo root; move it to `mister/` (it must differ from the
   previous one only in CRC/date).
5. Verify: `python3 -I patch.py roms/matsuri15.zip --god roms/435A07E3.zip --zip --mra` must give a u4 identical
   to `OUT_u4` (it writes into `roms/`, which also gives the owner the test files), and the web page with the same
   two files must show the same CRC ("Matches build N"). For the page: serve the repo on 127.0.0.1, open it in
   the built-in browser, feed both files to the inputs with a DataTransfer, read `#outcrc`.
6. Update README + dev notes (rules above).
Run Python with `-I`.

## MAME test environment
- The owner's MAME 0.289 is in WSL at `~/mame` (from `IAmTheChuckster/mame0.289_claude`): `bin/cv1k`,
  `lua/harness.lua`, `scripts/run.sh`. Env: `BT_SCHED` (input schedule `FRAME KEYS`), `BT_SNAP`, `BT_FRAMES`,
  `BT_SAVE`, `BT_DUMP`. Keep test files under `~/mame/work/m15/` (own ROM folder and nvram folder).
- `-state` with `-autoboot_script` does not run the script: test from boot with a schedule. First boot of a new
  nvram folder takes longer.
- Typical schedule (patched): coin at 3000, stick down at 3060 (cursor to MATSURI ARRANGE), start at 3120; the
  patch then picks Ultra and the shot by itself. Unpatched / CAVE MATSURI Ultra: coin 3000, start 3100, down
  3300 and 3340, A 3400, right 3540 (choose 上等 on the warning), A 3600, A 3800.
- Breakpoints/watchpoints are unreliable under the DRC; use RAM/VRAM dumps, screenshots and Lua polling.
