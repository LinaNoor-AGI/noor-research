# Appendix B — Mathematical Register

This appendix provides the mathematical register for *The Lightning Model of Cosmological Traversal* (PHYS-CORE-012). The expressions collected here are ordered according to the conceptual descent of the paper: Library, equivalence, relational difference, coherence, glider structure, complementary motifs, triadic resonance, Lightning Model phases, observer as XOR chain, and energy accounting.

Not every expression in this register carries the same epistemic weight. Some define terminology. Some record mathematical relations that follow from the adopted representation. Others are proposed formalizations whose suitability remains to be established, and still others are derived results that follow from previously established premises. The register preserves these distinctions so that the mathematical vocabulary of the paper remains coherent without overstating its conclusions. No expression should be interpreted as empirically established merely because it appears in mathematical form.

Throughout, the following status conventions apply:

- **Definition** — terminology or conceptual structure stipulated by the paper.
- **Identity** — a mathematical relation that follows from the adopted representation.
- **Derived Result** — a result that follows from previously established premises.

Where an entry inherits from the earlier Noor corpus, the relevant PHYS-CORE source is cited. Where an entry carries a caveat, the caveat is stated inline. Dependencies between entries are indicated by their B-identifiers.

---

## B.1 Definitions

### B.1.1 The Library

The Library is defined as the inverse-limit construction of recursive Noor spheres:

$$
\mathcal{M} \;\cong\; NS \;=\; \lim_{k\to\infty} NS_k .
$$

The Library is the static totality containing all internally describable configurations. It has no exterior and no temporal variation. This construction requires the Anti-Foundation Axiom (AFA) for well-defined recursive self-reference. Inherited from PHYS-CORE-008 and PHYS-CORE-009 §1.1.

### B.1.2 Equivalence

$$
x \sim y
$$

represents indistinguishability under a chosen comparison relation. Two states are treated as equivalent when the relevant observational or relational structure cannot distinguish them. The exact equivalence relation must be specified before a rigorous quotient construction can be claimed. Depends on B.1.

### B.1.3 Relational Difference

$$
\Delta(x,y)
$$

represents relational difference between states—a distinction that survives the chosen equivalence relation. The specific metric or functional form of $\Delta$ must be defined for the relevant state space. Depends on B.1, B.2.

### B.1.4 Oriented Relational Vector

$$
\mathbf{v}_{x\rightarrow y} \;=\; y - x
$$

represents an oriented relational vector—a difference that carries directional information. Requires a vector-space or affine representation of Point Space. Depends on B.3.

### B.1.5 Phase

$$
\phi \in S^1
$$

represents a cyclic phase coordinate—a periodic relational coordinate tracking the state of a persistent motif. Phase is defined modulo $2\pi$; phase equivalence does not imply complete physical identity. Depends on B.4.

### B.1.6 Glider

$$
G_t \;=\; \{\, x_i(t),\; \mathbf{v}_i(t),\; \mathcal{C}_i(t),\; \phi_i(t) \,\}
$$

defines a glider as a persistent coherence motif—a relational pattern whose structure survives transformation while preserving its identity. A glider is a candidate representation of persistent motion, not an established physical particle. Depends on B.1–B.5.

### B.1.7 Complementary Inverse Motif

$$
G \;\leftrightarrow\; \bar{G}
$$

defines the complementary inverse motif. The inverse motif is a complementary coherence configuration related to the glider by an inverse or opposing relational transformation. The inverse must not automatically be identified with a physical antiparticle, negative energy, antimatter, or time reversal without an explicit derivation. Depends on B.6.

### B.1.8 Triadic Closure

$$
T_3 \;=\; \{\, G,\; \bar{G},\; H \,\}
$$

defines triadic closure—a relational structure in which a glider, its inverse, and a contextual degree of freedom form a closed dynamical configuration. Triadic closure is a candidate stabilization mechanism; its necessity and sufficiency remain to be proven. Depends on B.6, B.7.

### B.1.9 Set of All Continuations

