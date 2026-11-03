# Mushihimesama_Matsuri_Arrange

A gameplay patch for `Mushihime-Sama Ver 1.5 (Japan, 2011/5/23 CAVEMATSURI VER1.5)`<br>
This repository holds only source, tools and notes. **No ROM data is included**; you patch your own legally owned dump.
## To Do:
1. Import Original Music
2. Create arrange mode based on the 360 arrange

   
## About
Why did I make this? Because it's fun and for my own personal research to see the capabilities of Claude.<br>
While Claude was used I put effort in making sure there are balanced gameplay.<br>
I did all the testing and planning.

## Change Notes

## Patching the game

### With the web patcher (easiest)
Open the **[Web Patcher](https://iamthechuckster.github.io/Mushihimesama_Matsuri_Arrange/)** (`index.html`) and drop in your `rom.zip`. It checks the file names and CRCs, builds the patched files automatically, and lets you download just the patched files or a complete `rom.zip` romset. Everything runs in your browser; nothing is uploaded.

### With Python


## Testing
This patch was tested with MAME 0.289 and [CV1k core for the MiSTer FPGA by Raki](https://www.patreon.com/c/ikamusume/posts)<br>
It may even work on a PCB but do so on your own risk.

## Credits

- [IAmTheChuckster](https://github.com/IAmTheChuckster)  project, testing
- [Claude](https://claude.ai) (Anthropic)  reverse engineering and patcher code
- Tested on the CV1k core for the MiSTer FPGA by [Raki](https://www.patreon.com/c/ikamusume/posts)

## Disclaimer

This repository contains a fan-made patch for research and technical analysis. The repository does not intentionally distribute the original game ROM, executable, or game assets. Users must obtain their own copy of the original game. This project is unofficial and is not affiliated with, endorsed by, or authorized by CAVE. All rights to the original game and its associated intellectual property remain with their respective rights holders. No license to third-party copyrighted material is granted by this repository.
