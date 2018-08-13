"""CLI prompts for user input"""
import json


def task_settings(as_json=True):
    task_settings = {
            'targets': input("Number of targets: "),
            'width': input("Target width (mm): "),
            'distance': input("Distance between targets (mm): "),
            'delay': input("Presentation delay (ms): "),
            'haptics': False if input("Haptic feedback (Y/N): ") == 'N' else True,
            'animated': True if input("Animated (Y/N): ") != 'Y' else False,
            'shrinking': True if input("Shrinking (Y/N): ") != 'Y' else False
        }
    if as_json:
        return json.dumps(task_settings)
    return task_settings


def session_settings(as_json=True):
    return


def animation_settings(as_json=True):
    return


def shrinking_settings(as_json=True):
    return