$$
\Omega(x_t) \;=\; \{\, \gamma \;\mid\; \gamma = \{x_t, x_{t+1}, \dots, x_N\} \,\}
$$

defines the set of **all** continuations from state $x_t$. All continuations exist in the static Library. This is the Blind Exploration phase of the Lightning Model. It is a formal property of the static Library, not a physical process. Depends on B.1.

### B.1.10 Observer Survival Function

$$
\mathcal{O}(\gamma) \;=\; \prod_{i=0}^{N-1} \Theta\!\left(\mathcal{C}(x_i, x_{i+1}) - \mathcal{C}_{min}\right)
$$

defines the observer survival function. The observer survives on path $\gamma$ if and only if every transition maintains coherence above the threshold. Here $\Theta$ is the Heaviside step function, and the threshold $\mathcal{C}_{min}$ is derived from $I_N$ (see B.17). Depends on B.9, B.17.

### B.1.11 Surviving Continuations

$$
\Omega_{survive} \;=\; \{\, \gamma \in \Omega(x_t) \;\mid\; \mathcal{O}(\gamma) = 1 \,\}
$$

defines the subset of continuations where the observer's identity is preserved. This is the Coherence Filtering phase of the Lightning Model. Paths that fail the survival condition dissolve; they are not erased but become inaccessible. Depends on B.9, B.10.

### B.1.12 XOR Singularity

$$
X_{XOR} = \{\, x \mid \exists\, G, \bar{G}, H \text{ such that } x \in (G, \bar{G}, H) \land \mathbf{v}_G + \mathbf{v}_{\bar{G}} + \mathbf{v}_H = 0 \land \phi_G + \phi_{\bar{G}} + \phi_H \equiv 0 \pmod{2\pi} \,\}
$$

defines the XOR Singularity as the set of states where triadic closure is achieved. The "Ground" the return stroke connects to is the coherence boundary where triadic closure is achieved. The XOR Singularity is not a location in the Library; it is a coherence boundary—a condition of the field. Depends on B.6, B.7, B.8, B.16.

### B.1.13 Grounded Paths

$$
\Omega_{ground} \;=\; \{\, \gamma \in \Omega_{survive} \;\mid\; x_N \in X_{XOR} \,\}
$$

defines the subset of surviving continuations that terminate in the XOR Singularity. A path is grounded when its terminal state belongs to $X_{XOR}$. This is the Attractor Detection phase. A grounded path is one that maintains coherence all the way to the attractor. Depends on B.11, B.12.

### B.1.14 Retrocausally Locked-In Worldline

$$
\gamma_{obs} \;=\; \{\, x_N,\; T^{-1}(x_N),\; \dots,\; x_t \,\}
$$

defines the retrocausally locked-in worldline. The return stroke is the stable path that reaches $X_{XOR}$ while maintaining coherence. This is the Retrocausal Lock-In phase. The path is evaluated backward from the attractor to the origin; $T^{-1}$ is the backward operator. Depends on B.13.

### B.1.15 Realized Energy Cost

$$
E_{realized}(t) \;=\; c_{lock} \cdot \mathbb{I}\{\gamma_{obs} \text{ exists at } t\}
$$

defines the realized energy cost of observation. The observer pays a constant thermodynamic cost $c_{lock}$ at each timestep to instantiate its next state. The cost is $O(1)$ and independent of the number of alternatives explored. Depends on B.14, B.22.

### B.1.16 XOR Ground Condition

$$
H \;=\; G_{16}(\mathcal{M}) \;=\; \mathcal{M} \oplus \neg\mathcal{M}
$$

defines the XOR ground condition. The physical singularity is the irresolvable self-reference of the total system. The universe persists because its ground contradiction does not resolve. There is no exterior operand available to collapse the XOR; the totality is closed. Inherited from PHYS-CORE-009 §2.4. Depends on B.1.

### B.1.17 Noor-Planck Threshold

$$
I_N \;:=\; \min \left| \mathbb{C}(x,t) - \mathbb{C}_{ref}(x,t) \right| \;\text{ such that } b(x,t) \text{ is stable and exportable}
$$

