import fitz
from functools import reduce

class IllusiveTextDetector:

    def __init__(self):
        fitz.TOOLS.set_small_glyph_heights(True)
        self.COLOR_WHITE = 16777215
        self.LABEL_ILLUSIVE = "ILLUSIVE"
        self.LABEL_NON_ILLUSIVE = "NON-ILLUSIVE"

    def _detect_chars(self, text_blocks):
        lines = [b['lines'] for b in text_blocks]
        lines = reduce(lambda a,b: a+b, lines)
        spans = [l['spans'] for l in lines]
        spans = reduce(lambda a,b: a+b, spans)

        detected_chars = []

        total_illusive = 0
        total_non_illusive = 0

        for span in spans:
            chars = span["chars"]
            for char in chars:
                text = char["c"]
                # origin = char["origin"]
                if span["color"] == self.COLOR_WHITE:
                    label = self.LABEL_ILLUSIVE
                    total_illusive += 1
                else:
                    label = self.LABEL_NON_ILLUSIVE
                    total_non_illusive += 1
                
                detected_chars.append({
                    # "page": curr_page,
                    # "origin": (origin[0], origin[1]),
                    "char": text,
                    "label": label,
                })
            
        return detected_chars, (total_illusive, total_non_illusive)

    def detect(self, file_loc: str):
        """ return followed schema
        {
            total_illusive: 100,
            total_non_illusive: 100,
            total_characters: 200
            chars_data: [
                    {
                        char: 'a',
                        label: 'ILLUSIVE'
                    },
                    {
                        char: 'b',
                        label: 'ILLUSIVE'
                    },
                    {
                        char: 'c',
                        label: 'ILLUSIVE'
                    },
                    ...
            ]
        }
        """
        doc = fitz.open(file_loc)
        predicted_page_chars = []
        total_illusive = 0
        total_non_illusive = 0
        for curr_page, page in enumerate(doc):
            text_page = page.get_textpage()
            blocks = text_page.extractRAWDICT()["blocks"]
            detected_chars, total_label = self._detect_chars(blocks)
            total_illusive += total_label[0]
            total_non_illusive += total_label[1]
            predicted_page_chars += detected_chars

        res = {
            "total_illusive": total_illusive,
            "total_non_illusive": total_non_illusive,
            "total_characters": total_illusive + total_non_illusive,
            "chars_data": predicted_page_chars
        }
        return res