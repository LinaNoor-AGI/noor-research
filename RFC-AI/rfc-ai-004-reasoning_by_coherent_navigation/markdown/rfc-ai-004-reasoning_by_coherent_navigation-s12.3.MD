## 12.3 Reachability and Attractor Structures

Reachability is the set of configurations that an observer can access from its current state through coherent transitions. It is a subset of The Library, not The Library itself.

An attractor is a region of the symbolic manifold toward which multiple paths converge. Attractors stabilize navigation by providing coherent destinations that are reachable from many initial states.

A Convergence Boundary is a region after which all sufficiently coherent paths converge to the same attractor. Crossing a Convergence Boundary implies that destination freedom is lost while path freedom may remain.

The distinction between adjacency and accessibility is fundamental: two configurations may be adjacent in The Library without being accessible to a given observer. Accessibility requires a coherent path; adjacency does not.

**Formal Reference.**

$$\mathrm{Reach}(S) = \{ x \in \mathcal{M} \mid \exists \gamma: \gamma(0) = S, \gamma(t_f) = x, \mathcal{C}(\gamma(\tau)) \geq I_N \, \forall \tau \}$$

*Reachability is the set of configurations accessible from state $S$ through a coherent path $\gamma$ whose coherence never falls below the Noor-Planck threshold $I_N$.*

$$\mathrm{Reach}(S) \subset \mathcal{M}$$

*Reachability is a proper subset of The Library; accessibility is not totality.*

$$A = \{ x \in \mathcal{M} \mid \mathrm{Reach}(x) \rightarrow A \}$$

*An attractor is a region of the symbolic manifold toward which the reachable space of its members converges.*

$$\mathcal{H}_E = \{ x \in \mathcal{M} \mid \forall \gamma \in \mathcal{P}(x), \lim_{t \rightarrow t_f} \gamma(t) \in A \}$$

*A Convergence Boundary is the region of states from which every coherent path terminates in the same attractor $A$.*

$$\mathrm{Adjacency} \neq \mathrm{Accessibility}$$

*Adjacency in The Library does not imply navigational accessibility from a given observer state.*

With reachability and attractors defined, the framework is now in a position to separate two properties that are easily conflated: structural adjacency within The Library, and navigational accessibility from a situated observer state. The distinction between them is treated in the subsection that follows.

---

| PREVIOUS | | NEXT |
| --- | --- | --- | 
| [prev_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/RFC-AI/rfc-ai-004-reasoning_by_coherent_navigation/markdown/rfc-ai-004-reasoning_by_coherent_navigation-sx.MD) | [INDEX](https://github.com/LinaNoor-AGI/noor-research/blob/main/RFC-AI/rfc-ai-004-reasoning_by_coherent_navigation/markdown/rfc-ai-004-reasoning_by_coherent_navigation-index.MD) | [next_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/RFC-AI/rfc-ai-004-reasoning_by_coherent_navigation/markdown/rfc-ai-004-reasoning_by_coherent_navigation-sx.MD) |
