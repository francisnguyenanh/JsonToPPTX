"""
OCR worker supporting two backends:
  1. Google Cloud Vision  (backend = google_vision)
  2. Vertex AI / Gemini   (backend = vertex_ai)

Vertex AI uses google-cloud-aiplatform to call Gemini models via the
generateContent REST endpoint.  To avoid per-minute quota limits the
worker rotates across multiple GCP regions (round-robin).

Features:
- Sequential processing (one image at a time to respect API rate limits)
- Tracks processed filenames in screenshots/.vision_done.json to avoid re-sending
- Filters out configured button label texts before writing results
- Falls back gracefully if required libraries are not installed
"""

import base64
import io
import json
import os
import queue
import re
import threading
import time

from PIL import Image

try:
    from google.cloud import vision
    from google.oauth2 import service_account
    _VISION_AVAILABLE = True
except ImportError:
    _VISION_AVAILABLE = False

try:
    import google.auth
    import google.auth.transport.requests
    _AIPLATFORM_AVAILABLE = True
except ImportError:
    _AIPLATFORM_AVAILABLE = False

try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

import urllib.request
import urllib.error

_PROGRESS_FILENAME = ".vision_done.json"


# ---------------------------------------------------------------------------
# Progress tracking
# ---------------------------------------------------------------------------

def _load_progress(screenshots_dir: str) -> set[str]:
    path = os.path.join(screenshots_dir, _PROGRESS_FILENAME)
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Filter to keep only string items (discard old int indices from previous runs)
                return set(item for item in data if isinstance(item, str))
        except Exception:
            pass
    return set()


def _save_progress(screenshots_dir: str, done: set[str]) -> None:
    path = os.path.join(screenshots_dir, _PROGRESS_FILENAME)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sorted(done), f)


# ---------------------------------------------------------------------------
# Google Cloud Vision helpers
# ---------------------------------------------------------------------------

def _build_client(key_path: str):
    creds = service_account.Credentials.from_service_account_file(
        key_path,
        scopes=["https://www.googleapis.com/auth/cloud-vision"],
    )
    return vision.ImageAnnotatorClient(credentials=creds)


# ---------------------------------------------------------------------------
# Vertex AI / Gemini helpers
# ---------------------------------------------------------------------------

_VERTEX_PROMPT = (
    "This is a screenshot of a Japanese quiz/exam question. "
    "Extract ALL visible text and output it in this exact structure:\n"
    "1. First line MUST be the question counter shown in the top header (e.g. '問題 3 / 30'), "
    "formatted exactly as: [問題 X/Y] (e.g. [問題 3/30]). If not visible, write [問題 ?/?].\n"
    "2. Question text (問題文) — output as-is on one or more lines\n"
    "3. One blank line\n"
    "4. Each answer option on its own line, prefixed with A. B. C. D. E. in order\n"
    "If the original already has markers (○, □, ①②③, ア., A., 1. etc.), replace them with A. B. C. D. in order.\n"
    "Output ONLY the extracted text, no commentary or markdown."
)

_Q_HEADER_RE = re.compile(r'^\[問題\s*(\d+)/(\d+)\]')


