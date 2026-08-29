"""Реестр генераторов задач на счёт.

Ключ — идентификатор приёма из банка (`C1.cosine_rule`). Один модуль на
практикум; приём без генератора работает только на узнавание, и это видно
в статистике и на экране настроек.
"""
from __future__ import annotations

from . import a3, a4, a5, a6, a7, a8, b1, b2, b3, b4, b5, c1, c3, c4, e7

GENERATORS = {}
for module in (a3, a4, a5, a6, a7, a8, b1, b2, b3, b4, b5, c1, c3, c4, e7):
    GENERATORS.update(module.GENERATORS)

__all__ = ['GENERATORS']
