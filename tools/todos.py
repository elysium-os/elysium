#!/usr/bin/env python3

import os
import sys
import re
import subprocess

sys.dont_write_bytecode = True
import chariot_utils

if chariot_utils.build(["source/cronus"]).returncode != 0:
    print("Failed to update cronus source, exiting")
    exit(1)

source_dir = chariot_utils.path("source/cronus")
source_dirs = [os.path.join(source_dir, "kernel/"), os.path.join(source_dir, "modules/")]

def find_tags(tag, color):
    tags = []
    for dir in source_dirs:
        for root, dirs, files in os.walk(dir):
            for file in files:
                if file.endswith(".c") or file.endswith(".h"):
                    fullpath = os.path.join(root, file)
                    with open(fullpath, "r") as f:
                        for i, line in enumerate(f):
                            match = re.search(f"(\\/\\/|\\*|@|;) *{tag}:? *(.*)", line)
                            if match != None:
                                tags.append({ "tag": tag, "color": color, "path": fullpath.split("source/cronus/src/")[1], "line": i, "value": match.group(2) })
                                break
    return tags

tags = []
tags += find_tags("TODO", 33)
tags += find_tags("todo", 33)
tags += find_tags("OPTIMIZE", 36)
tags += find_tags("UNIMPLEMENTED", 35)
tags += find_tags("CRITICAL", 31)
tags += find_tags("FIX", 91)
tags += find_tags("TEMPORARY", 32)
tags += find_tags("NOTE", 37)
tags += find_tags("FLIMSY", 90)

for tag in tags:
    print(f"\033[{tag["color"]}m[{tag["tag"]}] {tag["path"]}:{tag["line"]}\033[0m {tag["value"]}")
