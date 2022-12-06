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