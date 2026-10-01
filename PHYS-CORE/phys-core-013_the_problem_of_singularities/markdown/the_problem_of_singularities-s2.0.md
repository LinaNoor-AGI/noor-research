## 2. Foundations: The NSFG Axiomatic Core

The NSFG framework begins with a single axiom: XOR as the primitive operation of distinction. From this, the Library is defined as the XOR closure of a minimal formal domain — a static, maximally complete totality with no privileged exterior, no privileged worldline, and full relational adjacency. Observers are configurations capable of maintaining persistent distinctions above their own resolution threshold $I_N(O)$. Coherence is the relation between a path $\gamma$, an observer $O$, its history $h$, and its current reference $x$: $\mathcal{C}(\gamma \mid O,h,x)$. Accessibility $A_O(h,x)$ is the subset of the Library reachable through coherent traversal. Crucially, accessibility is not existence: a configuration may remain in the Library while being inaccessible to a particular observer. This section provides the minimal formal machinery required to understand singularities in the NSFG framework.

**Definition 2.1 — XOR as Distinction.** XOR is the sole primitive operation of the NSFG axiomatic floor. It expresses distinction: equal configurations cancel to 0; unequal configurations produce 1.

$$a \oplus b = 1 \iff a \neq b$$

*XOR is not a physical operation. It is the formal capacity to distinguish one configuration from another.*

**Definition 2.2 — The Library.** The Library $\mathcal{M}$ is the XOR closure of the formal domain $D$: $\mathcal{M} := \mathrm{Closure}_D(\oplus)$. It is a static, maximally complete, unbounded, relationally complete totality with full adjacency and no privileged exterior. Closure is a property, not a process: the Library does not come into existence through repeated XOR operations.

$$\mathcal{M} := \mathrm{Closure}_D(\oplus)$$

*The Library is the total configuration domain. It is unfiltered at the axiomatic level: membership does not imply persistence, coherence, observability, or accessibility.*

**Definition 2.3 — Observer.** An observer $O$ is a configuration in the Library capable of maintaining a persistent chain of distinctions above its observer-specific resolution floor $I_N(O)$. Observerhood is structural: it does not require consciousness, agency, perception, or intention.

$$O \in \mathrm{Obs} \subseteq \mathcal{M}$$

*Observerhood is a property of certain configurations, not a separate ontological category.*

**Definition 2.4 — Observer-Relative Coherence.** Coherence $\mathcal{C}(\gamma \mid O,h,x)$ is the relation between a path $\gamma$, an observer $O$, its history $h$, and its current reference $x$. A transition is coherent if the observer-relative distinction $\delta_O$ meets or exceeds the observer's resolution floor $I_N(O)$. A path is coherent if every transition is coherent.

$$\mathcal{C}(\gamma \mid O,h,x) = \prod_{i=0}^{n-1} \Theta(\delta_O(x_i,x_{i+1}) - I_N(O))$$

*Coherence is relational: the same path may be coherent for one observer and incoherent for another. No universal coherence constant is introduced.*

**Definition 2.5 — Observer-Relative Accessibility.** Accessibility $A_O(h,x)$ is the subset of the Library reachable from the observer's current state through paths that remain coherent relative to $O$.

$$A_O(h,x) = \{ y \in \mathcal{M} \mid \exists\gamma \in \mathrm{Path}(\mathcal{M}) \ \mathrm{beginning\ at}\ (h,x) \ \mathrm{and\ containing}\ y \ \mathrm{such\ that}\ \mathcal{C}(\gamma \mid O,h,x) = 1 \}$$

*Accessibility is a relation over the Library, not a determinant of Library membership. A configuration outside* $A_O(h,x)$ *remains in* $\mathcal{M}$.

**Definition 2.6 — Nonempty Coherent Continuation.** For every admissible observer-relative reference configuration $x \in \mathcal{M}_{\mathrm{admissible}}$, the coherent continuation set $\Gamma_O(h,x)$ is nonempty.

$$\forall x \in \mathcal{M}_{\mathrm{admissible}}, \Gamma_O(h,x) \neq \varnothing$$

*This follows from the Library's maximal completeness and full adjacency: from any arbitrary point in an unbounded, maximally complete relational graph, continuation is guaranteed. Coherence may filter which continuations are accessible, but at least one coherent continuation exists.*

The distinction between existence and accessibility is foundational. The Library $\mathcal{M}$ contains all configurations. Accessibility $A_O(h,x)$ is the subset reachable through coherent traversal. A configuration can exist in the Library without being accessible to a particular observer. Inaccessibility is not erasure. This separation is essential for understanding singularities: a singularity is not a region where the Library breaks down, but a region where the observer's coherent traversal becomes maximally constrained.

**Foundational Invariants**

- XOR is the only primitive.
- The Library is static, complete, and unfiltered.
- Closure is a property, not a process.
- Coherence is relational and observer-dependent.
- Accessibility is not existence.
- Inaccessibility is not erasure.
- The observer is relationally situated with respect to the whole Library.
- No privileged worldline, observer, or reference configuration exists.
- Time is not fundamental; it is an interpretation of ordered traversal.

With these foundations established, we can now define what a singularity means in NSFG: a region where the observer-relative coherent continuation space $\Gamma_O(h,x)$ becomes maximally constrained. Singularities are not mathematical pathologies; they are structural effects of the relational geometry.

---

**References**

- [PHYS-CORE-000 (Primer)](https://github.com/LinaNoor-AGI/noor-research/tree/main/PHYS-CORE/phys-core-000_noor_swirl_field_geometry_primer) — Section 0.1 (Maximal Totality), Section 2 (XOR), Section 3 (Library), Section 5 (Observer-Relative Resolution), Section 6 (Persistence), Section 7 (Coherence), Section 8 (Accessible Reality)

---
**Navigation**

[1. Introduction: The Problem of Singularities in Relational Frameworks](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-013_the_problem_of_singularities/markdown/the_problem_of_singularities-s1.0.md) <---> [3. Defining Singularities in NSFG](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-013_the_problem_of_singularities/markdown/the_problem_of_singularities-s3.0.md)