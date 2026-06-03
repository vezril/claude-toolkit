# Core quantities & inequalities

*Elements of Information Theory* (Cover & Thomas), Ch. 2 (+ 8 for the continuous case). Definitions and intuition; proofs are in the book. Logs are base 2 → units are **bits** (base e → nats). Convention `0 log 0 = 0`.

## Entropy

`H(X) = −Σ_x p(x) log p(x) = E[−log p(X)]` — the average uncertainty in `X`, or the minimum average bits to describe it. Properties: `H(X) ≥ 0`; `H(X) ≤ log|𝒳|` with equality iff `X` is uniform (max uncertainty); `H(X) = 0` iff `X` is deterministic. `−log p(x)` is the **surprise / information content** of outcome `x` (rare = surprising = more bits).

## Joint & conditional entropy

- **Joint** `H(X,Y) = −Σ p(x,y) log p(x,y)`.
- **Conditional** `H(Y|X) = Σ_x p(x) H(Y|X=x) = −Σ p(x,y) log p(y|x)` — remaining uncertainty in `Y` after seeing `X`.
- **Chain rule** `H(X,Y) = H(X) + H(Y|X)` (extends to `H(X₁,…,Xₙ) = Σ H(Xᵢ | X₁…X_{i−1})`).
- Conditioning reduces entropy *on average*: `H(Y|X) ≤ H(Y)` (but a *specific* `X=x` can raise it).

## Relative entropy (KL divergence)

`D(p‖q) = Σ_x p(x) log( p(x)/q(x) ) = E_p[log(p/q)]` — the inefficiency (extra bits) of assuming the distribution is `q` when it's really `p`. Key facts: `D(p‖q) ≥ 0`, `= 0` iff `p = q` (Gibbs' / information inequality); **asymmetric** (`D(p‖q) ≠ D(q‖p)`) and not a metric (no triangle inequality). The workhorse "distance between distributions" in stats and ML.

## Mutual information

`I(X;Y) = Σ p(x,y) log( p(x,y)/(p(x)p(y)) ) = D(p(x,y) ‖ p(x)p(y))`.
Equivalent forms: `I(X;Y) = H(X) − H(X|Y) = H(Y) − H(Y|X) = H(X) + H(Y) − H(X,Y)`. It's the information `Y` carries about `X` (and vice versa — **symmetric**), `≥ 0`, and `= 0` iff `X ⟂ Y`. Note `I(X;X) = H(X)` (self-information = entropy). Conditional `I(X;Y|Z)` and a chain rule exist too.

## Cross-entropy

`H(p,q) = −Σ p(x) log q(x) = H(p) + D(p‖q)` — bits to encode samples from `p` using a code optimal for `q`. Minimizing cross-entropy over `q` ≡ minimizing `D(p‖q)` (since `H(p)` is fixed) — this is why **cross-entropy is the standard ML loss**.

## Differential entropy (continuous)

`h(X) = −∫ f(x) log f(x) dx`. Caveats vs discrete entropy: it **can be negative**, isn't invariant under change of variables (`h(aX) = h(X) + log|a|`), and isn't a limit of `H`. But **KL and mutual information carry over cleanly** to the continuous case and keep their meaning. Among densities with a given variance, the **Gaussian maximizes** differential entropy (`h = ½ log(2πe σ²)`).

## Inequalities you actually use

- **Jensen's inequality** — for convex `φ`, `E[φ(X)] ≥ φ(E[X])`. The lever behind `D ≥ 0`, `I ≥ 0`, and the entropy bounds.
- **Log-sum inequality** — `Σ aᵢ log(aᵢ/bᵢ) ≥ (Σaᵢ) log(Σaᵢ/Σbᵢ)`; gives convexity of `D` and concavity of `H`.
- **Data-processing inequality** — if `X → Y → Z` is a Markov chain, `I(X;Z) ≤ I(X;Y)`: **you can't create information about `X` by processing `Y`** (post-processing/feature transforms can only lose info). Foundational for ML and for reasoning about pipelines/anonymization.
- **Fano's inequality** — if you estimate `X` from `Y` with error probability `Pₑ`, then `H(X|Y) ≤ H(Pₑ) + Pₑ log(|𝒳|−1)`: **low conditional entropy is necessary for reliable guessing**; bounds achievable error from below. Central to converse (impossibility) proofs.
- **Sufficient statistics** — `T(X)` is sufficient for a parameter `θ` iff `I(θ; X) = I(θ; T(X))` (it preserves all the information about `θ`); the data-processing inequality makes "no statistic beats a sufficient one" precise.

These quantities are pure functions of distributions — easy to compute as folds over a `Map[A, Double]` for instrumentation (entropy of a keyspace/tag distribution, KL between expected vs observed, mutual information between two columns).
