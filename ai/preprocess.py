import re
from typing import Sequence, List

class TextPreprocessor:
    URL_RE = re.compile(r"https?://\S+")
    MULTI_SPACE_RE = re.compile(r"\s+")

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        
        text = self.URL_RE.sub(" ", text)

        text = text.lower()

        text = self.MULTI_SPACE_RE.sub(" ", text).strip()

        return text

    def clean_texts(self, texts: Sequence[str]) -> List[str]:
        
        return [self.clean_text(t) for t in texts]