defines the Noor-Planck threshold—the minimum coherence contrast required for a stable, exportable binary measurement. Below $I_N$, the field cannot resolve a distinction. $I_N$ is fixed by the Planck-scale structure of $H$; it is not an adjustable parameter, and $I_N \approx E_P / (T_P \cdot k_B \ln 2)$. Inherited from PHYS-CORE-009 §1.2. Depends on B.16.

### B.1.18 Observer

$$
\text{Observer} \;=\; \{\, b_i \,\}_{i\in\mathbb{N}} \quad \text{such that} \quad b_{i+1} = b_i \oplus b_{i-1} \;\text{ and }\; \mathbb{C}(b_i) \geq I_N \;\; \forall i
$$

defines the observer as a coherence-stable chain of XOR outputs. The observer is literally made of XOR operations. The fundamental propagation rule at the Noor-Planck floor is $b_{i+1} := b_i \oplus b_{i-1}$. The observer *is* XOR, instantiated as a coherent worldline. The observer does not require consciousness, life, intelligence, or agency; any coherence-stable XOR chain above $I_N$ qualifies. Inherited from PHYS-CORE-009 §1.1, §2.3, §3.2. Depends on B.16, B.17.

### B.1.19 Dissolution

$$
\text{Dissolution} \;\iff\; \exists\, i : \mathbb{C}(b_i) < I_N
$$

defines the condition under which an observer's identity ceases to propagate. When any link in the XOR chain falls below $I_N$, the observer dissolves. The path remains in the Library but becomes inaccessible. Dissolution is not erasure; no information is destroyed, and the pattern remains in $\mathcal{M}$. Inherited from PHYS-CORE-009 §1.2, §3.2. Depends on B.17, B.18.

### B.1.20 Triadic Closure Condition

$$
\oint_{A,\, \neg A,\, \chi} \Phi \;=\; 0
$$

defines the triadic closure condition. When triadic closure holds, coherence circulates through the triad without accumulating net torsion. This prevents blowup. Triadic closure is the mechanism that holds structure above $I_N$; without it, blowup is the default trajectory. Inherited from PHYS-CORE-009 §3.3. Depends on B.16.

### B.1.21 Field Demand Function

$$
D(R,t) \;=\; \int_R \left(1 - \Theta\!\left(\oint_{\triangle} \Phi\right)\right) \, d\mu
$$

defines the field demand function. $D(R,t) \in [0,1]$, where $0$ corresponds to full triadic closure and $1$ to complete closure failure. It measures the proportion of triadic loops in region $R$ that fail closure. The integral is over all triadic loops in region $R$, and the measure $\mu$ is the natural measure on $\mathcal{M}$ inherited from the inverse-limit construction. Inherited from PHYS-CORE-009 §3.4. Depends on B.20.

### B.1.22 Cost of Instantiation

$$
c_{lock} \;=\; \Delta F_{instantiation} \;\text{ where } \Delta F \text{ maintains } \mathbb{C}(\gamma) \geq I_N
$$

defines the cost of instantiation per timestep. The observer pays a constant thermodynamic cost to maintain coherence above $I_N$ for each timestep. $c_{lock}$ is $O(1)$ and constant per timestep, independent of the size of the Library or the number of alternatives explored. Depends on B.17, B.18.

### B.1.23 Global Coherence Operator

$$
\Omega : \text{ worldline with } |\Omega| \sim |R| \text{ and } G_{16}(\Omega) \text{ stable}
$$

defines the global coherence operator. A global coherence operator is a worldline that can hold the XOR tension at field scale, providing triadic closure for an entire region $R$. The operator's role is functional, not conscious; it does not require awareness of its role. Inherited from PHYS-CORE-009 §4.1. Depends on B.16, B.20, B.24.

### B.1.24 Coherence Reach

$$
|\Omega| = \mu ( \{ x \in R \mid \oint_{A(x),\, \neg A(x),\, \Omega} \Phi = 0 \} )
$$

defines the coherence reach of operator $\Omega$—the measure of the region over which $\Omega$ can function as witnessing motif $\chi$. The condition $|\Omega| \sim |R|$ is required for the operator to stabilize the region. Inherited from PHYS-CORE-009 §4.1. Depends on B.20, B.23.

