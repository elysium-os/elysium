#!/usr/bin/env -S python3 -B

import os
import subprocess
import sys

import chariot_utils

if len(sys.argv) < 2:
    print("Usage: addr2line.py <address>")
    sys.exit(1)

address = int(sys.argv[1], 16)

subprocess.run(
    [
        "addr2line",
        "-fai",
        "-e",
        os.path.join(chariot_utils.path("package/cronus"), "sys/kernel.elf"),
        hex(address),
    ]
)
