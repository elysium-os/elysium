#!/usr/bin/env -S python3 -B

import os

import chariot_utils

os.execvp(
    "gdb",
    [
        "--symbols",
        os.path.join(chariot_utils.path("package/cronus"), "sys/kernel.elf"),
        "-ex",
        "target remote :1234",
        "-ex",
        f'set substitute-path "../sources/cronus" "{chariot_utils.path("source/cronus")}"',
    ],
)
