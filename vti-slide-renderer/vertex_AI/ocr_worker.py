import os
import queue
import re
import threading

import numpy as np
import pytesseract
from PIL import Image, ImageFilter

if os.name == "nt":
    _TESS_DEFAULT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.isfile(_TESS_DEFAULT):
        pytesseract.pytesseract.tesseract_cmd = _TESS_DEFAULT

# Option B: PSM 4 — single column, variable text sizes (better for quiz layout)
_TESS_CONFIG = "--psm 4 --oem 1"
_TESS_LANG = "jpn+eng"

_RADIO_RE = re.compile(r"^[\d\s○oO。×\-]+$")

# Option A: post-processing correction table for systematic Tesseract misreads
# Pattern: (regex_to_find, replacement)
# Rules are applied in order; most specific first.
_POSTPROC_RULES: list[tuple[re.Pattern, str]] = [
    # （ア）/（イ）/（ウ） misread as numbers inside parentheses
    (re.compile(r"\(7{1,2}\)"), "（ア）"),
    (re.compile(r"\(T\)"),      "（ア）"),
    (re.compile(r"\(1\)"),      "（イ）"),
    (re.compile(r"\(\|\)"),     "（イ）"),
    (re.compile(r"\(l\)"),      "（イ）"),
    (re.compile(r"\(0\)"),      "（ウ）"),
    (re.compile(r"\(o\)"),      "（ウ）"),
    # 和勾配 → 勾配  (extra 和 prepended to 勾 stroke split)
    (re.compile(r"和勾配"),     "勾配"),
    # 届 → 層  (consistent misread in "次の層との間")
    (re.compile(r"次の届との"),  "次の層との"),
]


_DARK_BLUR_RADIUS = 30
_DARK_THRESHOLD = 100


def _mask_dark_regions(gray: np.ndarray) -> np.ndarray:
    # Blur heavily to detect dark background regions (not individual dark pixels like text)
    blurred = np.array(
        Image.fromarray(gray).filter(ImageFilter.GaussianBlur(radius=_DARK_BLUR_RADIUS))
    )
    # Pixels in dark-background regions → set to 255 so OCR ignores them
    masked = gray.copy()
    masked[blurred < _DARK_THRESHOLD] = 255
    return masked


def _preprocess(image: Image.Image) -> Image.Image:
    # Option C: Otsu adaptive binarization instead of linear contrast enhance
    w, h = image.size
    img = image.resize((w * 2, h * 2), Image.LANCZOS)
    gray = np.array(img.convert("L"), dtype=np.uint8)

    gray = _mask_dark_regions(gray)

    # Otsu threshold: compute optimal global threshold
    hist, _ = np.histogram(gray.ravel(), bins=256, range=(0, 256))
    total = gray.size
    sum_total = np.dot(np.arange(256), hist)
    sum_b = 0.0
    w_b = 0
    best_thresh = 0
    best_var = 0.0
    for t in range(256):
        w_b += hist[t]
        if w_b == 0:
            continue
        w_f = total - w_b
        if w_f == 0:
            break
        sum_b += t * hist[t]
        m_b = sum_b / w_b
        m_f = (sum_total - sum_b) / w_f
        var = w_b * w_f * (m_b - m_f) ** 2
        if var > best_var:
            best_var = var
            best_thresh = t

    binary = np.where(gray > best_thresh, 255, 0).astype(np.uint8)
    img = Image.fromarray(binary, mode="L")
    img = img.filter(ImageFilter.SHARPEN)
    return img


def _postprocess(text: str) -> str:
    for pattern, replacement in _POSTPROC_RULES:
        text = pattern.sub(replacement, text)
    return text


def _filter(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if _RADIO_RE.match(stripped) and len(stripped) <= 15:
            continue
        lines.append(stripped)
    return "\n".join(lines)


def _ocr(image: Image.Image) -> str:
    img = _preprocess(image)
    raw = pytesseract.image_to_string(img, lang=_TESS_LANG, config=_TESS_CONFIG)
    filtered = _filter(raw)
    return _postprocess(filtered)


def _worker_loop(
    task_queue: queue.Queue,
    results_dict: dict,
    lock: threading.Lock,
) -> None:
    while True:
        try:
            item = task_queue.get(block=True, timeout=1.0)
        except queue.Empty:
            continue

        if item is None:
            task_queue.task_done()
            break

        filename, pil_image = item
        try:
            text = _ocr(pil_image)
        except Exception as e:
            text = f"[OCR error: {e}]"

        with lock:
            results_dict[filename] = text

        preview = text[:80].replace("\n", " / ")
        task_queue.task_done()


def start_worker(
    task_queue: queue.Queue,
    results_dict: dict,
    lock: threading.Lock,
    **_kwargs,
) -> threading.Thread:
    t = threading.Thread(
        target=_worker_loop,
        args=(task_queue, results_dict, lock),
        daemon=True,
    )
    t.start()
    return t


def wait_until_done(task_queue: queue.Queue) -> None:
    task_queue.join()
