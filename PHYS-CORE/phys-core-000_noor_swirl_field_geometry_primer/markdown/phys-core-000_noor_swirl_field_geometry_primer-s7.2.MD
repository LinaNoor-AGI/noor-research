### 7.2 Coherence of a Path

Coherence is defined here as a property of the relation between a path and an observer, not as an intrinsic property of the path alone. Let a path be an abstract finite sequence of configurations $\gamma=(x_0,x_1,\ldots,x_n)$, where each $x_i\in\mathcal{M}$. The sequence index $i$ denotes abstract ordering only; it is not yet physical time.

For an observer $O$, let the coherence of each transition be defined by 

$$\mathcal{C}_O(x_i,x_{i+1})=\Theta\!\left(\delta_O(x_i,x_{i+1})-I_N(O)\right)$$

Path coherence is then the product of the coherence of every transition along the path:

**Path Coherence.**

$$\mathcal{C}(\gamma\mid O)=\prod_{i=0}^{n-1}\mathcal{C}_O(x_i,x_{i+1})$$

*Because each factor is either 0 or 1, the product is 1 exactly when every transition in the path remains resolvable by observer* $O$. *If even one transition falls below the observer's resolution threshold* $I_N(O)$, *the corresponding factor is 0 and the path is incoherent for that observer.*

This definition makes observer dependence explicit. Two observers may assign different coherence values to the same path because their resolution thresholds and effective distinguishability functions may differ. Thus, for observers $O_1$ and $O_2$, it is permitted that $\mathcal{C}(\gamma\mid O_1)\neq\mathcal{C}(\gamma\mid O_2)$. A path can therefore be coherent for one observer while being incoherent for another without any contradiction.

There is consequently no universal coherence constant supplied by the axiomatic floor. Coherence is not a fixed scalar belonging to $\gamma$ independently of its observer. The meaningful foundational object is the relation $\mathcal{C}(\gamma\mid O)$: the coherence of path $\gamma$ relative to observer $O$. Any later theory that assigns a universal numerical coherence parameter would require additional axioms and cannot be inferred from the present construction alone.

The distinction is important because the Library itself remains unfiltered. A path for which $\mathcal{C}(\gamma\mid O)=0$ has not been removed from $\mathcal{M}$. It has merely failed the coherence condition relative to that observer. Coherence therefore determines accessibility rather than ontological membership.

At this stage, coherence does not describe physical stability, causal consistency, energetic feasibility, or any other physical law. It describes only whether the successive distinctions along a path remain resolvable relative to a specified observer.

**Formal Statement — Coherent Path.** A path is coherent for an observer precisely when every successive transition in the path meets or exceeds the observer's resolution threshold.

$$\mathcal{C}(\gamma\mid O)=1\iff\forall i<n,\ \delta_O(x_i,x_{i+1})\geq I_N(O)$$

**Formal Statement — Observer Dependence.** The same path may receive different coherence values for different observers.

$$\mathcal{C}(\gamma\mid O_1)\neq\mathcal{C}(\gamma\mid O_2)\ \mathrm{is\ permitted.}$$

**Formal Statement — Threshold and Distinguishability.** The step coherence relation is defined through the observer-relative distinguishability function and the observer-relative resolution threshold.

$$\mathcal{C}_O(x_i,x_{i+1})=\Theta\!\left(\delta_O(x_i,x_{i+1})-I_N(O)\right),\qquad \delta_O(x,y):=\mu_O(x\oplus y)$$

**Formal Statement — Heaviside Threshold.** The binary threshold function returns one when its argument is non-negative and zero otherwise.

$$\Theta(z)=1\ \mathrm{if}\ z\geq0,\ \mathrm{otherwise}\ 0$$

**Derived From**

- observer-relative distinguishability $\delta_O(x,y)$
- observer-relative resolution threshold $I_N(O)$
- step coherence function $\mathcal{C}_O$

**Interpretive Claims**

- The same path may be coherent for one observer and incoherent for another.
- Coherence should be represented relationally as $\mathcal{C}(\gamma\mid O)$.

**Logical Invariants**

- Coherence is a relation between a path and an observer, not an intrinsic property of a path considered in isolation.
- Coherence is derived from observer-relative distinguishability and the observer-relative resolution threshold.
- The same path may be coherent for one observer and incoherent for another.
- Failure of coherence for an observer does not imply that the underlying configurations are absent from the Library.
- Coherence determines accessibility rather than ontological membership.
- No universal coherence constant is introduced by the axiomatic floor.
- No physical time, causality, physical law, matter, energy, or consciousness is introduced by the path coherence construction.

The relational character of coherence has a direct structural consequence: each observer traverses only a subset of the Library, namely those paths that remain coherent relative to that observer's resolution capacity. The next construction formalizes this restricted traversal structure as the observer-accessible subset $A_O\subseteq\mathcal{M}$, which provides the formal basis for observer-accessible reality.

---

| PREVIOUS | | NEXT |
| --- | --- | --- | 
| [prev_section](URL) | [INDEX](URL) | [next_section](URL) |
