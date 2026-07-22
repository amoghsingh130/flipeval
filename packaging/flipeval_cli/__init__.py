"""Standalone CLI layer over the registered FlipEval analysis code.

This package adds packaging, argument parsing, input validation and reporting.
It computes no statistics of its own: `flipeval.core` and `flipeval.io` are
imported and used unchanged.
"""
from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["__version__"]
