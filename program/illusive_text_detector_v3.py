import fitz
from functools import reduce

class IllusiveTextDetector:

    def __init__(self):
        fitz.TOOLS.set_small_glyph_heights(True)
        self.COLOR_WHITE = 16777215

    def _detect_chars(self, text_blocks, curr_page):
        lines = [b['lines'] for b in text_blocks]
        lines = reduce(lambda a,b: a+b, lines)
        spans = [l['spans'] for l in lines]
        spans = reduce(lambda a,b: a+b, spans)
        detected_chars = []
        for span in spans:
            chars = span["chars"]
            for char in chars:
                text = char["c"]
                origin = char["origin"]
                label = "ILLUSIVE" if (span["color"] == self.COLOR_WHITE) else "NON-ILLUSIVE"
                
                detected_chars.append({
                    "page": curr_page,
                    "origin": list((round(origin[0], 0), round(origin[1], 0))),
                    "text": text,
                    "label": label,
                })
            
        return detected_chars

    def detect(self, filename: str):
        doc = fitz.open(filename)
        predict = []
        for curr_page, page in enumerate(doc):
            text_page = page.get_textpage()
            blocks = text_page.extractRAWDICT()["blocks"]
            detected_chars = self._detect_chars(blocks, curr_page)
            predict += detected_chars
        return predict