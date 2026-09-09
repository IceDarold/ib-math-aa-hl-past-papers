// Файл собирается: python practicum/build_browser_practicum.py
// Руками не править — правьте practicum/map.yaml и карточку приёмов.

export interface PracticumSkill {
  id: string
  name: string
  trigger: string
  calculator: 'required' | 'replaces' | 'speeds_up' | 'checks' | 'forbidden'
}

export interface Practicum {
  id: string
  title: string
  topics: string[]
  notebook: string
  skills: PracticumSkill[]
}

/** Единственный практикум, который проходится прямо в браузере.
 *  Остальной список страница берёт у службы, а та — из
 *  practicum/map.yaml: держать его ещё и здесь значило отставать. */
export const practicums: Practicum[] = [
  {
    id: 'C3',
    title: 'Тригонометрические тождества и уравнения',
    topics: ['geometry.trigonometric_equations', 'geometry.trigonometric_identities'],
    notebook: 'practicum/geometry/practicum-c3-trigonometric-equations.ipynb',
    skills: [
      { id: 'reference_angle', name: 'Опорный угол и все корни в области', trigger: 'Одна тригонометрическая функция, аргумент равен самому x.', calculator: 'replaces' },
      { id: 'compound_argument', name: 'Составной аргумент', trigger: 'Под функцией стоит не x, а ax + b — например 2x − 5°, x/2 + π/3, 2θ.', calculator: 'replaces' },
      { id: 'angle_sum', name: 'Формулы сложения углов', trigger: 'Аргумент есть сумма или разность двух углов, каждый из которых интересен отдельно.', calculator: 'forbidden' },
      { id: 'pythagorean_reduction', name: 'Пифагорово тождество и квадратное уравнение', trigger: 'В уравнении есть квадрат одной функции и первая степень другой.', calculator: 'replaces' },
      { id: 'double_angle_reduction', name: 'Двойной угол и квадратное уравнение', trigger: 'В одном уравнении встречаются и 2x, и x.', calculator: 'replaces' },
      { id: 'factor_not_divide', name: 'Разложение на множители вместо деления', trigger: 'Обе части содержат общий множитель, или уравнение сводится к A·B = 0.', calculator: 'replaces' },
      { id: 'reduce_to_tangent', name: 'Сведение к тангенсу', trigger: 'sin и cos входят в одинаковой степени, и уравнение однородно по ним.', calculator: 'replaces' },
      { id: 'root_selection', name: 'Отбор корней и посторонние решения', trigger: 'В условии есть оговорка вида θ ≠ π/4, дробь, корень, обратная функция, либо просят «наименьшее положительное».', calculator: 'speeds_up' },
      { id: 'numeric_gdc', name: 'Численное решение', trigger: 'Коэффициенты не дают точных значений на единичной окружности, задача из Paper 2, ответ просят с точностью до трёх значащих цифр.', calculator: 'required' },
    ],
  },
]
