import json
from pathlib import Path

RESOURCES_DIR = Path(__file__).resolve().parent.parent / "resources"


class ReadResource:
    @staticmethod
    def read_json(file_name):
        with open(RESOURCES_DIR / file_name) as opened_file:
            return json.load(opened_file)

    @staticmethod
    def read_resource(file_name):
        return ReadResource.read_json(file_name)
