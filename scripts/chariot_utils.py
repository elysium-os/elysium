import os
import subprocess


def config_path():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "config.chariot")


def path(recipe, options=[]):
    result = subprocess.run(
        ["chariot", "--config", config_path(), *options, "path", recipe],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("chariot path failed")
        print(result.stderr)
        exit(1)

    return result.stdout


def build(recipes, options=[]):
    return subprocess.run(["chariot", "--config", config_path(), *options, "build", *recipes])
