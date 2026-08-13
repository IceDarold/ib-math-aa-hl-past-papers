export type ExerciseLevel = '🟢' | '🟡' | '🔴'

export interface BrowserExercise {
  id: string
  skillId: string
  level: ExerciseLevel
  title: string
  prompt: string
  source: string
  answerMode: 'roots' | 'value'
  unit: 'radians' | 'degrees'
  expected: number[]
  hint: string
  solution: string
}

export const c3Exercises: BrowserExercise[] = [
  {
    id: 'c3-01', skillId: 'reference_angle', level: '🟢', title: 'Область шире одного оборота',
    prompt: 'График $f(x)=6+6\\cos x$ касается оси $x$. Найдите все $x$ на отрезке $0\\leq x\\leq4\\pi$, при которых это происходит.',
    source: 'May 2021 TZ2 — Paper 1 — Q10(a) — 3 балла', answerMode: 'roots', unit: 'radians', expected: [Math.PI, 3 * Math.PI],
    hint: 'Касание оси означает $6+6\\cos x=0$. Сначала назови значение косинуса, затем посчитай число оборотов области.',
    solution: '$\\cos x=-1$. На каждом обороте это $x=\\pi$; на $[0,4\\pi]$ оборотов два: $\\pi$ и $3\\pi$.',
  },
  {
    id: 'c3-02', skillId: 'compound_argument', level: '🟢', title: 'Градусы и составной аргумент',
    prompt: 'Решите $\\tan(2x-5^\\circ)=1$ для $0^\\circ\\leq x\\leq180^\\circ$.',
    source: 'May 2024 TZ2 — Paper 1 — Q1 — 4 балла', answerMode: 'roots', unit: 'degrees', expected: [25, 115],
    hint: 'Пусть $u=2x-5^\\circ$. Область для $u$ — не та же, что для $x$.',
    solution: '$u\\in[-5^\\circ,355^\\circ]$. $\\tan u=1$ при $45^\\circ$ и $225^\\circ$, откуда $x=25^\\circ,115^\\circ$.',
  },
  {
    id: 'c3-03', skillId: 'compound_argument', level: '🟡', title: 'Наименьшее положительное',
    prompt: 'Найдите наименьшее положительное $x$, при котором $\\cos\\left(\\frac{x}{2}+\\frac{\\pi}{3}\\right)=\\frac{1}{\\sqrt2}$.',
    source: 'May 2022 TZ2 — Paper 1 — Q4 — 5 баллов', answerMode: 'value', unit: 'radians', expected: [17 * Math.PI / 6],
    hint: 'Период по $x$ здесь равен $4\\pi$. Первые кандидаты отрицательны — не останавливайся.',
    solution: '$u=\\pm\\pi/4+2k\\pi$, $x=2u-2\\pi/3$. Первое положительное значение: $17\\pi/6$.',
  },
  {
    id: 'c3-04', skillId: 'pythagorean_reduction', level: '🟡', title: 'Пифагорово тождество',
    prompt: 'Решите $2\\cos^2x+5\\sin x=4$ для $0\\leq x\\leq2\\pi$.',
    source: 'May 2021 TZ2 — Paper 1 — Q2 — 7 баллов', answerMode: 'roots', unit: 'radians', expected: [Math.PI / 6, 5 * Math.PI / 6],
    hint: 'Рядом с квадратом косинуса стоит первая степень синуса. Оставь в уравнении только синус.',
    solution: '$2(1-\\sin^2x)+5\\sin x=4$. Получаем $(2\\sin x-1)(\\sin x-2)=0$; второе значение невозможно.',
  },
  {
    id: 'c3-05', skillId: 'double_angle_reduction', level: '🟡', title: 'Двойной угол и отрицательная область',
    prompt: 'Решите $\\cos2x=\\sin x$ для $x\\in[-\\pi,\\pi]$.',
    source: 'May 2023 TZ1 — Paper 1 — Q3 — 6 баллов', answerMode: 'roots', unit: 'radians', expected: [-Math.PI / 2, Math.PI / 6, 5 * Math.PI / 6],
    hint: 'Поскольку рядом $\\sin x$, выбери форму $\\cos2x=1-2\\sin^2x$. Не потеряй левую половину отрезка.',
    solution: '$2\\sin^2x+\\sin x-1=0$. Отсюда $\\sin x=1/2$ или $-1$, поэтому $-\\pi/2,\\pi/6,5\\pi/6$.',
  },
  {
    id: 'c3-06', skillId: 'double_angle_reduction', level: '🟡', title: 'Невозможный корень',
    prompt: 'Решите $2\\cos2\\theta-5\\cos\\theta+2=0$ для $\\pi\\leq\\theta\\leq2\\pi$.',
    source: 'May 2025 TZ3 — Paper 1 — Q3 — 5 баллов', answerMode: 'roots', unit: 'radians', expected: [3 * Math.PI / 2],
    hint: 'Рядом с $\\cos\\theta$ нужна форма через $\\cos^2\\theta$. Проверь, может ли найденное значение быть косинусом.',
    solution: '$4\\cos^2\\theta-5\\cos\\theta=0$. $\\cos\\theta=5/4$ невозможно; остаётся $\\cos\\theta=0$, то есть $3\\pi/2$.',
  },
  {
    id: 'c3-07', skillId: 'factor_not_divide', level: '🔴', title: 'Разложи, не сокращай',
    prompt: 'Графики $f(x)=\\cos x$ и $g(x)=\\sin2x$ пересекаются. Найдите все $x$ на $[0,\\pi]$.',
    source: 'May 2024 TZ1 — Paper 1 — Q4(a), область расширена — 3 балла', answerMode: 'roots', unit: 'radians', expected: [Math.PI / 6, Math.PI / 2, 5 * Math.PI / 6],
    hint: 'Не дели на $\\cos x$. Перенеси всё в одну часть и вынеси множитель.',
    solution: '$\\cos x-2\\sin x\\cos x=\\cos x(1-2\\sin x)=0$. Серия $\\cos x=0$ тоже даёт корень $\\pi/2$.',
  },
  {
    id: 'c3-08', skillId: 'reduce_to_tangent', level: '🔴', title: 'Однородное уравнение',
    prompt: 'Найдите корни $\\cos^2x-3\\sin^2x=0$ на $0\\leq x\\leq\\pi$.',
    source: 'November 2022 — Paper 1 — Q10(a) — 5 баллов', answerMode: 'roots', unit: 'radians', expected: [Math.PI / 6, 5 * Math.PI / 6],
    hint: 'После отдельной проверки $\\cos x=0$ можно получить уравнение для $\\tan^2x$. Не забудь знак $\\pm$.',
    solution: '$1-3\\tan^2x=0$, значит $\\tan x=\\pm1/\\sqrt3$. На отрезке получаются $\\pi/6$ и $5\\pi/6$.',
  },
  {
    id: 'c3-09', skillId: 'root_selection', level: '🔴', title: 'Экзаменационный сет: отбор корней',
    prompt: 'Решите $\\dfrac{2\\sin^22\\theta-5\\sin2\\theta-3}{\\sin2\\theta-1}=0$ для $0\\leq\\theta\\leq\\pi$, $\\theta\\ne\\pi/4$.',
    source: 'November 2021 — Paper 1 — Q6(b) — 5 баллов', answerMode: 'roots', unit: 'radians', expected: [7 * Math.PI / 12, 11 * Math.PI / 12],
    hint: 'Дробь равна нулю, когда числитель ноль, а знаменатель — нет. Сделай замену $u=\\sin2\\theta$.',
    solution: 'Числитель даёт $u=3$ или $u=-1/2$; остаётся $\\sin2\\theta=-1/2$. Ограничение исключает запрещённый корень.',
  },
  {
    id: 'c3-10', skillId: 'root_selection', level: '🔴', title: 'Посторонний корень',
    prompt: 'Решите $\\arccos x+\\arccos3x=\\dfrac{3\\pi}{2}$.',
    source: 'May 2025 TZ2 — Paper 1 — Q8(b) — 6 баллов', answerMode: 'value', unit: 'radians', expected: [-1 / Math.sqrt(10)],
    hint: 'Сначала область: $|3x|\\leq1$. После возведения в квадрат обязательна подстановка в исходное равенство.',
    solution: 'Кандидаты после преобразований нужно проверить в исходном уравнении. Остаётся только $x=-1/\\sqrt{10}$.',
  },
]
