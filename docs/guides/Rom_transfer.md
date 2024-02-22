# Transferring Roms to IVistation

## Quick Start

Before transferring roms to IVistation, perhaps it would be a good idea to check the 
[supported file formats per emulated system table](../Extensions.tsv) to know what type of roms are supported by
IVistation per system. Roms are placed in a sub-folder located at `ivistation\roms`, the folder will be called by the
"System ID" (refer to the table, again). So, for example, NES (Nintendo Entertainment System) roms are placed in
`ivistation\roms\nes`, and `.nes` is the supported format for this system.

After transferring the roms, boot IVistation up and run the scanner by pressing **START** at the main menu and
selecting "SCANNER".

## How To:

Before starting, make sure to run IVistation at least once after installing it, so the appropriate folders will be
created.

IVistation will create the corresponding folders for each system inside `ivistation\roms` sub-folder. These folders
are named after the "System ID" IVistation uses internally, which is usually the initials for a system, or the
short-form nickname the overall community widely refers to a system as, like "nes" for "Nintendo Entertainment System".

```bash
.
└── ivistation/
    └── roms/
        ├── nes/
        ├── snes/
        ├── gb/
        ├── gbc/
        ├── gba/
        ├── n64/
        ├── xbox/
        └── ...
```

Before transferring your roms, keep in mind that every system has a unique list of file extensions that they accept for
roms. This is usually not a problem, as IVistation is capable of using the most common formats for every system, but
it may be worth to keep in mind for some very gimmicky systems. For a full list of these extensions, see the
[supported file formats per emulated system table](../Extensions.tsv).

Now that the target folder has been identified, transfer your games to it. After you are done, it should look like this
example:

```bash
.
└── ivistation/
    └── roms/
        └── nes/
            ├── Contra.nes
            ├── Mega Man 2.nes
            ├── Super Mario Bros.nes
            ├── Qix.nes
            └── ...
```

Finally, to get your roms recognized in IVistation, you need to scan them. To do this, start IVistation up in your Xbox,
wait for the main menu to come up, and press the **START** button to bring up the settings menu. Here, navigate to
**"SCANNER"**. Here you will be faced with two choices; running an auto scan, or a manual scan:

- ### Auto scan:
    Will scan each system sequentially, even if nothing has changed for other systems. It will do this until every 
    single system has been scanned for roms. This is useful if you have transferred a pretty big amount of roms to
    IVistation covering multiple systems, as it will take care of all the scanning for you. Nonetheless, it may be a bad
    idea to use this option when you have transferred just a couple roms.
- ### Manual scan:
    Allows for the user to select what individual system they want to scan games for. This is usually the fastest way
    to add a couple roms, or to update your library if it is already huge.

The scanning process consists of multiple steps taken by IVistation to integrate the roms into a playlist for every
system. This includes, but is not limited to:

- Calculating rom fingerprints
- Identifying the rom
- Renaming the rom
- Downloading box art (if available) (requires an internet connection)
- Removing invalid files (or corrupt roms)
- Looking for the rom synopsis

After this process is done, the carousel (main menu) will be refreshed, and you will be able to play your games,
if you have the right core for them. To know what cores are built into IVistation by default, and what cores
are available for download, check the [supported cores per system table](../Cores.tsv).

Keep in mind that IVistation is *never* officially bundled with any copyrighted games, and you need to bring your own
roms. IVistation also does not condone piracy, and thus recommends making your own copy of the roms you own.

Nonetheless, from a retro enthusiast (myself as astarivi) to another (you), I recommend seeking the cleanest
possible copies for every game, as doing this will result in IVistation correctly identifying the rom, thus enabling
for cover images downloads, and even the game synopsis to appear.

## Quirks:
 - By default, no roms folders exist until IVistation is first run, where they will be created.
 - Zipped roms are not supported (yet).
 - Any roms transferred to IVistation will be renamed, and sometimes even deleted if they're deemed invalid.
 - To create game folders for newer systems introduced through updates, refresh the carousel.
