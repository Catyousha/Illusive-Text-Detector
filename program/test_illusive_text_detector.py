import json
import os
import re
import unittest
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
    
    def test_detector(self):
        detector = IllusiveTextDetector()
        test_schema = self.generate_test_schema()
        # print(test_schema)
        
        for schema in test_schema:
            loc = schema["location"]
            for idx, subject in enumerate(schema["test_subject"]):
                file = open(f"{loc}\{subject['actual']}")
                actual = json.load(file)
                predicted = detector.detect(f"{loc}\{subject['document']}")
                self.assertEqual(actual, predicted)
                print(f"{loc}/{subject['document']} SUCCESS")
                file.close()
    
if __name__ == "__main__":
    unittest.main()