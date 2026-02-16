"""
Command modules for Terra Invicta Advisory System

Each command is in its own module for maintainability.
"""

from . import install
from . import clean
from . import build
from . import parse
from . import inject
from . import validate
from . import perf
from . import run

__all__ = [
    'install',
    'clean', 
    'build',
    'parse',
    'inject',
    'validate',
    'perf',
    'run',
]