class _VertexAIClient:
    """Thin wrapper around the Vertex AI generateContent REST API with region rotation."""

    _ENDPOINT_TMPL = (
        "https://{region}-aiplatform.googleapis.com/v1/projects/{project}/"
        "locations/{region}/publishers/google/models/{model}:generateContent"
    )

    def __init__(self, project: str, model: str, regions: list[str], fallback_model: str = "", key_path: str = ""):
        self.project = project
        # Strip 'google/' prefix for the URL path (publisher is already set)
        self.model = model.replace("google/", "", 1) if "/" in model else model
        self.fallback_model = fallback_model.replace("google/", "", 1) if fallback_model and "/" in fallback_model else fallback_model
        self.regions = list(regions) if regions else ["us-central1"]
        self.key_path = key_path
        self._region_idx = 0
        self._creds = None
        self._lock = threading.Lock()

    def _get_creds(self):
        """Return valid Application Default Credentials (ADC), refreshing if needed."""
        if self._creds is None:
            if self.key_path and os.path.exists(self.key_path):
                from google.oauth2 import service_account
                self._creds = service_account.Credentials.from_service_account_file(
                    self.key_path,
                    scopes=["https://www.googleapis.com/auth/cloud-platform"],
                )
            else:
                self._creds, _ = google.auth.default(
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
        if not self._creds.valid:
            req = google.auth.transport.requests.Request()
            self._creds.refresh(req)
        return self._creds

    def _current_region(self) -> str:
        with self._lock:
            return self.regions[self._region_idx % len(self.regions)]

    def _rotate_region(self) -> str:
        """Advance to the next region and return it."""
        with self._lock:
            self._region_idx = (self._region_idx + 1) % len(self.regions)
            new = self.regions[self._region_idx]
        print(f"[VertexAI] Rotating to region: {new}")
        return new

    def generate_content(self, pil_image: Image.Image, max_retries: int = 3) -> str:
        """Send image to Vertex AI generateContent, rotating regions on quota errors."""
        # Encode image to base64 PNG
        buf = io.BytesIO()
        pil_image.save(buf, format="PNG")
        b64_data = base64.b64encode(buf.getvalue()).decode("ascii")

        payload = json.dumps({
            "contents": [{
                "role": "user",
                "parts": [
                    {"text": _VERTEX_PROMPT},
                    {"inline_data": {"mime_type": "image/png", "data": b64_data}},
                ],
            }],
            "generation_config": {
                "temperature": 0.0,
                "max_output_tokens": 2048,
            },
        }).encode("utf-8")

        last_error = None
        for attempt in range(max_retries * len(self.regions)):
            region = self._current_region()
            url = self._ENDPOINT_TMPL.format(
                region=region, project=self.project, model=self.model
            )

            try:
                creds = self._get_creds()
                token = creds.token
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                }

                req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=60) as resp:
                    body = json.loads(resp.read().decode("utf-8"))

                # Parse response
                try:
                    return body["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError) as e:
                    raise RuntimeError(f"Unexpected response shape: {body}") from e

            except urllib.error.HTTPError as e:
                status = e.code
                err_body = e.read().decode("utf-8", errors="replace")
                last_error = f"HTTP {status}: {err_body[:200]}"

                if status in (429, 503):  # quota / service unavailable → rotate region
                    print(f"[VertexAI] Quota/busy on {region} (HTTP {status}). "
                          f"Attempt {attempt + 1} — rotating region...")
                    self._rotate_region()
                    time.sleep(2 ** min(attempt, 4))  # exponential back-off, max 16s
                    continue

                if status in (404, 400):
                    if self.fallback_model and self.model != self.fallback_model:
                        print(f"[VertexAI] Model API error on {region} (HTTP {status}). "
                              f"Switching to fallback model: {self.fallback_model}")
                        self.model = self.fallback_model
                        self._rotate_region()
                        time.sleep(1)
                        continue
                    else:
                        print(f"[VertexAI] Model {self.model} error on {region} (HTTP {status}). "
                              f"Attempt {attempt + 1} — rotating to next region...")
                        self._rotate_region()
                        time.sleep(1)
                        continue

                raise RuntimeError(last_error)

            except urllib.error.URLError as e:
                last_error = str(e)
                print(f"[VertexAI] Network error on {region}: {e} — rotating region...")
                self._rotate_region()
                time.sleep(2)
                continue

        raise RuntimeError(f"Vertex AI failed after {max_retries * len(self.regions)} attempts. "
                           f"Last error: {last_error}")


def _ocr_image_vertexai(client: _VertexAIClient, pil_image: Image.Image) -> str:
    """Send image to Vertex AI Gemini and return extracted text."""
    return client.generate_content(pil_image)


def _ocr_image(client, pil_image: Image.Image) -> str:
    """Send image to Cloud Vision document_text_detection.
    Uses paragraph bounding boxes to preserve visual layout (line breaks between
    question text and answer options) instead of just returning raw .text."""
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    content = buf.getvalue()

    image = vision.Image(content=content)
    image_context = vision.ImageContext(language_hints=["ja"])
    response = client.document_text_detection(image=image, image_context=image_context)

    if response.error.message:
        raise RuntimeError(response.error.message)

    if not response.full_text_annotation:
        return ""

    # Extract paragraphs grouped by block.
    # Preserving block boundaries is critical: Vision groups the question body
    # and each answer option into separate blocks (separated by the horizontal
    # divider line in the quiz UI).  Inserting a blank line between blocks lets
    # _format_quiz_text reliably distinguish question text from answer options.
    _LINE_Y_THRESHOLD = 15   # px — paragraphs within the same visual line
    _BLOCK_GAP_THRESHOLD = 8  # px — blocks closer than this are merged (rare)

    block_groups: list[list[tuple[int, int, str]]] = []  # list of blocks, each a list of (y, x, text)

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            paras_in_block: list[tuple[int, int, str]] = []
            for para in block.paragraphs:
                words = []
                for word in para.words:
                    word_text = "".join(s.text for s in word.symbols)
                    words.append(word_text)
                para_text = "".join(words)
                if not para_text.strip():
                    continue
                top_y = min(v.y for v in para.bounding_box.vertices)
                left_x = min(v.x for v in para.bounding_box.vertices)
                paras_in_block.append((top_y, left_x, para_text))
            if paras_in_block:
                block_groups.append(paras_in_block)

    # Sort blocks top→bottom by the minimum Y of their paragraphs
    block_groups.sort(key=lambda b: min(p[0] for p in b))

    def _paragraphs_to_lines(paras: list[tuple[int, int, str]]) -> list[str]:
        """Sort paragraphs by Y then X, group into visual lines."""
        paras_sorted = sorted(paras, key=lambda p: (p[0], p[1]))
        lines: list[str] = []
        current_line: list[tuple[int, str]] = []
        current_y = -9999
        for top_y, left_x, text in paras_sorted:
            if abs(top_y - current_y) > _LINE_Y_THRESHOLD:
                if current_line:
                    current_line.sort(key=lambda p: p[0])
                    lines.append("".join(t for _, t in current_line))
                current_line = [(left_x, text)]
                current_y = top_y
            else:
                current_line.append((left_x, text))
        if current_line:
            current_line.sort(key=lambda p: p[0])
            lines.append("".join(t for _, t in current_line))
        return lines

    # Build final text: blocks separated by blank lines (= structural boundary)
    block_texts: list[str] = []
    for block_paras in block_groups:
        block_line_list = _paragraphs_to_lines(block_paras)
        block_text = "\n".join(block_line_list).strip()
        if block_text:
            block_texts.append(block_text)

    return "\n\n".join(block_texts)


def _filter_text(text: str, filter_texts: list[str]) -> str:
    """Remove lines containing any of the button label strings.
    Preserves single empty lines (they separate question from options)."""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if filter_texts and any(ft in stripped for ft in filter_texts):
            continue
        lines.append(stripped)
    # Collapse 3+ consecutive empty lines into one
    result = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
    return result.strip()


# ---------------------------------------------------------------------------
# Quiz format post-processor
# ---------------------------------------------------------------------------

_QUESTION_END_RE = re.compile(
    r"[。？?]$"
    r"|か[。]?\s*$"                        # ～か、～か。
    r"|選べ\s*$"                            # ～選べ
    r"|答えよ\s*$"                          # ～答えよ
    r"|述べよ\s*$"                          # ～述べよ
    r"|なさい\s*$"                          # ～しなさい、選びなさい
    r"|せよ\s*$"                            # ～記述せよ
    r"|求めよ\s*$"
    r"|どれか\s*$"                          # ～はどれか
    r"|正しいか\s*$"                        # ～正しいか
    r"|誤りか\s*$"                          # ～誤りか
    r"|当てはまるものは\s*$"
    r"|適切(?:な|でない)ものは\s*$"
    r"|含まれ(?:る|ない)ものは\s*$"
    r"|てください\s*$"                  # 選択してください
)
_MARKER_RE = re.compile(
    r"^(?:"
    r"[○●◯□■☐☑◻▢〇]\s*"           # ○ □ 既存
    r"|[①②③④⑤⑥⑦⑧⑨⑩]\s*"         # 丸数字
    r"|[ア-オ][.．]\s*"                # カタカナ: ア. イ.（「、」は誤認識リスクあり）
    r"|[Ａ-Ｅa-eA-E][.．)）]\s*"       # 英字: A. B.（全角・半角）
    r"|[1-9][.．)）]\s*"               # 数字: 1. 2.
    r"|（[ア-オ1-9]）\s*"              # 括弧形式: （ア） （1）
    r")"
)
_JOUKI_RE = re.compile(r"上記の式|この式")
_ARTIFACT_RE = re.compile(r"^[Oo○OОＯ]{2,}$|^[☐]$")
_QUESTION_NUM_RE = re.compile(
    r"^(?:"
    r"問\s*[0-9０-９]+[.．]?\s*"       # 問1. 問２
    r"|【問[0-9０-９]+】\s*"            # 【問1】
    r"|Q[0-9]+[.．]?\s*"               # Q1. Q2
    r")"
)


def _looks_like_option_set(blocks: list[str]) -> bool:
    """Return True if blocks look like answer options.

    Criteria (all must pass):
    - 2–8 blocks (G検定 typically 4–5 options)
    - ≥60% of blocks are single-line (options are rarely multi-line)
    - Average char length ≤ 100 (options are concise)
    - Coefficient of variation (std/avg) < 0.7 (reasonably uniform length)
    """
    n = len(blocks)
    if not (2 <= n <= 8):
        return False
    single_line = sum(1 for b in blocks if len(b.splitlines()) == 1)
    if single_line / n < 0.6:
        return False
    lengths = [len(b.strip()) for b in blocks]
    avg = sum(lengths) / n
    if avg > 100 or avg == 0:
        return False
    std = (sum((l - avg) ** 2 for l in lengths) / n) ** 0.5
    return (std / avg) < 0.7


def _format_quiz_text(text: str) -> str:
    """Post-process OCR text into structured quiz format.

    Root problem: Vision OCR drops the ○ radio-button graphic on the FIRST
    option (and occasionally on all options).  We cannot rely on marker
    presence alone to separate question body from answer options.

    Algorithm:
      1. Split on ``\\n\\n`` (block boundaries from ``_ocr_image``).
      2. Find the first block whose first line starts with any option marker
         (○/□, ①②③, ア./イ., A./B., 1./2., （ア）) → ``first_marked_idx``.
         Everything before = *pre-marked*.
      3. In the pre-marked blocks, find the **last** block whose last
         non-empty line matches a question-end pattern (か/せよ/。/？)
         → ``last_q_idx``.
      4. ``blocks[0 .. last_q_idx]`` = question body.
      5. ``blocks(last_q_idx .. first_marked_idx)`` = *between* blocks:
         - If the marked options contain 「上記の式」/「この式」→ the
           between blocks are **formula** (part of the question body).
         - Else if between+marked blocks look like uniform short options
           → **missing-marker options**.
         - Otherwise → treated as question body continuation.
      6. ``blocks[first_marked_idx ..]`` = marked options.
      7. Strip all markers, determine ○ vs □, and re-add uniform markers.
    """
    raw_blocks = [b.strip() for b in re.split(r"\n\n+", text) if b.strip()]
    if not raw_blocks:
        return text

    # ── Step 1: find first block with a marker ────────────────────────────
    first_marked_idx = len(raw_blocks)
    for i, block in enumerate(raw_blocks):
        first_line = block.splitlines()[0].strip()
        if _MARKER_RE.match(first_line):
            first_marked_idx = i
            break

    pre_marked  = raw_blocks[:first_marked_idx]
    post_marked = raw_blocks[first_marked_idx:]

    # ── Step 2: in pre_marked, find LAST question-end block ───────────────
    last_q_idx = 0                       # default: at least the first block is question
    for i, block in enumerate(pre_marked):
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        # Check last 2 lines — final line may be a citation/note, not the question ending
        check_lines = lines[-2:] if len(lines) >= 2 else lines
        if any(_QUESTION_END_RE.search(l) for l in check_lines):
            last_q_idx = i

    question_blocks = list(pre_marked[:last_q_idx + 1])
    between_blocks  = list(pre_marked[last_q_idx + 1:])

    # ── Step 3: classify between_blocks ───────────────────────────────────
    has_jouki = any(
        _JOUKI_RE.search(_MARKER_RE.sub("", line))
        for block in post_marked
        for line in block.splitlines()
    )

    if has_jouki and between_blocks:
        # Formula / condition lines → part of question body
        question_blocks.extend(between_blocks)
        option_source = post_marked
    elif between_blocks and _looks_like_option_set(between_blocks + post_marked):
        # Missing-marker options (short, length-uniform blocks)
        option_source = between_blocks + post_marked
    elif between_blocks:
        # Ambiguous: treat as question body continuation
        question_blocks.extend(between_blocks)
        option_source = post_marked
    else:
        option_source = post_marked

    # ── Step 4: build question text ───────────────────────────────────────
    q_parts: list[str] = []
    for bi, block in enumerate(question_blocks):
        lines_out: list[str] = []
        for li, raw_line in enumerate(block.splitlines()):
            if not raw_line.strip():
                continue
            cl = _MARKER_RE.sub("", raw_line).strip()
            if bi == 0 and li == 0:
                cl = _QUESTION_NUM_RE.sub("", cl).strip()  # strip 問1. Q1. etc.
            if cl:
                lines_out.append(cl)
        if lines_out:
            q_parts.append("\n".join(lines_out))
    question_text = "\n".join(q_parts)

    # ── Step 5: collect and clean options ──────────────────────────────────
    option_lines: list[str] = []
    for block in option_source:
        for line in block.splitlines():
            cleaned = _MARKER_RE.sub("", line).strip()
            if not cleaned or _ARTIFACT_RE.match(cleaned):
                continue
            # Fix OCR artifact: ○ merged with first char ("OTransformer" → "Transformer")
            cleaned = re.sub(r"^[Oo○OОＯ]([A-Z\[（\u3041-\u9FFF])", r"\1", cleaned)
            # Split concatenated options (marker embedded mid-line, e.g. BERT①GPT②LSTM)
            sub_opts = re.split(
                r"(?<=[^\s○□①-⑩])\s*[○□①②③④⑤⑥⑦⑧⑨⑩]\s*(?=\S)",
                cleaned,
            )
            for opt in sub_opts:
                opt = opt.strip()
                if opt:
                    option_lines.append(opt)

    result: list[str] = [question_text, ""]
    for i, opt in enumerate(option_lines):
        result.append(f"{chr(ord('A') + i)}. {opt}")

    return "\n".join(result)


# ---------------------------------------------------------------------------
# Worker loop
# ---------------------------------------------------------------------------

def _drain_queue_on_error(task_queue: queue.Queue) -> None:
    """Drain remaining tasks from queue when worker cannot start."""
    while True:
        item = task_queue.get(block=True)
        task_queue.task_done()
        if item is None:
            break


def _worker_loop(
    task_queue: queue.Queue,
    results_dict: dict,
    lock: threading.Lock,
    key_path: str,
    filter_texts: list[str],
    screenshots_dir: str,
    backend: str = "google_vision",
    vertexai_project: str = "",
    vertexai_model: str = "",
    vertexai_fallback_model: str = "",
    vertexai_regions: list[str] = None,
    on_result=None,
) -> None:
    use_vertex = (backend == "vertex_ai")

    # ── Initialize backend client ────────────────────────────────────────────
    if use_vertex:
        if not _AIPLATFORM_AVAILABLE:
            print("[VisionWorker] google-auth not installed — cannot use Vertex AI backend.")
            _drain_queue_on_error(task_queue)
            return
        try:
            client = _VertexAIClient(
                project=vertexai_project,
                model=vertexai_model,
                regions=vertexai_regions or ["us-central1"],
                fallback_model=vertexai_fallback_model,
                key_path=key_path,
            )
            print(f"[VertexAI] Initialized. Project={vertexai_project}, "
                  f"Model={vertexai_model}, Fallback={vertexai_fallback_model}, "
                  f"Regions={client.regions}")
        except Exception as e:
            print(f"[VisionWorker] Cannot initialize Vertex AI client: {e}")
            _drain_queue_on_error(task_queue)
            return
    else:
        if not _VISION_AVAILABLE:
            print("[VisionWorker] google-cloud-vision not installed — skipping Vision OCR.")
            _drain_queue_on_error(task_queue)
            return
        try:
            client = _build_client(key_path)
        except Exception as e:
            print(f"[VisionWorker] Cannot initialize Google Vision client: {e}")
            _drain_queue_on_error(task_queue)
            return

    done_set = _load_progress(screenshots_dir)

    # ── Main processing loop ─────────────────────────────────────────────────
    while True:
        try:
            item = task_queue.get(block=True, timeout=1.0)
        except queue.Empty:
            continue

        if item is None:
            task_queue.task_done()
            break

        filename, pil_image = item

        if filename in done_set and on_result is None:
            print(f"[VisionWorker] {filename} already processed — skipping.")
            task_queue.task_done()
            continue

        try:
            if use_vertex:
                raw = _ocr_image_vertexai(client, pil_image)
                backend_tag = "VertexAI"
                # Extract [問題 X/Y] header before text processing
                raw_lines = raw.splitlines()
                if raw_lines and _Q_HEADER_RE.match(raw_lines[0].strip()):
                    q_header = raw_lines[0].strip()
                    raw = "\n".join(raw_lines[1:]).strip()
                else:
                    q_header = "[問題 ?/?]"
            else:
                raw = _ocr_image(client, pil_image)
                backend_tag = "Vision"
                q_header = ""
            text = _filter_text(raw, filter_texts)
            text = _format_quiz_text(text)
            if q_header:
                text = q_header + "\n" + text
        except Exception as e:
            text = f"[{backend_tag if 'backend_tag' in dir() else 'OCR'} error: {e}]"
            print(f"[VisionWorker] {filename} error: {e}")
        else:
            done_set.add(filename)
            _save_progress(screenshots_dir, done_set)

        with lock:
            results_dict[filename] = text

        task_queue.task_done()

        if on_result is not None:
            try:
                on_result(filename, text)
            except Exception as exc:
                print(f"[VisionWorker] on_result error: {exc}")


# ---------------------------------------------------------------------------
# Public API — same signature pattern as ocr_worker.start_worker
# ---------------------------------------------------------------------------

def start_worker(
    task_queue: queue.Queue,
    results_dict: dict,
    lock: threading.Lock,
    key_path: str = "",
    filter_texts: list[str] = None,
    screenshots_dir: str = "",
    backend: str = "google_vision",
    vertexai_project: str = "",
    vertexai_model: str = "",
    vertexai_fallback_model: str = "",
    vertexai_regions: list[str] = None,
    on_result=None,
) -> threading.Thread:
    """Start the OCR worker thread.

    Args:
        backend: 'google_vision' (default) or 'vertex_ai'
        key_path: Service-account JSON for Google Cloud Vision (only when backend='google_vision')
        vertexai_project: GCP project ID for Vertex AI
        vertexai_model: Vertex AI model name (e.g. 'google/gemini-flash-lite-preview-06-17')
        vertexai_regions: List of regions for round-robin rotation to avoid quota limits
    """
    t = threading.Thread(
        target=_worker_loop,
        kwargs=dict(
            task_queue=task_queue,
            results_dict=results_dict,
            lock=lock,
            key_path=key_path,
            filter_texts=filter_texts or [],
            screenshots_dir=screenshots_dir,
            backend=backend,
            vertexai_project=vertexai_project,
            vertexai_model=vertexai_model,
            vertexai_fallback_model=vertexai_fallback_model,
            vertexai_regions=vertexai_regions or ["us-central1"],
            on_result=on_result,
        ),
        daemon=True,
    )
    t.start()
    return t


def wait_until_done(task_queue: queue.Queue) -> None:
    task_queue.join()
