import os
import subprocess
import sys

def chariot_path(recipe, options=[]):
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "config.chariot")

    result = subprocess.run([
        "chariot",
        "--config", config_path,
        *options,
        "path", recipe
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print("chariot path failed")
        print(result.stderr)
        exit(1)

    return result.stdout
