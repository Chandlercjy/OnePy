from functools import wraps

from OnePy.environment import Environment


class OnePyEnvBase:
    """作为基类，提供env共享单例给各个模块"""
    env = Environment
