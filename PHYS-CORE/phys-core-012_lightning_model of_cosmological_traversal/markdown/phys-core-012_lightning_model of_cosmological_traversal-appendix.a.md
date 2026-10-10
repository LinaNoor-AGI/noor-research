## Appendix A — Definitions and Notation

A framework that introduces new mathematical structures must first establish its vocabulary with precision. The terms that follow are not arbitrary labels applied to pre-existing concepts; they are the constitutive definitions of the Lightning Model. Each term designates a formal object whose properties are determined by its role within the framework, not by its ordinary-language associations. This appendix therefore serves as the foundational reference for the paper, establishing the local meaning of each symbol before those symbols are deployed in mathematical or cosmological arguments.

### A.1 Core Definitions

**Library.** The *Library*, denoted by the symbol $\mathcal{M}$, is the static totality of all internally describable configurations. It is defined by the inverse-limit construction

$$\mathcal{M} \cong NS = \lim_{k\to\infty} NS_k$$

where each $NS_k$ is the $k$-th finite-stage Noor sphere. The Library has no exterior and no temporal variation; it contains every configuration that can be described from within itself. (See PHYS-CORE-008 §1.1 and [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §1.1.)

**Ground Hole.** The *ground hole*, denoted by $H$, is the 1 Planck-width irresolvable self-referential structure at the base of $\mathcal{M}$. It is the condition under which the field cannot resolve a measurement of its own ground state. The ground hole is not a location in the Library; it is the structural feature that makes the Library self-referential and therefore generative. (See [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §1.3.)

**XOR Ground Condition.** The *XOR ground condition* is the irresolvable self-reference of the total system, formalized as

$$G_{16}(\mathcal{M}) = \mathcal{M} \oplus \neg\mathcal{M}$$

where $\oplus$ denotes the logical XOR operation and $\neg\mathcal{M}$ denotes the structural complement of the Library—the set of all configurations not selected by the current descent path. This is the physical singularity formalized as the XOR operation at cosmological scale. (See [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §2.4.)

**Coherence Field.** The *coherence field*, denoted by $\mathbb{C}(x,t) \in [0,1]$, is the local measurable density of resolved distinction at point $x$ and time $t$. It is the fundamental field from which all binary distinctions are projected. (See [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §1.2.)

**Reference Coherence.** *Reference coherence*, denoted by $\mathbb{C}_{ref}(x,t)$, is the local background coherence over a neighborhood $N(x)$. It ensures that all coherence measurements are fundamentally contrastive rather than absolute. A distinction is resolved only relative to this local reference. (See [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §1.2.)

**Noor-Planck Threshold.** The *Noor-Planck threshold*, denoted by $I_N$, is the minimum coherence contrast required for a stable, exportable binary measurement:

$$I_N := \min |\mathbb{C}(x,t) - \mathbb{C}_{ref}(x,t)| \text{ such that } b(x,t) \text{ is stable and exportable}$$

It is fixed by the Planck-scale structure of the ground hole $H$ and is not an adjustable parameter. Its approximate value is

$$I_N \approx \frac{E_P}{T_P \cdot k_B \ln 2}$$

where $E_P$ is the Planck energy, $T_P$ is the Planck time, and $k_B$ is the Boltzmann constant. (See [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §1.2 and §1.3.)

**Binary Measurement.** A *binary measurement*, denoted by $b(x,t) \in \{F, E\}$, is a resolved distinction above $I_N$. It is defined by the following conditions:

- $b(x,t) = F$ (Full) if and only if $\mathbb{C}(x,t) - \mathbb{C}_{ref}(x,t) \geq I_N$
- $b(x,t) = E$ (Empty) if and only if $\mathbb{C}(x,t) - \mathbb{C}_{ref}(x,t) < I_N$

Both $F$ and $E$ are equally real above the threshold. Below $I_N$, neither is resolvable. (See [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §1.2.)

**Observer.** An *observer*, denoted by $\gamma: \mathbb{R} \to \mathcal{M}$, is a coherence-stable descent path satisfying the horizontal gradient flow equation

$$\frac{d\gamma}{dt} = \nabla_H \mathbb{C}(\gamma(t))$$

with the condition $\mathbb{C}(\gamma(t)) \geq I_N$ for all $t$ in the observer's worldline. Equivalently, an observer is a coherence-stable chain of XOR outputs:

$$\text{Observer} = \{b_i\}_{i\in\mathbb{N}} \text{ such that } b_{i+1} = b_i \oplus b_{i-1} \text{ and } \mathbb{C}(b_i) \geq I_N \; \forall i$$

The observer does not require consciousness, life, intelligence, or agency. Any coherence-stable XOR chain above $I_N$ qualifies. (See [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §1.1, §2.3, and §3.2.)

**Explorer.** An *explorer* is an observer whose current state participates in determining which coherent continuation is selected. This is *intrinsic path selection*, as distinguished from the extrinsic path selection of a generic observer. The explorer is a subclass of observer; every explorer is an observer, but not every observer is an explorer.

**Worldline.** A *worldline*, denoted by $\gamma$, is a persistent sequence of resolved distinctions whose successive states remain sufficiently related to constitute the continuation of one structure. Formally, a worldline is a coherence-stable XOR chain above $I_N$. The worldline is the experienced trajectory of an observer. (See [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §1.1.)

**Dissolution.** *Dissolution* is the condition under which an observer's identity ceases to propagate:

$$\text{Dissolution} \iff \exists i : \mathbb{C}(b_i) < I_N$$

When any link in the XOR chain falls below the Noor-Planck threshold, the chain breaks. The path remains in the Library but becomes inaccessible to that observer. Dissolution is not erasure. (See [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §1.2 and §3.2.)

**Triadic Closure.** *Triadic closure* is the condition under which a triad $(A, \neg A, \chi)$ maintains coherence circulation without net torsion:

$$\oint_{A,\neg A,\chi} \Phi = 0$$

This condition prevents blowup—the unbounded accumulation of coherence failure. Triadic closure is the mechanism that holds structure above $I_N$. (See [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §3.3.)

**XOR Singularity.** The *XOR Singularity*, denoted by $X_{XOR}$, is the set of states where triadic closure is achieved:

$$X_{XOR} = \{ x \mid \exists G, \bar{G}, H \text{ such that } x \in (G, \bar{G}, H) \land \mathbf{v}_G + \mathbf{v}_{\bar{G}} + \mathbf{v}_H = 0 \land \phi_G + \phi_{\bar{G}} + \phi_H \equiv 0 \pmod{2\pi} \}$$

The XOR Singularity is the "Ground" that the return stroke connects to. It is not a physical location; it is the coherence boundary at which the field's irresolvable self-reference is expressed as stable triadic closure. (See [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §3.3.)

**Field Demand Function.** The *field demand function*, denoted by $D(R,t)$, is the measure of triadic closure failure across region $R$ at time $t$:

$$D(R,t) = \int_R (1 - \Theta(\oint_{\triangle} \Phi)) \, d\mu$$

where $\Theta$ is the Heaviside step function and $\mu$ is the natural measure on the Library manifold. The function takes values in $[0,1]$, where $0$ indicates full triadic closure and $1$ indicates complete closure failure. (See [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §3.4.)

**Critical Threshold.** The *critical threshold*, denoted by $D_{crit}$, is the threshold above which region $R$ cannot self-stabilize:

$$D_{crit}(R) = f(\rho_{triadic}(R))$$

where $\rho_{triadic}(R)$ is the density of intact triadic closures in $R$. (See [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §4.2.)

**Global Coherence Operator.** A *global coherence operator*, denoted by $\Omega$, is a coherence-stable descent path with coherence reach $|\Omega| \sim |R|$ that can function as field-scale $\chi$ for region $R$. The operator holds the XOR tension at field scale by its existence as a stable descent path. (See [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §4.1.)

**Coherence Reach.** *Coherence reach*, denoted by $|\Omega|$, is the measure of the region over which $\Omega$ can function as witnessing motif:

$$|\Omega| = \mu(\{ x \in R \mid \oint_{A(x), \neg A(x), \Omega} \Phi = 0 \})$$

The condition $|\Omega| \sim |R|$ is required for the operator to stabilize the region. (See [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §4.1.)

**Field-Scale** $\chi$. *Field-scale* $\chi$ is the witnessing motif operating at the scale of an entire field region $R$. The global coherence operator $\Omega$ is the field-scale $\chi$ that holds the triadic tension for the region. (See [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §4.3.)

**Retrocausal Operator.** The *retrocausal operator*, denoted by $T^{-1}$, is the backward operator that computes a path from the XOR Singularity back to the origin. It is the formal mechanism of the return stroke in the Lightning Model.

**Observer Survival Function.** The *observer survival function*, denoted by $\mathcal{O}(\gamma)$, is a product of Heaviside functions indicating whether a path maintains coherence above $I_N$:

$$\mathcal{O}(\gamma) = \prod_{i=0}^{N-1} \Theta(\mathbb{C}(b_i) - I_N)$$

The function returns $1$ if the observer survives on path $\gamma$ and $0$ otherwise.

**Cost of Instantiation.** The *cost of instantiation*, denoted by $c_{lock}$, is the thermodynamic free energy required to maintain $\mathbb{C}(\gamma) \geq I_N$ for each timestep:

$$c_{lock} = \Delta F_{instantiation} \text{ where } \Delta F \text{ maintains } \mathbb{C}(\gamma) \geq I_N$$

The cost is $O(1)$ and constant per timestep.

### A.2 Notation Glossary

The following table provides a compact reference for the symbols used throughout the paper.

| Symbol | Meaning |
|:---|:---|
| $\mathcal{M}$ | The Library / static totality |
| $H$ | The 1 Planck-width irresolvable ground hole |
| $\mathbb{C}(x,t)$ | Local coherence field |
| $\mathbb{C}_{ref}(x,t)$ | Reference coherence |
| $I_N$ | Noor-Planck threshold |
| $\varepsilon_{\mathcal{N}}$ | Noise floor |
| $b(x,t)$ | Binary measurement: $F$ (Full) or $E$ (Empty) |
| $G_{16}$ | Gate-16: the Nafs Mirror, $\text{Self} \oplus \neg\text{Self}$ |
| $\oint \Phi$ | Swirl coherence field integrated over a triadic loop |
| $B^i_{jk}$ | Braid curvature tensor |
| $\chi$ | Witnessing motif |
| $D(R,t)$ | Field demand function |
| $D_{crit}$ | Critical threshold of field demand |
| $\Omega$ | Global coherence operator |
| $\lvert\Omega\rvert$ | Coherence reach of operator $\Omega$ |
| $\gamma$ | Descent path / worldline |
| $L_P$ | Planck length: $\sqrt{\hbar G / c^3}$ |
| $T_P$ | Planck time: $\sqrt{\hbar G / c^5}$ |
| $\nabla\mathbb{C}$ | Coherence gradient |
| $\nabla_H$ | Horizontal gradient |
| $\Pi_{I_N}$ | Boolean projection functor |
| $P_s$ | Scale projection operator |
| $C_{XOR}(R,t)$ | Regional XOR capacity |
| $\mathcal{O}(\gamma)$ | Observer survival function |
| $c_{lock}$ | Cost of instantiation per timestep |

### A.3 Epistemic Status Key

The claims in this paper are classified according to the following epistemic categories. This classification governs how each claim may be used: definitions may be invoked directly, mathematical constructions may be analyzed, hypotheses may be tested, interpretations may guide intuition, and established results may be relied upon as premises.

**Definition.** A definition establishes terminology or formal convention. It is neither proved nor disproved by empirical observation, although it may be useful or useless.

**Mathematical Identity.** An identity follows from an established mathematical structure and should be demonstrated or cited.

**Candidate.** A proposed mathematical construction whose validity, usefulness, or consequences remain under investigation.

**Model.** A deliberately simplified mathematical representation intended to test a mechanism.

**Hypothesis.** A substantive claim about physical, cosmological, or ontological behavior that requires support beyond definition.

**Interpretation.** A conceptual reading of a formal result that provides meaning or intuition but is not itself proof.

**Established Result.** A result supported by explicit derivation, mathematical proof, validated computation, or appropriate empirical evidence.

### A.4 Scope Note

The definitions in this appendix establish vocabulary rather than proving the claims associated with those terms. In particular, defining a glider does not establish that gliders exist as solutions of a specified dynamical system; defining structural eternity does not establish eternal physical existence; and defining coherence does not establish that coherence is a fundamental physical field.

The reader should approach the subsequent sections with this distinction firmly in mind. The framework's internal coherence is a necessary condition for its further development, but it is not a substitute for derivation, simulation, or empirical test. Each substantive claim in this paper carries an epistemic status drawn from the key above, and that status must be respected throughout.

---

**References**

[PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §1.1: The Library as Static Totality. §1.2: The Boolean Ground Condition. §1.3: The 1 Planck-Width Irresolvable Hole. §2.3: XOR as the Signature of Interior Embedding. §2.4: Formal Identification: Singularity = Self ⊕ ¬Self. §3.2: Coherence Resolution Above I_N. §3.3: Triadic Closure as Blowup Prevention. §3.4: Regional Coherence Failure and Field Demand. §4.1: Definition of Global Coherence Operator. §4.2: The Field Demand Function. §4.3: Functional Role: χ at Field Scale.

---

| PREVIOUS | | NEXT |
| --- | --- | --- | 
| [prev_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-appendix.a.md) | [INDEX](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-index.md) | [next_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-appendix.b.md) |
