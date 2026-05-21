from pathlib import Path
from typing import Optional

import yaml


class JurisdictionService:
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path(__file__).resolve().parents[1] / "jurisdictions"

    def load(self, jurisdiction_id: str) -> dict:
        path = self.base_path / f"{jurisdiction_id}.yaml"
        with path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file)
