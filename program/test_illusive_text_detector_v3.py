import json
import math
import os
import re
import unittest
import time
import sklearn.metrics as metrics

import fitz

from illusive_text_detector_v3 import IllusiveTextDetector
# import program.illusive_text_detector as ill


COLOR_WHITE = 16777215
IGNORE_REAL_SPACE = True # Auto generated document for testing still contain unwanted invisible space
TEST_DIR = "../test-document-v3/spaces"
POSITIVE = "ILLUSIVE"
NEGATIVE = "NON-ILLUSIVE"

def generate_test_schema():
    """
    [
        {
            'document': 'TEST1.pdf',
            'actual': 'TEST1.json'
        }
    ]
    """
    test_schema = []
    for root, dirs, files in os.walk(TEST_DIR):

        document_files = [f for f in files if f.endswith('.pdf')]
        actual_files = [f for f in files if f.endswith('.json')]
        assert(len(document_files) == len(actual_files))

        test_schema = [
            {
                "document": document_files[i],
                "actual": actual_files[i]
            } for i in range(0, len(document_files))
        ]
    return test_schema

def _comparator(actual, predicted):
    cond1 = math.isclose(actual["origin"][0], predicted["origin"][0], abs_tol=2)
    cond2 = math.isclose(actual["origin"][1], predicted["origin"][1], abs_tol=2)
    cond3 = actual["text"] == predicted["text"]
    assert(cond1 and cond2 and cond3) # PROGRAM IS FAILED IF ERROR
    if(not(cond1 and cond2 and cond3)):
        print(actual, predicted)

    return actual["label"], predicted["label"]
    
# def dump_predicted( json_name, pdf_name, spans):
#     json_object = json.dumps(spans, indent=2)
#     with open(f"test_dumps/{json_name}", "w") as outfile:
#         outfile.write(json_object)
#     doc = fitz.open(f"{TEST_DIR}/{pdf_name}")

#     for page in doc:
#         for s in spans:
#             print(s)
#             shape=page.new_shape()
#             shape.draw_rect(s["bbox"])
#             shape.finish(color=(0,0,0))
#             shape.commit()
#     doc.save(f"test_dumps/{json_name}.pdf")

def test_detector():
    detector = IllusiveTextDetector()
    test_schema = generate_test_schema()
    # print(test_schema)
    start_time = time.time()
    for schema in test_schema:
        json_file = open(f"{TEST_DIR}/{schema['actual']}")
        actual = json.load(json_file)
        json_file.close()
        predicted = detector.detect(f"{TEST_DIR}/{schema['document']}")
        predicted.sort(key=lambda p: (p["origin"][1], p["origin"][0]))
        
        if IGNORE_REAL_SPACE:
            actual = [a for a in actual if a["text"] != " "]
            predicted = [p for p in predicted if p["text"] != " "]

        actual_labels = []
        predicted_labels = []
        
        for i in range(actual.__len__()):
            a, p = _comparator(actual[i], predicted[i])
            actual_labels.append(a)
            predicted_labels.append(p)
        m = metrics.confusion_matrix(actual_labels, predicted_labels)
        acc = metrics.accuracy_score(actual_labels, predicted_labels)
        
        print(f"\n{schema['document']}")
        print(f"COMPLETED IN {time.time() - start_time}")
        print(f"TRUE POSITIVE: {m[0][0]}")
        print(f"FALSE POSITIVE: {m[0][1]}")
        print(f"TRUE NEGATIVE: {m[1][1]}")
        print(f"FALSE NEGATIVE: {m[1][0]}")
        print(f"ACCURACY: {acc}")


    
if __name__ == "__main__":
    test_detector()