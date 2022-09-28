import json
import os
import re
import unittest
import time

import fitz

from illusive_text_detector import IllusiveTextDetector
# import program.illusive_text_detector as ill


class TestIllusiveTestDetector(unittest.TestCase):

    def setUp(self):
        self.COLOR_WHITE = 16777215
        self.TEST_DIR = "../test-document"

    def generate_test_schema(self):
        """
        [
            {
                'location': '../test-document/word',
                'test_subject': [
                    {
                        'document': 'TEST1.pdf',
                        'actual': 'TEST1.json'
                    }
                ]
            }
        ]
        """
        test_schema = []
        # print(self.TEST_DIR)
        for root, dirs, files in os.walk(self.TEST_DIR):
            # if(len(files) == 0):
            #     continue
            # print(files)
            document_files = [f for f in files if f.endswith('.pdf')]
            actual_files = [f for f in files if f.endswith('.json')]
            assert(len(document_files) == len(actual_files))

            test_schema.append({
                "location": re.sub("\\\+", "/", root),
                "test_subject": [
                    {
                        "document": document_files[i],
                        "actual": actual_files[i]
                    } for i in range(0, len(document_files))
                ]
            })
        return test_schema
    
    def dump_predicted(self, filename, predicted, doc, bboxes):
        json_object = json.dumps(predicted, indent=2)
        with open(f"test_dumps/{filename}.json", "w") as outfile:
            outfile.write(json_object)
        for page in doc:
            for b in bboxes:
                shape=page.new_shape()
                shape.draw_rect(b)
                shape.finish(color=(0,0,0))
                shape.commit()
        doc.save(f"test_dumps/{filename}.pdf")

    def test_detector(self):
        
        detector = IllusiveTextDetector()
        test_schema = self.generate_test_schema()
        # print(test_schema)
        start_time = time.time()
        for schema in test_schema:
            loc = schema["location"]
            for idx, subject in enumerate(schema["test_subject"]):
                file = open(f"{loc}\{subject['actual']}")
                actual = json.load(file)
                file.close()
                predicted, bboxes = detector.detect(f"{loc}\{subject['document']}")
                try:
                    self.assertEqual(actual, predicted)
                    print(f"{loc}/{subject['document']} SUCCESS in {time.time() - start_time}")
                except AssertionError:
                    doc = fitz.open(f"{loc}\{subject['document']}")
                    x = loc.split("/")
                    title = subject['actual'].split('.')[0]
                    self.dump_predicted(f"{x[-1]}_{title}", predicted, doc, bboxes)
                file.close()
    
if __name__ == "__main__":
    unittest.main()