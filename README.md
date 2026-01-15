# Airport Optimiser

Script to remove vehicles from X-Plane scenery.

**⚠️ Important**

The version of Airport Optimiser originally posted on X-Plane.org is unsupported. Numerous requests have been made for it to be removed but all have been ignored. The only official release and updates are available via this GitHub repository. Files elsewhere are stale, may crash your simulator, and are not maintained.

## Features
    
* Removes airport ground vehicles and/or world scenery vehicles, potentially improving FPS by around 3-4 (your mileage will vary)
* Backs up the relevant files automatically before making changes, and can restore them at a later date
* Efficiently edits large files that are otherwise impossible to manage in a normal text editor
* Doesn't impact BetterPushback (effects on other addons are untested)
* Works with any version of X-Plane, unlike pre-packaged `apt.dat` scripts out there (just re-run if you update the sim)

## Usage

1. Drag the script into your root X-Plane folder
2. Open a terminal (cd into the X-Plane folder) and run: `python air_opt.py -g -w` (or `python3`, depending on your setup)

## Configuration

`-g` removes airport ground vehicles

`-w` disables world scenery vehicles

`-r` restores files (when used in conjunction with the appropriate flag(s) above)

`-d` performs a dry run

`-f` uses force mode (modifies a file that is already modified; not recommended)

## Disclaimer

This is a personal utility I use myself, provided here as-is, with no warranty. Use at your own risk.
