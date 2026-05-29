import sys
from pathlib import Path
import os

APP_NAME = "convert-exam-notes"

def parse_subjects(text: str) -> dict[str, list[str]]:
    result = {}
    current = None

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
            result[current] = []
            continue

        if current is None:
            raise ValueError(f"Value outside section: {line!r}")

        result[current].append(line)

    return result

def subjects_dict_to_lists(x: dict[str, list[str]]) -> tuple[list[str], list[str]]:
    return list(x.keys()), [item for sublist in x.values() for item in sublist]

def create_toml_config(subjects: dict[str, list[str]]) -> list[dict]:
    final = []
    for key in subjects.keys():
        final.append({
            "name": key,
            "items": subjects[key],
            "anki-deckname": key.replace(" ", "") # TODO: More sanitization
        })

    return final

def toml_config_to_subject_lists(config: dict):
    possible_subjects: list[str] = []
    possible_areas: list[str] = []

    for subject in config["subject"]:
        possible_areas.append(subject["name"])
        possible_subjects.extend(subject["items"])

    return possible_areas, possible_subjects


## TODO: Change to https://github.com/tox-dev/platformdirs
# Claude generated
def get_config_dir(app_name: str = APP_NAME) -> Path:
    """
    Return the platform-appropriate config *directory* for *app_name*.

    The directory is not created by this function — call
    ``path.mkdir(parents=True, exist_ok=True)`` yourself, or use
    :func:`write_config` which does it automatically.
    """
    if sys.platform == "win32":
        # Prefer the roaming AppData folder; fall back gracefully if the
        # environment variable is missing (rare, but possible in containers).
        base = Path(
            os.environ.get("APPDATA")
            or Path.home() / "AppData" / "Roaming"
        )

    elif sys.platform == "darwin":
        # Apple's recommended location for app support files.
        base = Path.home() / "Library" / "Application Support"

    else:
        # Linux / other POSIX: honour $XDG_CONFIG_HOME (must be absolute),
        # falling back to the XDG default of ~/.config.
        xdg = os.environ.get("XDG_CONFIG_HOME", "").strip()
        base = Path(xdg) if (xdg and Path(xdg).is_absolute()) else Path.home() / ".config"

    return base / app_name
