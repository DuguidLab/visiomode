"""Parser for Phone-RPi JSON requests"""
import json


def parse(raw):
    return json.loads(str(raw, "utf-8"))
