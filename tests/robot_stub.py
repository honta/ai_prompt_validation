from __future__ import annotations

import sys
import types


def install_robot_stub():
    if "robot.api" in sys.modules and "robot.api.deco" in sys.modules:
        return

    robot_module = types.ModuleType("robot")
    api_module = types.ModuleType("robot.api")
    deco_module = types.ModuleType("robot.api.deco")

    class _Logger:
        @staticmethod
        def info(*args, **kwargs):
            return None

    def keyword(_name=None):
        def decorator(func):
            return func

        return decorator

    def library(*args, **kwargs):
        def decorator(obj):
            return obj

        return decorator

    api_module.logger = _Logger()
    api_module.deco = deco_module
    deco_module.keyword = keyword
    deco_module.library = library
    robot_module.api = api_module

    sys.modules["robot"] = robot_module
    sys.modules["robot.api"] = api_module
    sys.modules["robot.api.deco"] = deco_module
