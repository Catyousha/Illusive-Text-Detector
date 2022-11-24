from functools import reduce
import fitz
import json
from minio import Minio
import nsq
import tornado

client = Minio(
        "127.0.0.1:9000",
        access_key="Q3AM3UQ867SPQQA43P2F",
        secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
        secure=False,
)

COLOR_WHITE = 16777215

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

def detect(filename):
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
    obj = client.get_object("documents", filename)
    pdf_file = fitz.open(stream=obj.read())
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

    return json.dumps({
        "total_illusive_chars": total_illusive,
        "pages": pages
    })



OUTPUT_QUEUE = []
def subscriber_handler(message):
    bbody = message.body
    body = json.loads(bbody.decode('utf-8'))
    result = detect(body['file_name'])
    OUTPUT_QUEUE.append(result)
    return True

r = nsq.Reader(
        message_handler=subscriber_handler,
        lookupd_http_addresses=['http://127.0.0.1:4161'],
        topic='TESTAGAIN',
        channel='method1',
        lookupd_poll_interval=15,
    )

writer = nsq.Writer(['localhost:4150'])
def publish():
    if(len(OUTPUT_QUEUE) != 0):
        msg = OUTPUT_QUEUE.pop(0)
        writer.pub('documents', msg.encode('utf-8'), finish_pub)

def finish_pub(conn, data):
    print(data)

tornado.ioloop.PeriodicCallback(publish, 1000).start()
nsq.run()