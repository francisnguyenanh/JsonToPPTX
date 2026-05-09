"""
Vertex AI slide designer.

Uses the same urllib-based REST pattern as vision_worker._VertexAIClient but
for text-only (no image) generation.  Calls Gemini via the Vertex AI
generateContent endpoint with system_instruction + JSON response mode.

Usage:
    designer = SlideDesigner.from_config()
    intent_deck = designer.generate(user_request, theme="VTI", lang="vi")
    # intent_deck is a dict ready for renderer.design_system.resolve_deck()
"""
from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request

try:
    import google.auth
    import google.auth.transport.requests
    _AUTH_AVAILABLE = True
except ImportError:
    _AUTH_AVAILABLE = False

_SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "slide_designer_system_prompt.md")


def _load_system_prompt() -> str:
    try:
        with open(_SYSTEM_PROMPT_PATH, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


class _TextVertexAIClient:
    """Thin wrapper around Vertex AI generateContent for text-only requests.

    Mirrors the region-rotation + fallback-model pattern from vision_worker
    so quota behaviour is consistent across the project.
    """

    _ENDPOINT = (
        "https://{region}-aiplatform.googleapis.com/v1/projects/{project}/"
        "locations/{region}/publishers/google/models/{model}:generateContent"
    )

    def __init__(
        self,
        project: str,
        model: str,
        regions: list[str],
        fallback_model: str = "",
        key_path: str = "",
    ):
        self.project = project
        self.model = model.replace("google/", "", 1) if "/" in model else model
        self.fallback_model = (
            fallback_model.replace("google/", "", 1)
            if fallback_model and "/" in fallback_model
            else fallback_model
        )
        self.regions = list(regions) if regions else ["us-central1"]
        self.key_path = key_path
        self._region_idx = 0
        self._creds = None
        self._lock = threading.Lock()

    # ── Credentials ──────────────────────────────────────────────────────────

    def _get_token(self) -> str:
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
            self._creds.refresh(google.auth.transport.requests.Request())
        return self._creds.token

    # ── Region rotation ───────────────────────────────────────────────────────

    def _current_region(self) -> str:
        with self._lock:
            return self.regions[self._region_idx % len(self.regions)]

    def _rotate_region(self) -> str:
        with self._lock:
            self._region_idx = (self._region_idx + 1) % len(self.regions)
            new = self.regions[self._region_idx]
        print(f"[SlideDesigner] Rotating to region: {new}")
        return new

    # ── Core call ─────────────────────────────────────────────────────────────

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.4,
        max_output_tokens: int = 8192,
        max_retries: int = 3,
    ) -> str:
        payload = json.dumps({
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [{
                "role": "user",
                "parts": [{"text": user_prompt}],
            }],
            "generation_config": {
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
                "response_mime_type": "application/json",
            },
        }).encode("utf-8")

        last_error = None
        for attempt in range(max_retries * len(self.regions)):
            region = self._current_region()
            url = self._ENDPOINT.format(region=region, project=self.project, model=self.model)

            try:
                token = self._get_token()
                req = urllib.request.Request(
                    url, data=payload,
                    headers={"Authorization": f"Bearer {token}",
                             "Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    body = json.loads(resp.read().decode("utf-8"))

                return body["candidates"][0]["content"]["parts"][0]["text"]

            except urllib.error.HTTPError as e:
                status = e.code
                err_body = e.read().decode("utf-8", errors="replace")
                last_error = f"HTTP {status}: {err_body[:300]}"

                if status in (429, 503):
                    print(f"[SlideDesigner] Quota on {region} (HTTP {status}), rotating...")
                    self._rotate_region()
                    time.sleep(2 ** min(attempt, 4))
                    continue

                if status in (400, 404):
                    if self.fallback_model and self.model != self.fallback_model:
                        print(f"[SlideDesigner] Switching to fallback: {self.fallback_model}")
                        self.model = self.fallback_model
                        self._rotate_region()
                        time.sleep(1)
                        continue
                    self._rotate_region()
                    time.sleep(1)
                    continue

                raise RuntimeError(last_error)

            except urllib.error.URLError as e:
                last_error = str(e)
                print(f"[SlideDesigner] Network error on {region}: {e}, rotating...")
                self._rotate_region()
                time.sleep(2)
                continue

        raise RuntimeError(
            f"Vertex AI failed after {max_retries * len(self.regions)} attempts. "
            f"Last: {last_error}"
        )


class SlideDesigner:
    """Generate semantic intent JSON for a slide deck via Vertex AI Gemini."""

    def __init__(self, client: _TextVertexAIClient):
        self._client = client
        self._system_prompt = _load_system_prompt()

    # ── Factory ───────────────────────────────────────────────────────────────

    @classmethod
    def from_config(cls) -> "SlideDesigner":
        """Build from vertex_AI/config.ini [slide_designer] section."""
        from .config_manager import (
            get_vertexai_project,
            get_vision_key_path,
            get_slide_designer_model,
            get_slide_designer_fallback_model,
            get_slide_designer_regions,
        )
        client = _TextVertexAIClient(
            project=get_vertexai_project(),
            model=get_slide_designer_model(),
            regions=get_slide_designer_regions(),
            fallback_model=get_slide_designer_fallback_model(),
            key_path=get_vision_key_path(),
        )
        return cls(client)

    # ── Public API ────────────────────────────────────────────────────────────

    def generate(
        self,
        user_request: str,
        theme: str = "VTI",
        lang: str = "vi",
    ) -> dict:
        """Call Gemini and return a parsed intent deck dict.

        Args:
            user_request: Free-text description of the slide deck to create.
            theme: "VTI" | "Dark" | "Light"
            lang: "vi" | "jp"

        Returns:
            dict with keys "deck_meta" and "slides" (semantic intent, no design values).
        """
        if not _AUTH_AVAILABLE:
            raise RuntimeError(
                "google-auth is not installed. "
                "Run: pip install google-auth requests"
            )

        user_prompt = (
            f"Theme: {theme}\n"
            f"Language: {lang}\n\n"
            f"{user_request}"
        )

        raw = self._client.generate(
            system_prompt=self._system_prompt,
            user_prompt=user_prompt,
        )

        try:
            deck = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"Gemini returned invalid JSON: {e}\n---\n{raw[:500]}") from e

        if "deck_meta" not in deck or "slides" not in deck:
            raise ValueError(
                f"Gemini response is missing 'deck_meta' or 'slides': {str(deck)[:300]}"
            )

        deck.setdefault("deck_meta", {})
        deck["deck_meta"].setdefault("theme", theme)
        deck["deck_meta"].setdefault("lang", lang)

        return deck
