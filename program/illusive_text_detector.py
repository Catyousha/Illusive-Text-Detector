import fitz
from functools import reduce

class IllusiveTextDetector:

    def __init__(self):
        fitz.TOOLS.set_small_glyph_heights(True)
        self.COLOR_WHITE = 16777215

    def _get_spans(self, text_blocks):
        lines = [b['lines'] for b in text_blocks]
        lines = reduce(lambda a,b: a+b, lines)
        spans = [l['spans'] for l in lines]
        spans = reduce(lambda a,b: a+b, spans)
        return spans

    def detect(self, filename: str):
        doc = fitz.open(filename)
        predict = []
        bboxes = []
        for curr_page, page in enumerate(doc):
            text_page = page.get_textpage()
            page_dict = text_page.extractDICT()
            blocks = [b for b in page_dict["blocks"]]
            extracted_spans = self._get_spans(blocks)
            # print(blocks)
            illusive_text = [
                {
                    # "bbox": list(s["bbox"]),
                    "origin": list(s["origin"]),
                    "text": s["text"],
                    "page": curr_page,
                } for s in extracted_spans if s["color"] == self.COLOR_WHITE
            ]
            bbox = [
                list(s["bbox"])
                for s in extracted_spans if s["color"] == self.COLOR_WHITE
            ]
            predict += illusive_text
            bboxes += bbox
        return predict, bbox