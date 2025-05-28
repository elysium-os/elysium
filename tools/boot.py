#!/usr/bin/env python3

import argparse
import os
from os.path import abspath, dirname
import subprocess
import sys

sys.dont_write_bytecode = True
import chariot_utils

# Parse CLI
parser = argparse.ArgumentParser(prog="boot.py")
parser.add_argument("--efi", action="store_true")
parser.add_argument("-t", "--buildtype", default="debug", choices=["debug", "release"])
parser.add_argument("--accel", default="kvm", choices=["kvm", "tcg"])
parser.add_argument("--debug", action="store_true")
parser.add_argument("-d", "--display", default="default", choices=["default", "headless", "vnc"])
parser.add_argument("-n", "--cores", type=int, default=4)
parser.add_argument("--gdb", action="store_true")
parser.add_argument("--tcg", action="store_const", const="tcg", dest="accel")
parser.add_argument("--headless", action="store_const", const="headless", dest="display")

args = parser.parse_args()

chariot_opts = ["--option", f"buildtype={args.buildtype}"]

# Build cronus & image
recipes = [
    "source/cronus",
    "package/cronus",
    "package/modules",
    "custom/image",
]

if chariot_utils.build(recipes).returncode != 0:
    print("Build failed, not running qemu")
    exit(1)

# Run QEMU
image_path = os.path.join(chariot_utils.path("custom/image", chariot_opts), "elysium_efi.img" if args.efi else "elysium_bios.img")

qemu_args = ["qemu-ovmf-x86-64" if args.efi else "qemu-system-x86_64"]
qemu_args.extend(["-drive", f"format=raw,file={image_path}"])

qemu_args.extend(["-m", "512M"])
qemu_args.extend(["-machine", "q35"])
qemu_args.extend(["-cpu", "qemu64,+pdpe1gb,+invtsc,+pcid"])
qemu_args.extend(["-vga", "virtio"])
qemu_args.extend(["-smp", f"cores={args.cores}"])
qemu_args.extend(["-net", "none"])

if args.display == "default":
    qemu_args.extend(["-display", "gtk,zoom-to-fit=on,show-tabs=on,gl=on"])
elif args.display == "vnc":
    qemu_args.extend(["-vnc", ":0,websocket=on"])
elif args.display == "headless":
    qemu_args.extend(["-display", "none"])

qemu_args.extend(["-accel", args.accel])
qemu_args.extend(["-M", "smm=off"])
qemu_args.extend(["-k", "en-us"])

qemu_args.extend(["-d", "int,fpu,guest_errors"])
qemu_args.extend(["-D", "./log.txt"])
qemu_args.extend(["-monitor", "stdio"])
qemu_args.extend(["-debugcon", "file:/dev/stdout"])
if args.debug or args.gdb:
    qemu_args.extend(["-s", "-S"])

qemu_args.append("-no-reboot")
qemu_args.append("-no-shutdown")

try:
    subprocess.run(qemu_args)
except KeyboardInterrupt:
    pass