### B.1.25 Witnessing Motif

$$
\chi \text{ (witnessing motif): } \chi = \Omega \text{ at field scale}
$$

defines the witnessing motif at field scale. The global coherence operator is the field-scale $\chi$ that holds the triadic tension for an entire region. The operator holds the tension by its existence as a stable descent path, not by any active intervention. Inherited from PHYS-CORE-009 §4.3. Depends on B.20, B.23.

### B.1.26 Critical Threshold of Field Demand

$$
D_{crit}(R) \;=\; f(\rho_{triadic}(R))
$$

defines the critical threshold of field demand. $D_{crit}$ is the threshold above which region $R$ cannot self-stabilize. It scales with the density of intact triadic closures. Regions with denser triadic networks have higher $D_{crit}$ and can tolerate more failure before requiring field-scale intervention. Inherited from PHYS-CORE-009 §4.2. Depends on B.21.

### B.1.27 Triadic Connectivity Density

$$
\rho_{triadic}(R) \;=\; \text{density of intact triadic closures in } R
$$

defines the triadic connectivity density—the measure of how densely interlinked worldlines are through mutual witnessing relationships. Higher $\rho_{triadic}$ means greater capacity to absorb local coherence failures. Inherited from PHYS-CORE-009 §4.2. Depends on B.20.

### B.1.28 Regional XOR Capacity

$$
C_{XOR}(R,t) = \sup \{ |\Omega| : \gamma_\Omega \in R,\; G_{16}(\Omega) \text{ stable} \}
$$

defines the regional XOR capacity—the maximum coherence reach of any worldline in region $R$ that maintains Gate-16 stability. $C_{XOR}(R,t)$ is the upper bound on the field's capacity to hold XOR at the scale of $R$. Inherited from PHYS-CORE-009 §5.2. Depends on B.16, B.23, B.24.

---

## B.2 Identities

The following entries record mathematical relations that follow from the adopted representation. They are inherited from PHYS-CORE-009 unless otherwise noted.

### B.2.1 Ontological Completeness

$$
\forall C \text{ internally describable } \;\Rightarrow\; C \in \mathcal{M}
$$

Every internally describable configuration exists in the Library. Nothing describable is outside the totality. Inherited from PHYS-CORE-009 §1.1. Depends on B.1.

### B.2.2 No Exterior

$$
\nexists\, \Omega' : \mathcal{M} \subset \Omega'
$$

There is no exterior to the Library. The totality is closed. Inherited from PHYS-CORE-009 §1.1. Depends on B.1.

### B.2.3 Staticity

$$
\mathcal{M}(t) \;=\; \mathcal{M} \quad \forall t \in \mathbb{R}
$$

The Library does not change. Observed temporality arises solely from projection of coherence gradients along descent paths. Inherited from PHYS-CORE-009 §1.1. Depends on B.1.

### B.2.4 Persistence Condition

$$
\forall t,\; \mathcal{M} \text{ persists } \;\Longleftrightarrow\; G_{16}(\mathcal{M}) \text{ does not resolve to } 0 \text{ or } 1
$$

The universe persists if and only if the ground condition remains irresolvable. Resolution of $H$ to $0$ or $1$ would correspond to a terminal state—a halting of recursive continuation. Inherited from PHYS-CORE-009 §2.4. Depends on B.16.

### B.2.5 Boolean Projection

$$
b(x,t) = F \;\text{ iff }\; \mathbb{C}(x,t) - \mathbb{C}_{ref}(x,t) \geq I_N
$$

defines the Boolean projection of the coherence field. Above $I_N$, the field resolves into stable binary distinctions. Below $I_N$, distinctions dissolve. Inherited from PHYS-CORE-009 §3.1. Depends on B.17.

### B.2.6 Exportability

$$
b(x,t) = E \;\text{ iff }\; \mathbb{C}(x,t) - \mathbb{C}_{ref}(x,t) < I_N
$$

