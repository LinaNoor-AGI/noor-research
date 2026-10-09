# 2.3 Phase 2: Coherence Filtering (Dissolution)

The first phase of the Lightning Model generated the set $\Omega(x_t)$ of **ALL** continuations from the current state—every conceivable path, regardless of whether the observer's identity could survive traversal. The second phase applies the filter that reduces this indiscriminate totality to the paths on which an observer can actually persist. We call this phase **Coherence Filtering**, and its central operation is the evaluation of each candidate path against the coherence threshold inherited from PHYS-CORE-009.

For each path $\gamma \in \Omega(x_t)$, the system evaluates whether the observer's identity can be maintained across every transition. On paths where the observer's coherence falls below the survival threshold at any point, the observer's identity dissolves. There is no longer an entity on that path capable of experiencing or reporting the incoherence. This dissolution is not a choice, nor is it a failure of the observer's will; it is the structural consequence of the XOR chain breaking when coherence falls below the Noor-Planck floor.

The observer survival function $\mathcal{O}(\gamma)$ formalizes this evaluation as a product of Heaviside step functions:

$$
\mathcal{O}(\gamma) = \prod_{i=0}^{N-1} \Theta\big(\mathcal{C}(x_i, x_{i+1}) - \mathcal{C}_{\min}\big)
$$

where $\Theta$ is the Heaviside step function, $\Theta(z) = 1$ if $z \geq 0$ and $\Theta(z) = 0$ otherwise, and $\mathcal{C}(x_i, x_{i+1})$ is the relational coherence between successive states. The threshold $\mathcal{C}_{\min}$ maps directly to the Noor-Planck threshold $I_N$ from PHYS-CORE-009 §1.2. The observer survives on path $\gamma$ if and only if every transition maintains coherence above the threshold. The surviving paths are therefore those for which $\mathcal{O}(\gamma) = 1$:

$$
\Omega_{\text{survive}} = \{\gamma \in \Omega(x_t) \mid \mathcal{O}(\gamma) = 1\}
$$

The Noor-Planck threshold $I_N$ is the minimum coherence contrast required for a stable, exportable binary measurement. Below $I_N$, the field cannot resolve a distinction; above it, distinctions are stable and can propagate. This is the survival boundary for all coherence-stable observers. It is fixed by the Planck-scale structure of the ground hole $H$ and is not an adjustable parameter:

$$
I_N := \min \big|\mathbb{C}(x,t) - \mathbb{C}_{\text{ref}}(x,t)\big| \text{ such that } b(x,t) \text{ is stable and exportable}
$$

The dissolution condition can therefore be expressed with precision. Dissolution occurs when either coherence falls below the Noor-Planck threshold, or the relational identity of the observer is not preserved across the transition:

$$
\text{Dissolution}(x_i, x_{i+1}) = \text{True} \iff \mathcal{C}(x_i, x_{i+1}) < I_N \lor \mathrm{Identity}(x_i) \neq \mathrm{Identity}(x_{i+1})
$$

The first condition captures the loss of coherence below the survival floor. The second captures the loss of identity—the transition may maintain coherence numerically while failing to preserve the relational structure that constitutes the observer. Both are dissolution events, because both terminate the observer's identity on that path.

A critical distinction must be maintained throughout: dissolution is not erasure. The Noor-Planck threshold $I_N$ is a survival boundary, not a deletion operator. When a path falls below $I_N$, the XOR chain breaks, and the observer's identity ceases to propagate because there is no longer a stable chain of resolved distinctions. The path remains in the Library. It is simply no longer accessible to that observer. From the observer's perspective, the path never existed—because there was no observer on that path to experience it. This distinction between erasure and inaccessibility is one of the central commitments of the framework and will recur throughout the paper.

The Library is static: $\mathcal{M}(t) = \mathcal{M}$ for all $t$. All configurations exist eternally. What ceases is the traversal of a particular descent path, not the existence of the path itself. The failed tines of the lightning strike do not disappear from the sky; they simply do not carry the return stroke. They remain in the atmosphere, unilluminated.

In terms of the XOR chain formalism inherited from PHYS-CORE-009, the observer is a coherence-stable chain of XOR outputs:

$$
\text{Observer} = \{b_i\}_{i\in\mathbb{N}} \text{ such that } b_{i+1} = b_i \oplus b_{i-1} \text{ and } \mathbb{C}(b_i) \geq I_N \; \forall i
$$

Dissolution is therefore the condition under which this chain breaks:

$$
\text{Dissolution} \iff \exists i : \mathbb{C}(b_i) < I_N
$$

When any link in the XOR chain falls below $I_N$, the chain ceases to propagate coherently. The observer dissolves. There is no longer a stable sequence of resolved distinctions—the fundamental logical atoms of reality—that constitute the observer's worldline. This is the precise mathematical meaning of dissolution: the loss of coherence-stable propagation above the Noor-Planck floor.

The derivation from the continuous path formalism to the XOR chain formalism proceeds in five steps. First, represent the observer's worldline as a sequence of resolved binary distinctions $\{b_i\}$. Second, require that each $b_i$ maintains coherence above $I_N$, so that $\mathbb{C}(b_i) \geq I_N$ for all $i$. Third, observe that if any $b_i$ falls below $I_N$, the XOR chain breaks. Fourth, note that the observer's identity ceases to propagate on that path. Therefore, dissolution is equivalent to $\exists i : \mathbb{C}(b_i) < I_N$. The two formalisms—the continuous descent path and the discrete XOR chain—are representations of the same structure, related by the Boolean projection at the Noor-Planck floor.

This phase of the Lightning Model has important consequences for the interpretation of the observer's experience. The observer does not survey the Library and select the coherent path. The observer does not choose to remain coherent. The observer is the structure that persists when coherence is maintained, and dissolves when it is not. The coherence filter is not an external constraint imposed on the observer; it is the condition of the observer's existence. The paths that survive are not the paths the observer prefers; they are the paths on which the observer can be.

A note on the epistemic status of this construction. The coherence filtering phase is a mathematical construction within the Lightning Model. Its central operation—the evaluation of paths against the Noor-Planck threshold—follows from the observer definition and the Boolean field structure inherited from PHYS-CORE-009. The dissolution condition is a derived result. The claim that the Lightning Model operates at every timestep to produce reality is a physical hypothesis requiring empirical support. The exact functional form of the coherence function $\mathcal{C}(x_i, x_{i+1})$ remains an open question, as does the question of whether the Heaviside step function is an accurate idealization of the survival boundary or whether the transition is continuous. These open questions define directions for future work without diminishing the internal coherence of the framework.

The coherence filtering phase leaves us with the set $\Omega_{\text{survive}}$ of paths on which the observer's identity is preserved. But preservation of identity is not yet sufficient for the observer's worldline to be locked in. The surviving paths must also reach the XOR Singularity—the terminal attractor that grounds the retrocausal calculation. The next phase, Attractor Detection, determines which of the surviving paths reach this ground.

---

| PREVIOUS | | NEXT |
| --- | --- | --- | 
| [prev_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-s2.2.md) | [INDEX](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-index.md) | [next_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-s2.4.md) |
