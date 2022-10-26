from functools import reduce
from http.client import HTTPException
from flask import Flask, abort, jsonify, request
from flask_cors import CORS, cross_origin
import fitz
from werkzeug.exceptions import default_exceptions

COLOR_WHITE = 16777215

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JSON_SORT_KEYS'] = False

def _detect_chars(text_blocks):
    lines = [b['lines'] for b in text_blocks]
    lines = reduce(lambda a,b: a+b, lines)
    spans = [l['spans'] for l in lines]
    spans = reduce(lambda a,b: a+b, spans)

    detected_chars = []

    total_illusive = 0

    for span in spans:
        chars = span["chars"]
        for char in chars:
            text = char["c"]
            bbox = char["bbox"]
            if span["color"] == COLOR_WHITE:
                total_illusive += 1
            
            detected_chars.append({
                "char": text,
                "rect": {
                    "x1": bbox[0],
                    "y1": bbox[1],
                    "x2": bbox[2],
                    "y2": bbox[3],
                },
            })
        
    return detected_chars, total_illusive

@app.route('/sendDocuments', methods=['POST'])
@cross_origin()
def send_document():
    """ return followed response
        {
            total_illusive_chars: 100,
            pages: [
                {
                    "page": 0,
                    "width": 595.32,
                    "height": 841.92,
                    "items": [
                        {
                            "char": "A",
                            "rect": {
                                "x1": 92.6500015258789,
                                "y1": 147.08999633789062,
                                "x2": 540.7999877929688,
                                "y2": 225.69000244140625,
                            }
                        },
                        ...
                    ],
                    ...
                }
            ]
        }
        """
    try:
        req_pdf_file = request.files['file'].stream.read()
        pdf_file = fitz.open(stream=req_pdf_file)
        pages = []
        total_illusive = 0
        for curr_page, page in enumerate(pdf_file):
            text_page = page.get_textpage()
            page_dict = text_page.extractRAWDICT()
            items, total_illusive_curr = _detect_chars(page_dict["blocks"])
            pages.append({
                "page": curr_page,
                "width": page_dict["width"],
                "height": page_dict["height"],
                "items": items,
            })
            total_illusive += total_illusive_curr

        return jsonify({
            "total_illusive_chars": total_illusive,
            "pages": pages
        })

    except Exception as e:
        abort(500, e)

@app.errorhandler(HTTPException)
def handle_exception(e):
   response = jsonify({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
   return response, e.code

if __name__ == '__main__':
   for ex in default_exceptions:
      app.register_error_handler(ex, handle_exception)
   app.run(debug=True, port=2727)