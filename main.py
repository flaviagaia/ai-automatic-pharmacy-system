from __future__ import annotations

import json
from pathlib import Path

from src.pipeline import run_pipeline


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    summary = run_pipeline(base_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
