export type PracticumStatus = 'ready' | 'planned'

export interface PracticumSkill {
  id: string
  name: string
  trigger: string
  calculator: 'required' | 'replaces' | 'speeds_up' | 'checks' | 'forbidden'
}

export interface Practicum {
  id: string
  title: string
  section: string
  sectionTitle: string
  topics: string[]
  status: PracticumStatus
  notebook?: string
  corpus?: { blocks: number; marks: number; papers: { no: number; yes: number } }
  skills?: PracticumSkill[]
}

const sections = {
  A: 'Числа и алгебра',
  B: 'Функции',
  C: 'Геометрия и тригонометрия',
  D: 'Статистика и вероятность',
  E: 'Математический анализ',
} as const

function item(id: string, title: string, section: keyof typeof sections, topics: string[], status: PracticumStatus = 'planned'): Practicum {
  return { id, title, section, sectionTitle: sections[section], topics, status }
}

export const practicums: Practicum[] = [
  item('A1', 'Арифметические прогрессии и суммы', 'A', ['number_algebra.sequences']),
  item('A2', 'Геометрические прогрессии и бесконечные суммы', 'A', ['number_algebra.sequences', 'number_algebra.geometric_sequences']),
  item('A3', 'Биномиальная теорема', 'A', ['number_algebra.binomial_theorem']),
  item('A4', 'Многочлены: Виета, деление, кратность корней', 'A', ['number_algebra.polynomials']),
  item('A5', 'Комплексные числа: формы и арифметика', 'A', ['number_algebra.complex_numbers']),
  item('A6', 'Муавр, корни из единицы, геометрия на плоскости', 'A', ['number_algebra.complex_numbers']),
  item('A7', 'Доказательство: индукция, прямое, от противного', 'A', ['number_algebra.mathematical_induction', 'number_algebra.proof']),
  item('A8', 'Неравенства', 'A', ['number_algebra.inequalities', 'functions.inequalities']),

  item('B1', 'Уравнения: квадратные, дробные, с параметром', 'B', ['functions.equations']),
  item('B2', 'Композиция и обратные функции', 'B', ['functions.equations', 'functions.inverse_functions']),
  item('B3', 'Преобразования графиков', 'B', ['functions.graphing']),
  item('B4', 'Исследование функции, асимптоты, эскиз', 'B', ['functions.curve_sketching', 'functions.asymptotes']),
  item('B5', 'Показательные и логарифмические модели', 'B', ['functions.logarithmic_functions', 'functions.exponential_models', 'functions.mathematical_models', 'number_algebra.exponential_models']),

  item('C1', 'Треугольник: синусы, косинусы, площадь', 'C', ['geometry.trigonometry']),
  item('C2', 'Радианная мера, сектор, объёмные тела', 'C', ['geometry.circular_measure', 'geometry.solid_geometry']),
  {
    id: 'C3', title: 'Тригонометрические уравнения', section: 'C', sectionTitle: sections.C,
    topics: ['geometry.trigonometric_equations'], status: 'ready',
    notebook: 'practicum/geometry/practicum-c3-trigonometric-equations.ipynb',
    corpus: { blocks: 31, marks: 127, papers: { no: 23, yes: 8 } },
    skills: [
      { id: 'reference_angle', name: 'Опорный угол и все корни в области', trigger: 'Одна тригонометрическая функция от x.', calculator: 'replaces' },
      { id: 'compound_argument', name: 'Составной аргумент', trigger: 'Под функцией стоит ax + b, а не x.', calculator: 'replaces' },
      { id: 'pythagorean_reduction', name: 'Пифагорово тождество и квадратное уравнение', trigger: 'Есть квадрат одной функции и первая степень другой.', calculator: 'replaces' },
      { id: 'double_angle_reduction', name: 'Двойной угол и квадратное уравнение', trigger: 'Встречаются 2x и x.', calculator: 'replaces' },
      { id: 'factor_not_divide', name: 'Разложение на множители вместо деления', trigger: 'Уравнение сводится к A·B = 0.', calculator: 'replaces' },
      { id: 'reduce_to_tangent', name: 'Сведение к тангенсу', trigger: 'sin и cos входят в одинаковой степени.', calculator: 'replaces' },
      { id: 'root_selection', name: 'Отбор корней и посторонние решения', trigger: 'Есть ограничения области, дробь, корень или обратная функция.', calculator: 'speeds_up' },
      { id: 'numeric_gdc', name: 'Численное решение', trigger: 'Paper 2 и ответ до трёх значащих цифр.', calculator: 'required' },
    ],
  },
  item('C4', 'Тождества и тригонометрические функции', 'C', ['geometry.trigonometric_identities', 'functions.trigonometric_functions']),
  item('C5', 'Векторы: операции, прямые, углы', 'C', ['geometry.vectors']),
  item('C6', 'Прямые и плоскости в пространстве', 'C', ['geometry.vectors_3d']),
  item('C7', 'Расстояния, углы и векторное произведение', 'C', ['geometry.vectors_3d']),

  item('D1', 'Комбинаторика: размещения, блоки, дополнение', 'D', ['statistics.combinatorics']),
  item('D2', 'Вероятность: условная, независимость, деревья', 'D', ['statistics.probability']),
  item('D3', 'Биномиальное распределение', 'D', ['statistics.probability']),
  item('D4', 'Дискретные случайные величины и математическое ожидание', 'D', ['statistics.discrete_random_variables', 'statistics.expected_value']),
  item('D5', 'Нормальное распределение и обратная задача', 'D', ['statistics.continuous_random_variables']),
  item('D6', 'Непрерывные СВ: плотность, медиана, квантили', 'D', ['statistics.continuous_random_variables']),
  item('D7', 'Регрессия и корреляция', 'D', ['statistics.regression']),

  item('E1', 'Пределы, неопределённости, правило Лопиталя', 'E', ['calculus.limits']),
  item('E2', 'Ряды Маклорена', 'E', ['calculus.series']),
  item('E3', 'Техника дифференцирования', 'E', ['calculus.differentiation']),
  item('E4', 'Неявное и параметрическое дифференцирование', 'E', ['calculus.differentiation']),
  item('E5', 'Техника интегрирования', 'E', ['calculus.integration_applications']),
  item('E6', 'Площади, объёмы вращения, накопление', 'E', ['calculus.integration_applications']),
  {
    id: 'E7', title: 'Дифференциальные уравнения первого порядка', section: 'E', sectionTitle: sections.E,
    topics: ['calculus.differential_equations'], status: 'ready',
    notebook: 'practicum/calculus/practicum-e7-differential-equations.ipynb',
    corpus: { blocks: 64, marks: 254, papers: { no: 6, yes: 31 } },
    skills: [
      { id: 'direct_integration', name: 'Прямое интегрирование', trigger: 'Правая часть зависит только от x или является константой.', calculator: 'speeds_up' },
      { id: 'separation', name: 'Разделение переменных', trigger: 'Правая часть раскладывается в f(x)·g(y).', calculator: 'checks' },
      { id: 'separation_partial_fractions', name: 'Разделение с простейшими дробями', trigger: 'После разделения появляется дробь с разложимым знаменателем.', calculator: 'checks' },
      { id: 'homogeneous_substitution', name: 'Однородное уравнение: y = vx', trigger: 'Правая часть зависит только от отношения y/x.', calculator: 'forbidden' },
      { id: 'integrating_factor', name: 'Интегрирующий множитель', trigger: 'Уравнение приводится к y′ + P(x)y = Q(x).', calculator: 'checks' },
      { id: 'euler_method', name: 'Метод Эйлера', trigger: 'Дан шаг h и требуется приближённое значение.', calculator: 'required' },
      { id: 'euler_error_sign', name: 'Знак ошибки Эйлера через вогнутость', trigger: 'Спрашивают, занижено или завышено приближение.', calculator: 'speeds_up' },
    ],
  },
  item('E8', 'Стационарные точки, вогнутость, перегиб', 'E', ['calculus.stationary_points']),
  item('E9', 'Оптимизация и связанные скорости', 'E', ['calculus.optimization', 'calculus.rates_of_change']),
]

export const practicumSections = Object.entries(sections).map(([id, title]) => ({ id, title }))
