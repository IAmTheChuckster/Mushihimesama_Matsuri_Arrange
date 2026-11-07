# Mushihimesama Matsuri Arrange

A gameplay patch for `Mushihime-Sama Ver 1.5 (Japan, 2011/5/23 CAVEMATSURI VER1.5)`<br>
This repository holds only source, tools and notes. **No ROM data is included**; you patch your own legally owned dump.
   
## About
Why did I make this? Because it's fun and for my own personal research to see the capabilities of Claude.<br>
While Claude was used I put effort in making sure there are balanced gameplay.<br>
I did all the testing and planning.

## Change Notes
- **Warning screen.** Shows a disclaimer that this is an unofficial project, `HAVE FUN!!!` and `2026/11/7 MATSURI ARRANGE`, both centred, all in capitals.
- **Title menu.** After a coin is inserted, the title shows **CAVE MATSURI 1.5 / MATSURI ARRANGE** above `PRESS 1P OR 2P START` and `CREDITS`, which move down.
  - Move the arrow with the joystick up and down. It starts on CAVE MATSURI 1.5 every time; that is the unpatched game.
  - The ranking line at the bottom is hidden once a coin is in; the attract screen keeps it.
  - The game's own Original / Maniac / Ultra and shot select follow as usual.
- **MATSURI ARRANGE (Ultra mode only).** Original and Maniac are unchanged for now.
  - **Chain bullet cancel.** When an enemy dies, enemy bullets within 48 px turn into small crystal gems. Any bullet within 32 px of a cancelled bullet turns into a small gold gem, and the chain keeps going until no bullet is in range.
  - **Gem counter.** Gems you collect fill a hidden counter: small crystal +1, large crystal +5, small gold +10, large gold +15. At 12000 you get an extra bomb (up to 6) and the counter starts again from 0. It is kept when you lose a life and reset for a new game. There is no number on screen; the bomb gauge below shows it.
  - **Player 2 off.** 2P start does nothing while MATSURI ARRANGE is selected.
  - **Weapon change.** The 4th button (shown as `Weapon Change` in the MiSTer MRA, Y by default) switches player 1 to the next weapon on the fly: 1 → 2 → 3 → 1. The weapon is rebuilt with the game's own routine, so shot, laser and colour all change, and power, bombs and score are kept. Each change plays the sound test's SE code 17.
  - **Straight into the game.** Choosing MATSURI ARRANGE runs through mode select (ULTRA) and shot select (top-right weapon) by itself and starts the game; change weapons in play with the 4th button.
  - **Bomb cancels bullets.** The bomb button (and the automatic bomb when you are hit) no longer does the normal bomb: it uses one bomb and turns every enemy bullet on screen into a small crystal gem, with no damage to enemies. She no longer throws the bomb ball, so there is no blast; you are invulnerable for about 1.5 seconds after using it (no shield bubble is shown). Nothing happens with 0 bombs.
  - **Bomb gauge.** For every 2000 counter points one gold swirl fills one of the 6 right-hand slots of the bomb bar, from the right edge to the left; at 12000 a bomb is added (maximum 6), she gives her bomb shout, and the slots empty. The glyphs slide with the bar when it moves (boss start, score tally).

## Patching the game

### With the web patcher (easiest)
Open the **[Web Patcher](https://iamthechuckster.github.io/Mushihimesama_Matsuri_Arrange/)** (`index.html`) and drop in your `matsuri15.zip`. It checks the file names and CRCs, builds the patched files automatically, and lets you download just the patched files or a complete `mushimatsuriarr.zip` romset. Everything runs in your browser; nothing is uploaded.

### With Python
Needs Python 3 only. Download `matsuri_patch.py`, then run:
```
python3 matsuri_patch.py matsuri15.zip --zip --mra
```
This writes `matsuriarr_u4` (CRC `41dbfde1`), `mushimatsuriarr.zip` (u2, u23, u24, matsuriarr_u4) and `Mushihimesama Matsuri Arrange.mra` for MiSTer. `-o FILE` sets where `matsuriarr_u4` is written. The original u4 must have CRC `6af99f0e`.

### Using the patched files
- **MAME:** copy your matsuri15 set, replace its u4 with `matsuriarr_u4`; the checksum warning is expected.
- **MiSTer (CV1k core):** `mushimatsuriarr.zip` goes in `games/mame`, the `.mra` in `_Arcade`.

### Building from source
`python3 src/build.py matsuri15.zip OUT_u4` (needs `binutils-sh4-linux-gnu`), then `python3 src/update_patchers.py matsuri15.zip OUT_u4 BUILD`.

## Skills

## Testing
This patch was tested with MAME 0.289 and [CV1k core for the MiSTer FPGA by Raki](https://www.patreon.com/c/ikamusume/posts)<br>
It may even work on a PCB but do so on your own risk.

## Credits

- [IAmTheChuckster](https://github.com/IAmTheChuckster)  project, testing
- [Claude](https://claude.ai) (Anthropic)  reverse engineering and patcher code
- Tested on the CV1k core for the MiSTer FPGA by [Raki](https://www.patreon.com/c/ikamusume/posts)

## Disclaimer

This repository contains a fan-made patch for research and technical analysis. The repository does not intentionally distribute the original game ROM, executable, or game assets. Users must obtain their own copy of the original game. This project is unofficial and is not affiliated with, endorsed by, or authorized by CAVE. All rights to the original game and its associated intellectual property remain with their respective rights holders. No license to third-party copyrighted material is granted by this repository.
