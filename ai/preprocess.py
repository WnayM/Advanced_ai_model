from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence, List


@dataclass
class TextPreprocessorConfig:
    lowercase: bool = True
    max_len: int = 2000


class TextPreprocessor:
    def __init__(self, config: TextPreprocessorConfig | None = None) -> None:
        self.config = config or TextPreprocessorConfig()

    def clean_text(self, text: str) -> str:
        t = text or ""
        t = t.strip()
        if self.config.lowercase:
            t = t.lower()
        t = re.sub(r"\s+", " ", t)
        return t[: self.config.max_len]

    def clean_texts(self, texts: Sequence[str]) -> List[str]:
        return [self.clean_text(x) for x in texts]
