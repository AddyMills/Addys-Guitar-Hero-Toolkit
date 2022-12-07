# SKA Switcher

Submodule of Guitar Hero III Tools designed also as a standalone script.

Usage: Run the script with a ska file from GH3, GHA, or WT (PC only, and GH3 360 DLC works too) and a target.

The target is the intended model you want the lipsync to work on.

Allowable targets are:
*  gh3_singer
*  gh3_guitarist
*  gha_singer
*  gha_guitarist
*  dmc
*  steve
*  wt_singer

Files are saved in a folder called "ska_converts". This folder is located where your ska file is.

Example: ska_switcher.py GH3_Singer_Male_MyCurse_1.ska.xen steve

This will re-create the ska file to work with GH:A's Steven Tyler model.

You can also create a folder called "in" next to your scripts, and put all your ska files in there. Then run ska_switcher.py with your intended game target and all files will be converted to it.

Example: ska_switcher.py wt_singer

This will convert all files to World Tour's ska format.

The files will be in a folder called "out". Just be careful with this function as *all* files will be converted. If you are planning to convert to GH3 or GHA, please make sure to convert the guitarist's lipsync to the gh3_guitarist or gha_guitarist target.