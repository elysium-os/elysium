#!/usr/bin/env -S python3 -B

import os
import subprocess
import sys

import chariot_utils

if len(sys.argv) < 2:
    print("Usage: dump.py <address>")
    sys.exit(1)

start_address = int(sys.argv[1], 16)
end_address = start_address + 128

subprocess.run(
    [
        "objdump",
        os.path.join(chariot_utils.path("package/cronus"), "sys/kernel.elf"),
        "-d",
        "-wrC",
        "--visualize-jumps=color",
        "--disassembler-color=on",
        f"--start-address={hex(start_address)}",
        f"--stop-address={hex(end_address)}",
    ]
)
