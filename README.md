# rito-launcher
A launcher to launch games from Riot Games under Linux.
![Image of the Launcher, with League of Legends not installed](https://i.imgur.com/BNn7yXP.png)
![Image of the Launcher, with League of Legends installed](https://i.imgur.com/31YwpS0.png)

## Requirements:


Python 3, with the following pip plugins:

'configparser, pathlib, wget, os, subprocess, gi'

For Legends of Runeterra wine-staing 6.17 is also required (only tested working version so far).

## Features:
The script features automatic detection of a pre-existing Lutris installation for League of Legends and is able to use it as a base (detection for LORE is yet to be done).

## Usage
You can download this script and then unpack it, make sure you extract "lol-launchhelper.sh" and "main.py" into the same directory.
After that make the script executable via "chmod +x main.py" and then execute it via "./main.py".

### INSTALLING LEAGUE:

Select "League of Legends" in the top level bar and click on Install. The UI will freeze now, don't worry and wait. Once it unfreezes you should see the Riot launcher popping up shortly after. Let it download fully and then close it.

### LAUNCHING LEAGUE:

Select "League of Legends" in the top level bar and click on Launch. Only close the rito-launcher, once the LeagueClient has opened, otherwise the launchhelper script will terminate and League won't start.

### INSTALLING LORE:

Select "Legends of Runeterra" in the top level bar and click on Install. Make sure you have the prequesites installed and then it should launch.

### LAUNCHING RUNETERRA:

Select ... (okay I guess it should be self explainatory at this point. As a note, the launcher is programmed to close after launching runeterra.

INSTALLING VALORANT:

This isn't possible for now, and sadly I have no knowledge of the required dark magic to make it happen.

CHANGING LOCALE:

The launcher displays the news sites for LoL, LORE and Valorant in the language en-gb, to change it navigate to $HOME/.config/rito-launcher/launcher.cfg and change `locale = en-gb` the desired locale, for example english us (locale = en-us). The launcher.cfg is generated after first start.

