# ai_library/result_store.py
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from ai_library.config import Config


class ResultStore:
    def __init__(self, output_dir: str | None = None):
        self.output_dir = output_dir or Config.RESULTS_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def save_result(self, payload: dict[str, Any], filename_prefix: str = "result") -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        file_path = os.path.join(self.output_dir, f"{filename_prefix}_{timestamp}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return file_path
