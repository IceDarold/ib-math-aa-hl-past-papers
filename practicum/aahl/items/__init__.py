"""Реестр генераторов задач на счёт.

Ключ — идентификатор приёма из банка (`C1.cosine_rule`). Один модуль на
практикум; приём без генератора работает только на узнавание, и это видно
в статистике и на экране настроек.
"""
from __future__ import annotations

from . import (a1, a2, a3, a4, a5, a6, a7, a8, b1, b2, b3, b4, b5, c1,
               c2, c3, c4, c5, c6, d1, d2, d3, d4, d5, d6, e1, e2, e3, e4, e5, e6, e7)

GENERATORS = {}
for module in (a1, a2, a3, a4, a5, a6, a7, a8, b1, b2, b3, b4, b5, c1,
               c2, c3, c4, c5, c6, d1, d2, d3, d4, d5, d6, e1, e2, e3, e4, e5, e6, e7):
    GENERATORS.update(module.GENERATORS)

__all__ = ['GENERATORS']
