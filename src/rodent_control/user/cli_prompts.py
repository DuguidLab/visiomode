"""CLI prompts for user input"""
import json


def all_settings(as_json=True):
    all_settings = {
            'task': task_settings(as_json=False),
            'session': session_settings(as_json=False)
        }
    if as_json:
        return json.dumps(all_settings)
    return all_settings


def task_settings(as_json=True):
    task_settings = {
            'targets': int(input("Number of targets: ")),
            'width': int(input("Target width (mm): ")),
            'distance': int(input("Distance between targets (mm): ")),
            'delay': int(input("Presentation delay (ms): ")),
            'haptics': False if input("Haptic feedback (Y/N): ") == 'N' else True,
            'animated': True if input("Animated (Y/N): ") == 'Y' else False,
            'shrinking': True if input("Shrinking (Y/N): ") == 'Y' else False
        }
    if as_json:
        return json.dumps(task_settings)
    return task_settings


def session_settings(as_json=True):
    session_settings = {
            'sessionType': 'rpi',
            'duration': float(input("Session duration (min): ")),
            'showResults': False,
            'playToneAtEnd': True if input("Tone at End (Y/N): ") == 'Y' else False,
            'saveSession': True
        }
    if as_json:
        return json.dumps(session_settings)
    return session_settings


def animation_settings(as_json=True):
    return


def shrinking_settings(as_json=True):
    return
