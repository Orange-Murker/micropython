"""
Empty runpy module

Specifically added to make VS Code trust our executable
"""

json_text = '{"versionInfo": [1, 0, 0, "final", 0], "sysPrefix": "C:\\\\Program Files\\\\micropython", "version": "1.0.0 (micropython)", "is64Bit": true}'


def run_path(module, run_name="__main__"):

    print(json_text)

    return json_text


def run_module(module, run_name="__main__", alter_sys=True):

    print(json_text)

    return json_text
