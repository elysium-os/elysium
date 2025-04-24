#!/usr/bin/env nix
#! nix shell github:elysium-os/chariot nixpkgs#wget nixpkgs#libarchive nixpkgs#python3 --command python3

import sys
import os
from os.path import dirname, abspath
import subprocess
import tomllib

project_path = dirname(dirname(abspath(__file__)))
recipe_source_path = os.getcwd()

config_path = None
for dirpath, dirnames, filenames in os.walk(recipe_source_path):
    for filename in filenames:
        if filename == "chariot_clangd.toml":
            config_path = os.path.join(dirpath, filename)

if config_path == None:
    print("no chariot_clangd.toml config found")
    exit(1)

config = tomllib.load(open(config_path, "rb"))

mappings = [
    f"{recipe_source_path}=$SOURCES_DIR/{config["source"]}"
]

result = subprocess.run([
    "chariot",
    "--config", project_path + "/config.chariot",
    "--no-lockfile",
    "exec", "--rw",
    "--recipe-context", config["recipe"],
    "-p", "clangd",
    "-e", "HOME=/root/clangd",
    "-e", "XDG_CACHE_HOME=/root/clangd/cache",
    f"clangd --background-index --clang-tidy --header-insertion=never --path-mappings {",".join(mappings)}"
])
