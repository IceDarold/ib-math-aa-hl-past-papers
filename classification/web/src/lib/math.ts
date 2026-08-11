export interface TextSegment {
  type: 'text' | 'math'
  value: string
}

const expressions: ReadonlyArray<readonly [string, string]> = [
  ['dy/dx - y = x', String.raw`\frac{dy}{dx}-y=x`],
  ['y(0)=2', String.raw`y(0)=2`],
  ['y=f(x)', String.raw`y=f(x)`],
  ['sqrt(6)', String.raw`\sqrt{6}`],
  ['u dot v = 3', String.raw`\mathbf u\cdot\mathbf v=3`],
  ['P(A union B) = P(A) + P(B) - P(A intersection B)', String.raw`\Pr(A\cup B)=\Pr(A)+\Pr(B)-\Pr(A\cap B)`],
  ["P(A' intersection B')", String.raw`\Pr(A'\cap B')`],
  ["P(B')", String.raw`\Pr(B')`],
  ['cos(2 theta) = 2cos^2(theta) - 1', String.raw`\cos(2\theta)=2\cos^2(\theta)-1`],
  ['S_n = n(u_1 + u_n)/2', String.raw`S_n=\frac{n(u_1+u_n)}{2}`],
  ['V = pi integral f(x)^2 dx', String.raw`V=\pi\int f(x)^2\,dx`],
  ['OP = OA + lambda AB', String.raw`\overrightarrow{OP}=\overrightarrow{OA}+\lambda\overrightarrow{AB}`],
  ['OP dot AB = 0', String.raw`\overrightarrow{OP}\cdot\overrightarrow{AB}=0`],
  ['tan(pi/4 - 2x) = 3', String.raw`\tan\!\left(\frac{\pi}{4}-2x\right)=3`],
  ['tan(pi/4 - theta)', String.raw`\tan\!\left(\frac{\pi}{4}-\theta\right)`],
  ['cos(2 theta)', String.raw`\cos(2\theta)`],
  ['sin(2 theta)', String.raw`\sin(2\theta)`],
  ['tan(theta)', String.raw`\tan(\theta)`],
  ['A = (1/2)r^2 theta', String.raw`A=\frac12 r^2\theta`],
  ['E(X) = sum xP(X=x)', String.raw`\operatorname{E}(X)=\sum_x x\Pr(X=x)`],
  ['E(c - 2X) = c - 2E(X)', String.raw`\operatorname{E}(c-2X)=c-2\operatorname{E}(X)`],
  ['|S_infinity - S_n| < 0.1', String.raw`\lvert S_\infty-S_n\rvert<0.1`],
  ['p(alpha) = alpha^n p(1/alpha)', String.raw`p(\alpha)=\alpha^n p\!\left(\frac1\alpha\right)`],
  ['p(1/alpha) = 0', String.raw`p\!\left(\frac1\alpha\right)=0`],
  ['p(x) = x^n p(1/x)', String.raw`p(x)=x^n p\!\left(\frac1x\right)`],
  ['u_(k+1) = r u_k - d', String.raw`u_{k+1}=ru_k-d`],
  ['C_n as (6000 - 10d)(1.1)^(n-1) + 10d', String.raw`C_n=(6000-10d)(1.1)^{n-1}+10d`],
  ['C_(n+1) - C_n = 0', String.raw`C_{n+1}-C_n=0`],
  ['D_(n+1) - D_n', String.raw`D_{n+1}-D_n`],
  ['D_(n+1) < D_n', String.raw`D_{n+1}<D_n`],
  ['-150(1.1)^(n-1)', String.raw`-150(1.1)^{n-1}`],
  ['T2 = 1.1T1 - 500', String.raw`T_2=1.1T_1-500`],
  ['(1.1)^(n-1)', String.raw`(1.1)^{n-1}`],
  ['-2 +/- sqrt(3)', String.raw`-2\pm\sqrt3`],
  ['x^2 + 1', String.raw`x^2+1`],
  ['1/i = -i', String.raw`\frac1i=-i`],
  ['p(alpha) = alpha^n', String.raw`p(\alpha)=\alpha^n`],
  ['x^(n+m)', String.raw`x^{n+m}`],
  ['n+m', String.raw`n+m`],
  ['p(1/x)', String.raw`p\!\left(\frac1x\right)`],
  ['p(x)', String.raw`p(x)`],
  ['x^3', String.raw`x^3`],
  ['x^2', String.raw`x^2`],
  ['x-values', String.raw`x\text{-values}`],
  ['x = -1', String.raw`x=-1`],
  ['alpha != 0', String.raw`\alpha\ne0`],
  ['1/alpha', String.raw`\frac1\alpha`],
  ['f = pq', String.raw`f=pq`],
  ['A =', String.raw`A=`],
  ['r^2', String.raw`r^2`],
  ['r theta', String.raw`r\theta`],
  ['uk = 0', String.raw`u_k=0`],
  ['sec^2', String.raw`\sec^2`],
  ['a dot b', String.raw`\mathbf a\cdot\mathbf b`],
  ['|a|^2', String.raw`\lVert\mathbf a\rVert^2`],
  ['|b|^2', String.raw`\lVert\mathbf b\rVert^2`],
  ['lambda', String.raw`\lambda`],
  ['theta = 2x', String.raw`\theta=2x`],
  ['V(r)', String.raw`V(r)`],
  ['dV/dr = 0', String.raw`\frac{dV}{dr}=0`],
  ["y' = 1 - y^2", String.raw`y'=1-y^2`],
  ["1 - y^2", String.raw`1-y^2`],
  ["y'''", String.raw`y'''`],
  ["y''", String.raw`y''`],
  ["y'", String.raw`y'`],
  ['x^6', String.raw`x^6`],
  ['x^3', String.raw`x^3`],
  ['pi/2', String.raw`\frac\pi2`],
  ['cis(pi/2)', String.raw`\operatorname{cis}\!\left(\frac\pi2\right)`],
  ['z^4 = 16i', String.raw`z^4=16i`],
  ['f(0)', String.raw`f(0)`],
  ['f(20)', String.raw`f(20)`],
  ['x f(x)', String.raw`x f(x)`],
  ['w = x + iy', String.raw`w=x+iy`],
  ['x - iy', String.raw`x-iy`],
  ['x^2 + y^2', String.raw`x^2+y^2`],
  ['|w|^2', String.raw`\lvert w\rvert^2`],
  ['ww*', String.raw`ww^*`],
  ['zw', String.raw`zw`],
  ['w*', String.raw`w^*`],
  ['|r| < 1', String.raw`\lvert r\rvert<1`],
  ['t = 100', String.raw`t=100`],
  ['t = 75', String.raw`t=75`],
  ['r = a + lambda b', String.raw`\mathbf r=\mathbf a+\lambda\mathbf b`],
  ['(0,0,z)', String.raw`(0,0,z)`],
  ['direction dot plane normal = 0', String.raw`\mathbf d\cdot\mathbf n=0`],
  ['k = 2', String.raw`k=2`],
  ["y' as 2 + 7/(x+2)^2", String.raw`y'=2+\frac7{(x+2)^2}`],
  ["y' <= 2", String.raw`y'\le2`],
  ["y' > 2", String.raw`y'>2`],
  ['T1', String.raw`T_1`],
  ['T2', String.raw`T_2`],
  ['n = 6', String.raw`n=6`],
  ['D_n <= 0', String.raw`D_n\le0`],
  ['C2 = C1', String.raw`C_2=C_1`],
  ['n = 1', String.raw`n=1`],
  ['n = k', String.raw`n=k`],
  ['u_(k+1)', String.raw`u_{k+1}`],
  ['u_k', String.raw`u_k`],
  ['x^2', String.raw`x^2`],
  ['-1', String.raw`-1`],
]

const expressionMap = new Map(expressions)
const expressionPattern = new RegExp(
  [...expressionMap.keys()]
    .sort((a, b) => b.length - a.length)
    .map(escapeRegExp)
    .join('|'),
  'g',
)

export function tokenizeMathText(text: string): TextSegment[] {
  const segments: TextSegment[] = []
  let cursor = 0

  for (const match of text.matchAll(expressionPattern)) {
    const index = match.index
    const source = match[0]
    if (index > cursor) segments.push({ type: 'text', value: text.slice(cursor, index) })
    segments.push({ type: 'math', value: expressionMap.get(source) ?? source })
    cursor = index + source.length
  }

  if (cursor < text.length) segments.push({ type: 'text', value: text.slice(cursor) })
  return segments.length > 0 ? segments : [{ type: 'text', value: text }]
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}