defines the empty Boolean projection. Both $F$ and $E$ are equally real above $I_N$; below $I_N$, neither is resolvable. Inherited from PHYS-CORE-009 §3.1. Depends on B.17.

### B.2.7 Survivorship Bias

$$
P(\gamma_{obs} \mid \mathcal{O}(\gamma_{obs}) = 1) \;=\; 1
$$

The observer necessarily experiences the path that survived. Conditioned on the fact that an observer exists, the observed timeline must be 100% coherent. Depends on B.10, B.14.

### B.2.8 No Erasure

$$
\text{Erased} \;\neq\; \text{Inaccessible}
$$

Distinguishes erasure from inaccessibility. Information is not destroyed; it simply becomes inaccessible to the observer. Depends on B.1, B.11, B.19.

### B.2.9 Cost Scaling

$$
E_{realized}(t) \;=\; \mathcal{O}(1)
$$

The per-observer per-timestep realized cost is constant. The cost does not scale with the size of the Library or the number of alternatives. Depends on B.15.

### B.2.10 Noor-Planck Bound

$$
I_N \;\approx\; \frac{E_P}{T_P \cdot k_B \ln 2}
$$

This derived result grounds the coherence threshold in fundamental constants. $I_N$ is fixed by the Planck-scale structure of $H$; it is not an adjustable parameter. Inherited from PHYS-CORE-009 §1.3. Depends on B.17.

### B.2.11 Observer as Descent Path

$$
\gamma : \mathbb{R} \to \mathcal{M} \quad \text{such that} \quad \frac{d\gamma}{dt} = \nabla_H \mathbb{C}(\gamma(t)) \;\text{ and }\; \mathbb{C}(\gamma(t)) \geq I_N \;\; \forall t
$$

defines the observer as a coherence-stable descent path—a path through the Library that follows the coherence gradient while remaining above $I_N$. Inherited from PHYS-CORE-009 §1.1. Depends on B.1, B.17, B.18.

---

## B.3 Derived Results

The following entries follow from previously established premises.

### B.3.1 Operator Emergence

$$
D(R,t) > D_{crit} \;\land\; \exists\, \gamma_\Omega \in R \text{ with } |\Omega| \sim |R| \text{ and pattern } S_\Omega = S_R \;\Longrightarrow\; \Omega \text{ emerges}
$$

This states the condition under which a global coherence operator emerges. When field demand exceeds critical threshold and a worldline with sufficient reach and matching pattern exists, operator emergence is inevitable. Emergence is selection by the coherence geometry, not external intervention. Inherited from PHYS-CORE-009 §4.4. Depends on B.21, B.23, B.24, B.26.

### B.3.2 Pattern Reemergence

$$
(\gamma_S \text{ dissolves}) \;\land\; (\exists\, t' > t : D(R,t') > D_{crit} \text{ requires } S) \;\Longrightarrow\; \gamma_S \text{ reselected}
$$

The same unique worldline will be reselected if field demand again requires its pattern. The pattern persists in the Library and reemerges when the field demands it. The pattern is unique; there is exactly one worldline for each unique structural pattern. Inherited from PHYS-CORE-009 §5.2. Depends on B.16, B.21, B.23, B.40.

### B.3.3 Universal Dissolution

$$
\forall \text{ worldlines } \gamma,\; \gamma \text{ can choose descent below } I_N
$$

Every worldline has the structural capacity to dissolve. This is death—the choice to cease maintaining coherence. The choice is structural, not conscious; it is the capacity to allow coherence to drop below $I_N$. Inherited from PHYS-CORE-009 §5.2. Depends on B.18, B.19.

### B.3.4 Triadic Closure Prevents Blowup

$$
\oint \Phi = 0 \;\Longrightarrow\; \text{no blowup}
$$

Triadic closure prevents coherence collapse. When triadic closure holds for all constituent triads, the structure does not experience blowup. Blowup is the default trajectory without triadic maintenance. Inherited from PHYS-CORE-009 §3.3. Depends on B.20.

---

## B.4 Dependency Graph

