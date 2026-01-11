import os
import subprocess


def config_path():
    """Get an absolute path pointing at the configuration"""
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "config.chariot"
    )


def path(recipe: str, options: list[str] | None = None):
    """Resolve an absolute path to the installation of the given recipe"""
    if options is None:
        options = []

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


def build(recipes: str, options: list[str] | None = None):
    """Build the given recipe"""
    if options is None:
        options = []

    return subprocess.run(
        ["chariot", "--config", config_path(), *options, "build", *recipes]
    )
