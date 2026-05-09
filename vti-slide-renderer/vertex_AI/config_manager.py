import configparser
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.ini")


def _load() -> configparser.ConfigParser:
    cp = configparser.ConfigParser()
    cp.read(CONFIG_PATH, encoding="utf-8")
    return cp


def _save(cp: configparser.ConfigParser) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        cp.write(f)


def get_region() -> tuple[int, int, int, int] | None:
    cp = _load()
    raw = cp.get("capture", "region", fallback="").strip()
    if not raw:
        return None
    parts = [p.strip() for p in raw.split(",")]
    if len(parts) != 4:
        return None
    try:
        x, y, w, h = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
        return (x, y, w, h)
    except ValueError:
        return None


def set_region(x: int, y: int, w: int, h: int) -> None:
    cp = _load()
    if "capture" not in cp:
        cp["capture"] = {}
    cp["capture"]["region"] = f"{x},{y},{w},{h}"
    _save(cp)


def get_standby_sec() -> float:
    cp = _load()
    return cp.getfloat("capture", "standby_sec", fallback=5.0)


def get_interval() -> float:
    cp = _load()
    return cp.getfloat("capture", "interval_sec", fallback=3.0)


def get_total_shots() -> int:
    cp = _load()
    return cp.getint("capture", "total_shots", fallback=200)


def get_output_path() -> str:
    cp = _load()
    path = cp.get("output", "file_path", fallback="output.md")
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(__file__), path)
    return path


def get_next_button() -> tuple[int, int] | None:
    cp = _load()
    try:
        x = cp.getint("button", "next_x")
        y = cp.getint("button", "next_y")
        return (x, y)
    except Exception:
        return None


def set_next_button(x: int, y: int) -> None:
    cp = _load()
    if "button" not in cp:
        cp["button"] = {}
    cp["button"]["next_x"] = str(x)
    cp["button"]["next_y"] = str(y)
    _save(cp)


def get_button_label() -> str:
    cp = _load()
    return cp.get("button", "next_label", fallback="").strip()


def get_button_template() -> str | None:
    cp = _load()
    path = cp.get("button", "next_template", fallback="").strip()
    if not path:
        return None
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(__file__), path)
    return path


def set_button_template(path: str) -> None:
    cp = _load()
    if "button" not in cp:
        cp["button"] = {}
    rel = os.path.relpath(path, os.path.dirname(__file__))
    cp["button"]["next_template"] = rel
    _save(cp)


def get_button_search_ratio() -> float:
    cp = _load()
    return cp.getfloat("button", "search_region_ratio", fallback=0.4)


def get_auto_click() -> bool:
    cp = _load()
    return cp.getboolean("button", "auto_click", fallback=False)


def get_batch_size() -> int:
    cp = _load()
    return cp.getint("batch", "batch_size", fallback=15)


def get_screenshots_dir() -> str:
    cp = _load()
    path = cp.get("batch", "screenshots_dir", fallback="screenshots")
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(__file__), path)
    return path


def get_output_dir() -> str:
    cp = _load()
    path = cp.get("batch", "output_dir", fallback="output_ocr")
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(__file__), path)
    return path


# ---------------------------------------------------------------------------
# Vision API settings
# ---------------------------------------------------------------------------

def get_vision_enabled() -> bool:
    cp = _load()
    return cp.getboolean("vision", "enabled", fallback=False)


def get_vision_backend() -> str:
    """Return 'google_vision' or 'vertex_ai'."""
    cp = _load()
    return cp.get("vision", "backend", fallback="google_vision").strip().lower()


def get_vision_key_path() -> str:
    cp = _load()
    path = cp.get("vision", "key_file", fallback="CloudVisonViewer.json")
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(__file__), path)
    return path


def get_vision_filter_texts() -> list[str]:
    cp = _load()
    raw = cp.get("vision", "filter_texts", fallback="")
    return [t.strip() for t in raw.split(",") if t.strip()]


# ---------------------------------------------------------------------------
# Vertex AI settings
# ---------------------------------------------------------------------------

def get_vertexai_project() -> str:
    cp = _load()
    return cp.get("vertexai", "project_id", fallback="feednotebooklm").strip()


def get_vertexai_model() -> str:
    cp = _load()
    return cp.get("vertexai", "model", fallback="google/gemini-flash-lite-preview-06-17").strip()


def get_vertexai_fallback_model() -> str:
    cp = _load()
    return cp.get("vertexai", "fallback_model", fallback="google/gemini-2.5-flash-lite").strip()


def get_vertexai_regions() -> list[str]:
    """Return list of regions for round-robin rotation to avoid quota limits."""
    cp = _load()
    raw = cp.get("vertexai", "regions", fallback="us-central1")
    return [r.strip() for r in raw.split(",") if r.strip()]


# ---------------------------------------------------------------------------
# Skill settings
# ---------------------------------------------------------------------------

def get_auto_invoke_skill() -> bool:
    """Get auto-invoke skill setting (default: True)."""
    cp = _load()
    return cp.getboolean("skill", "auto_invoke", fallback=True)


# ---------------------------------------------------------------------------
# Slide designer settings
# ---------------------------------------------------------------------------

def get_slide_designer_model() -> str:
    cp = _load()
    return cp.get("slide_designer", "model", fallback="google/gemini-2.5-flash-lite").strip()


def get_slide_designer_fallback_model() -> str:
    cp = _load()
    return cp.get("slide_designer", "fallback_model", fallback="google/gemini-2.5-flash").strip()


def get_slide_designer_regions() -> list[str]:
    cp = _load()
    raw = cp.get("slide_designer", "regions", fallback="us-central1")
    return [r.strip() for r in raw.split(",") if r.strip()]
