# IVistation Features

IVistation is technically a dashboard, and thus contains many features. As some of these are somewhat hidden, or require
some tinkering to get working, here is a list of what IVistation is capable of. (These brief descriptions are
found in their respective guide pages, too)

## Features:

* ### [Rom parser (scanner)](Rom_transfer.md)
    Parse (scan) the roms you transfer to have them recognized by IVistation. Scanning roms is a process that involves
    identifying the rom by comparing its fingerprint with a known base of roms for each system, thus identifying
    characteristics such as the official title, synopsis, and even the boxart at times.
    * ### Rom renaming
        Roms are automatically renamed to their official title if found, otherwise, their filename will be cleaned
        to avoid issues.
    * ### Rom synopsis
        IVistation contains some synopsis databases for certain systems (which can change via updates), which are
        automatically added to the listing for your rom. Currently, there's no way to disable this.
    * ### Rom boxart
        For certain select systems, IVistation contains a base of downloadable boxart. This feature needs an internet
        connection. Enabled by default. Can be disabled from `SCANNER -> AUTOMATIC BOXART DOWNLOADS`

* ### Emulation cores
    In IVistation, emulation cores are closely related to their RetroArch definition. They are emulators that can be
    configured, or swapped, before launching a game. Depending on the emulator, they may have different configuration
    options and types. Some of the most notable are:

    * Display resolution
    * Software filter
    * Hardware filter
    * Reset settings to defaults
    * Remove all data

    These options are accessible via the `CONFIGURE SYSTEM` section, found by pressing `Y` over a system icon in the
    home menu, or inside the rom listings for a system.

    **A single system may have multiple cores to select from. More cores can be obtained from the Downloader.**
 
* ### Builtin updater
    IVistation can update itself, given an internet connection and access to the Downloader. Updates may be large, as
    the update file may include files that have not changed. Keep in mind that, while updating IVistation, it's critical
    to **never** power off the console until the update is done. Failure to do so may result in corrupting IVistation.

* ### Downloader
    Bundled with IVistation is a downloader, accessible via `MAIN MENU -> XBMC OPTIONS -> DOWNLOADER`. This downloader
    is different to the one found in XBMC-Emustation or any other Rocky5 project, as it fetches the downloads library
    dynamically, on the fly. This means that the downloader has no need to update itself to change the items it offers
    for download. Although, at times, it may need to update itself to upgrade certain install behaviours. Things found
    in the downloader vary, some of them are:
    * Emulation cores
    * Applications
    * Homebrew

* ### XISO Xbox games support
    XISO Xbox games can be parsed by using the scanner. This requires an up-to-date softmod, or a hardmod and a bios
    that supports this. To use this feature, locate your Xbox games folder, usually a `Games` folder at the root
    of a drive, like `E:\Games`, and create a folder related to the title of your game, ex: `E:\Games\Halo`, place
    your XISO files there, then run the scanner. A separate folder is needed for each game.

    **Note: Xbox games are considered as roms by IVistation.**

* ### Dashboard features
    IVistation has dashboard-like features, most inherited from XBMC-Emustation and XBMC itself. Some of the most
    notable are:
    * FTP server (user: xbox, pass: xbox)
    * File explorer
    * DVD launcher
    * XBE launcher
    * 720p, 480p and 480i resolution support
    * Games, homebrew, and applications local search
    * Console settings (such as display, network, sound, fan speed, etc.)

## Quirks:

* Xbox games are considered roms
* Homebrew are considered roms
* Emulators can not be manually added