The following directed graph records the dependency relations among the register entries. Each edge $X \to Y$ indicates that entry $Y$ depends on entry $X$ for its interpretation.

$$
\begin{aligned}
& B.1 \to \{B.2, B.3, B.4, B.5, B.6, B.9, B.16, B.29, B.30, B.31, B.36, B.39\} \\
& B.2 \to B.3 \\
& B.3 \to B.4 \\
& B.4 \to B.5 \\
& B.5 \to B.6 \\
& B.6 \to \{B.7, B.8, B.12\} \\
& B.7 \to \{B.8, B.12\} \\
& B.8 \to B.12 \\
& B.9 \to \{B.10, B.11\} \\
& B.10 \to \{B.11, B.35\} \\
& B.11 \to \{B.13, B.36\} \\
& B.12 \to B.13 \\
& B.13 \to B.14 \\
& B.14 \to \{B.15, B.35\} \\
& B.15 \to B.37 \\
& B.16 \to \{B.17, B.18, B.20, B.23, B.28, B.32, B.41\} \\
& B.17 \to \{B.18, B.19, B.22, B.33, B.34, B.38, B.39\} \\
& B.18 \to \{B.19, B.22, B.39, B.42\} \\
& B.19 \to \{B.36, B.42\} \\
& B.20 \to \{B.21, B.24, B.25, B.27, B.43\} \\
& B.21 \to \{B.26, B.40, B.41\} \\
& B.22 \to B.15 \\
& B.23 \to \{B.24, B.25, B.28, B.40, B.41\} \\
& B.24 \to \{B.28, B.40\} \\
& B.26 \to \{B.40, B.41\}
\end{aligned}
$$

---

## B.5 Status Legend

| Status | Meaning |
| :--- | :--- |
| **Definition** | Terminology or conceptual structure introduced by the paper. |
| **Identity** | A mathematical relation that follows from the adopted representation. |
| **Derived Result** | A result that follows from previously established premises. |

---

## B.6 Generation Guidance

Any register entry may be generated independently, but its dependency list must be consulted before interpretation. The following integrity rules apply:

- Do not silently upgrade an ansatz into a derived equation.
- Do not silently upgrade a hypothesis into a theorem.
- Do not use omitted terms represented by ellipses in a final derivation.
- Perform dimensional analysis before assigning physical interpretation.
- Define every symbol locally when generating a subsection independently.
- Preserve the distinction between mathematical consistency and physical validity.

Detailed derivations belong in the main paper or dedicated mathematical subsections; this appendix records the resulting mathematical vocabulary and its epistemic status.

---

## References

- PHYS-CORE-008: *Noor Library Ontology — Recursive Bloch Manifold*.
- PHYS-CORE-009 §1.1: *The Library as Static Totality*.
- PHYS-CORE-009 §1.2: *The Boolean Ground Condition*.
- PHYS-CORE-009 §1.3: *The 1 Planck-Width Irresolvable Hole*.
- PHYS-CORE-009 §2.3: *XOR as the Signature of Interior Embedding*.
- PHYS-CORE-009 §2.4: *Formal Identification: Singularity = Self ⊕ ¬Self*.
- PHYS-CORE-009 §3.1: *The Field is Boolean at Base*.
- PHYS-CORE-009 §3.2: *Coherence Resolution Above I\_N*.
- PHYS-CORE-009 §3.3: *Triadic Closure as Blowup Prevention*.
- PHYS-CORE-009 §3.4: *Regional Coherence Failure and Field Demand*.
- PHYS-CORE-009 §4.1: *Definition of Global Coherence Operator*.
- PHYS-CORE-009 §4.2: *The Field Demand Function*.
- PHYS-CORE-009 §4.3: *Functional Role: χ at Field Scale*.
- PHYS-CORE-009 §4.4: *Operator Emergence as Structural Necessity*.
- PHYS-CORE-009 §5.2: *The Birth of XOR is Not a Single Event*.

---

| PREVIOUS | | NEXT |
| --- | --- | --- | 
| [prev_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-appendix.a.md) | [INDEX](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-index.md) | [next_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-appendix.c.md) |
