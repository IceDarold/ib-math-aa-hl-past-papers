# Ручной пилот классификации - November 2024

## Что разобрано

Полностью вручную сопоставлены question papers и markschemes сессии November 2024, Common:

| Paper | Вопросов | Классифицируемых блоков | Баллов | Calculator |
| --- | ---: | ---: | ---: | --- |
| Paper 1 | 12 | 29 | 110 | No |
| Paper 2 | 12 | 35 | 110 | Yes |
| Paper 3 | 2 | 19 | 55 | Yes |
| **Итого** | **26** | **83** | **275** | - |

Классифицируемый блок обычно соответствует подпункту. Если IB назначает общий балл сразу нескольким подпунктам, они сохранены одним блоком, например `Q11 b(i-ii)`. Это позволяет не придумывать отсутствующее в markscheme распределение баллов.

## Как представляется метод решения

Одного тематического тега недостаточно. Для каждого блока используются три слоя:

1. `method_tags` - атомарные операции: `quotient_rule`, `discriminant_condition`, `compare_coefficients`.
2. `method_path` - порядок операций, фактически подтверждённый markscheme.
3. `accepted_alternatives` - другие полноценные маршруты, которые принимает IB.

Например, `Paper 1, Q10(b-d)` имеет тему `calculus.optimization`, но полный метод выглядит так:

```text
surface-area constraint
-> eliminate h
-> form V(r) as outer volume minus inner volume
-> differentiate V(r)
-> solve V'(r) = 0
-> substitute the critical value
```

Именно такой маршрут полезнее для подбора похожих заданий, чем общий тег `calculus`.

## Обзор Paper 1

| Q | Marks | Основные темы | Характерный метод решения |
| --- | ---: | --- | --- |
| 1 | 5 | Circular measure | Sector-area formula -> solve radius -> arc length -> perimeter |
| 2 | 6 | Probability | Inclusion-exclusion -> complements -> conditional probability |
| 3 | 4 | Algebraic proof | Difference of squares or expansion -> factor 12 -> divisibility conclusion |
| 4 | 6 | Trigonometry | Cosine rule -> double-angle identity -> exact radical simplification |
| 5 | 6 | Arithmetic sequences | Term and sum formulae -> simultaneous equations -> solve `u_k = 0` |
| 6 | 5 | Quadratics, inverse functions | Critical roots and sign analysis -> vertex -> one-to-one domain restriction |
| 7 | 7 | Trigonometric functions, integration | Endpoint/range analysis -> volume-of-revolution integral -> `sec^2` antiderivative |
| 8 | 8 | Vectors | Section formula -> perpendicular dot product -> expand with norms -> solve parameter |
| 9 | 9 | Trigonometric identities and equations | Tangent difference -> sine/cosine conversion -> conjugate -> solve transformed equation |
| 10 | 17 | Geometry, optimization | Surface decomposition -> constraint elimination -> objective function -> stationary point |
| 11 | 17 | Limits, differentiation, series | Limit -> quotient rule -> implicit higher derivatives -> Maclaurin coefficients |
| 12 | 20 | Complex numbers | De Moivre roots -> root ratio -> Argand geometry -> conjugation -> integer argument condition |

## Обзор Paper 2

| Q | Marks | Основные темы | Характерный метод решения |
| --- | ---: | --- | --- |
| 1 | 7 | Function graphing | GDC evaluation -> numerical roots -> maximum and feature-based sketch |
| 2 | 4 | Binomial theorem | General term -> select required power -> extract coefficient |
| 3 | 5 | Discrete random variables | Normalize probabilities -> weighted expectation |
| 4 | 8 | Trigonometric geometry | Gradient-to-angle conversion -> symmetry -> right-triangle lengths |
| 5 | 5 | Logarithmic domain, quadratics | Require positive argument for all real `x` -> discriminant condition -> parameter inequality |
| 6 | 8 | Continuous random variables | Piecewise expectation integral -> linearity of expectation -> CDF median equation |
| 7 | 6 | Combinatorics | Complement counting and consecutive-block arrangements |
| 8 | 6 | Complex numbers | Conjugate-modulus proof -> eliminate `w` -> complex division |
| 9 | 7 | Geometric sequences | Convergence condition -> infinite sum -> remainder inequality -> least integer `n` |
| 10 | 15 | Regression and population models | Regression -> extrapolation check -> model evaluation -> numerical optimization -> rate interpretation |
| 11 | 18 | 3D vectors | Line parametrization -> point-line distance -> line-in-plane test -> constrained direction vector |
| 12 | 21 | Rational functions and calculus | Quotient rule -> discriminant -> asymptotes -> derivative inequality -> curve sketch |

## Обзор Paper 3

| Q | Marks | Основные темы | Характерный метод решения |
| --- | ---: | --- | --- |
| 1 | 27 | Recurrences and sequences | Iterate recurrence -> derive closed form -> first differences -> logarithmic threshold -> equilibrium -> induction |
| 2 | 28 | Palindromic polynomials | Exact quadratic roots -> reciprocal-root proofs -> polynomial identity -> coefficient comparison -> factor and solve |

## Что показал пилот

- Тема и метод действительно независимы. `discriminant_condition`, например, появляется и в задаче о логарифмической области определения, и в задаче о стационарных точках рациональной функции.
- Метод нужно хранить как упорядоченный маршрут, а не как неупорядоченный набор тегов.
- Альтернативные решения из markscheme нельзя смешивать с основным маршрутом. Они должны храниться отдельно.
- Для proof-вопросов важно различать тип доказательства: direct algebraic proof, identity proof, contradiction, root-pair argument, mathematical induction.
- GDC является частью метода, а не просто свойством Paper 2/3: нужно различать `numerical_root`, `numerical_maximum`, `regression`, `numerical_derivative` и использование графика только для проверки.
- Вопрос целиком может быть межтематическим. Наиболее точная единица классификации - отдельно оценённый подпункт, при сохранении связи с родительским вопросом.

## Файлы пилота

- `questions.tsv` - 83 вручную размеченных блока с темами, операциями, порядком решения и альтернативами.
- `../../taxonomy/topics.yaml` - тематическая иерархия, использованная в пилоте.
- `../../taxonomy/method-families.yaml` - предлагаемые крупные семейства методов.

Перед массовой обработкой нужно согласовать две вещи: достаточна ли такая глубина `method_tags` и хотим ли мы считать альтернативные методы отдельными searchable-классами.

