"""CLI prompts for user input"""
import json


def task_settings(as_json=True):
    task_settings = {
        # 'targets': int(input("Number of targets: ")),
        # 'width': int(input("Target width (mm): ")),
        # 'distance': int(input("Distance between targets (mm): ")),
        'mode': str(input("Task mode ([single_target] / vdt): ")) or "single_target",
        'duration': float(input("Session duration (min) [30]: ")) or 30.,
        'iti_min': int(input("ITI Min (ms) [2000]")) or 2000,
        'iti_max': int(input("ITI Max (ms) [4000]")) or 4000,
        'offset': int(input("Target offset (pix) [0]")) or 0,
        # 'haptics': False if input("Haptic feedback (Y/N): ") == 'N' else True,
        # 'animated': True if input("Animated (Y/N): ") == 'Y' else False,
        # 'shrinking': True if input("Shrinking (Y/N): ") == 'Y' else False
    }
    if as_json:
        return json.dumps(task_settings)
    return task_settings
