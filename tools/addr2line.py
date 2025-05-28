#!/usr/bin/env python3

import os
import subprocess
import sys

sys.dont_write_bytecode = True
import chariot_utils

if len(sys.argv) < 2:
    print("Usage: addr2line.py <address>")
    sys.exit(1)

address = int(sys.argv[1], 16)

subprocess.run([
    "addr2line", "-fai",
    "-e", os.path.join(chariot_utils.path("package/cronus"), "sys/kernel.elf"),
    hex(address)
])
