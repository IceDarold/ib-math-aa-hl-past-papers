"""Проверочный набор для практикумов по IB Mathematics AA HL.

Принцип: ответ проверяется по существу задачи, а не сравнением с записанным
эталоном. Решение дифференциального уравнения подставляется в само уравнение,
неявный ответ принимается в любой эквивалентной форме, числовой ответ
сверяется по хешу с округлением до требуемого числа значащих цифр.

Так в ячейке проверки не видно ответа, а эквивалентные формы записи
засчитываются — ровно как в markscheme.

Набор разложен по темам программы:

    core          имена ноутбука, язык, хеш, первые проверки, тренажёр
    algebra       многочлены, неравенства, уравнения          A4 A8 B1
    functions     обратная, графики, асимптоты, корни, модели B2–B5 C3
    geometry      треугольник и фигура                        C1 C2
    sequences     прогрессии                                  A1 A2
    derivative    пределы, ряды Маклорена, производная        E1 E2 E3
    tangent       касательная и нормаль                       E4
    integral      первообразная и измеренное                  E5 E6
    probability   вероятность и счёт                          D1 D2
    distribution  распределение по модели                     D3
    table         таблица распределения                       D4
    normal        нормальное распределение                    D5
    density       величина с плотностью                       D6
    vectors       векторы, прямые, углы                       C5

Снаружи пакет — по-прежнему один набор. Ноутбук пишет `from kit import *`,
тренажёр — `kit.verify_chance`, генераторы — `from kit import _series_canon`,
поэтому здесь все имена всех модулей собираются в одно пространство, с
подчёркиванием и без. На Kaggle соседних файлов нет, и make_kaggle.py
склеивает модули в этом же порядке обратно в одну ячейку.
"""

from . import (
    core, algebra, functions, geometry, sequences, derivative, tangent,
    integral, probability, distribution, table, normal, density, vectors,
)

MODULES = (core, algebra, functions, geometry, sequences, derivative, tangent,
           integral, probability, distribution, table, normal, density, vectors)

for _module in MODULES:
    globals().update((name, value) for name, value in vars(_module).items()
                     if not name.startswith('__'))

__all__ = sorted({name for _module in MODULES for name in vars(_module)
                  if not name.startswith('_')})
del _module
