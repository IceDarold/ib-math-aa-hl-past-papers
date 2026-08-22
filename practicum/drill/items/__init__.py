"""Реестр генераторов задач на счёт.

Ключ — идентификатор приёма из банка (`C1.cosine_rule`). Практикум без
своего модуля просто не попадает в режим счёта: тренажёр по нему работает
на узнавание, и это видно в статистике как непокрытый приём.
"""
from __future__ import annotations

from . import b1, c1

GENERATORS = {}
GENERATORS.update(c1.GENERATORS)
GENERATORS.update(b1.GENERATORS)

__all__ = ['GENERATORS']
