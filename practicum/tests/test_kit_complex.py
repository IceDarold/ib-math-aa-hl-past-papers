"""Проверяет механику сверки комплексных ответов.

Главное требование: форма записи не должна влиять на результат. Полярная,
показательная и декартова записи одного числа обязаны проходить одинаково,
потому что markscheme принимает их все. Отдельно проверяется, что при этом
проверка не стала слепой и разные числа по-прежнему различает.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *
from kit import digest, _complex_canon

res = []


def t(name, ok):
    res.append((name, ok))
    print(('✅' if ok else '❌'), name)


print('=== одно число в разных записях ===')
want = digest(_complex_canon(-1 + sqrt(3) * I))
forms = {
    'декартова  −1 + √3 i': -1 + sqrt(3) * I,
    'показательная 2e^{2πi/3}': 2 * exp(2 * I * pi / 3),
    'тригонометрическая': 2 * (cos(2 * pi / 3) + I * sin(2 * pi / 3)),
    'через градусы': 2 * (cos(120 * pi / 180) + I * sin(120 * pi / 180)),
    'сопряжённое от сопряжённого': sp.conjugate(-1 - sqrt(3) * I),
}
for name, form in forms.items():
    t(f'проходит: {name}', check_complex(f'  {name}', form, want))

print('\n=== 3 − 3i, где аргумент отрицателен ===')
w2 = digest(_complex_canon(3 - 3 * I))
for name, form in {'декартова': 3 - 3 * I,
                   'показательная': 3 * sqrt(2) * exp(-I * pi / 4),
                   'тригонометрическая': 3 * sqrt(2) * (cos(-pi / 4) + I * sin(-pi / 4))}.items():
    t(f'проходит: {name}', check_complex(f'  {name}', form, w2))

print('\n=== чисто действительные и чисто мнимые ===')
t('−256 действительное', check_complex('  −256', (1 + I * sqrt(3))**8 + (1 - I * sqrt(3))**8,
                                       digest(_complex_canon(-256))))
t('−0 не отличается от 0', _complex_canon(sp.Float(-1e-30) + 0 * I) == _complex_canon(0))
print('   канон нуля:', _complex_canon(0), '/', _complex_canon(sp.Float(-1e-30)))

print('\n=== набор корней, порядок не важен ===')
roots = [2 * exp(2 * I * pi * k / 3) for k in range(3)]
wset = digest('|'.join(sorted(_complex_canon(r) for r in roots)))
t('прямой порядок', check_complex_set('  корни', roots, wset))
t('обратный порядок', check_complex_set('  корни наоборот', list(reversed(roots)), wset))
t('смешанные формы', check_complex_set('  смешанно', [2, -1 + sqrt(3) * I, 2 * exp(-2 * I * pi / 3)], wset))

print('\n=== должны падать ===')
t('другое число', not check_complex('  −1 − √3 i', -1 - sqrt(3) * I, want))
t('перепутан знак мнимой', not check_complex('  1 + √3 i', 1 + sqrt(3) * I, want))
t('модуль вместо числа', not check_complex('  2', 2, want))
t('десятичное вместо точного',
  not check_complex('  −1 + 1.732i', -1 + 1.732 * I, want))
t('корень пропущен', not check_complex_set('  два из трёх', roots[:2], wset))
t('корень задвоен', not check_complex_set('  с повтором', [roots[0]] + roots, wset))
t('пустой ответ', not check_complex('  пусто', ..., want))
t('пустой элемент набора', not check_complex_set('  дыра в наборе', [roots[0], ..., roots[2]], wset))

print('\n=== sf ослабляет требование до трёх значащих цифр ===')
w3 = digest(_complex_canon(-1 + sqrt(3) * I, sf=3))
t('десятичное проходит при sf=3',
  check_complex('  −1 + 1.73i', -1 + 1.73 * I, w3, sf=3))
t('но грубое всё равно нет',
  not check_complex('  −1 + 1.7i', -1 + 1.7 * I, w3, sf=3))

bad = [n for n, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  ({len(res) - len(bad)}/{len(res)})')
