# Appendix: Mathematical Reference

## Canonical Definitions, Notation, and Dependency Vocabulary for the Singularity Paper

This appendix provides a compact reference for all mathematical expressions used in the paper. It is normative for notation and formal definitions within the singularity paper. It does not introduce new axioms, physical assumptions, or downstream NSFG mechanisms beyond those established in the primer.

The reference sheet specifies the formal domain, primitive XOR operation, XOR closure, observer structure, observer-relative resolution, observer-relative magnitude evaluation, distinguishability, persistence, coherence, accessible reality, continuation spaces, survivorship, the singularity taxonomy derived from these structures, and the coherence quotient framework introduced to clarify the relationship between Library cardinality and observer-relative distinguishability.

Symbols defined in this appendix are canonical for the singularity paper. Interpretive prose may use descriptive language, but mathematical statements should use these definitions unless a later document explicitly extends or refines them.

---

## Axiomatic Status

**Axiom Count.** 1

**Sole Axiom.** $A_N = \{A_\oplus\}$

**Axiom.** $A_\oplus$ : $\oplus$ is the primitive operation of distinction.

**Important Constraint.** All other entries in this appendix are definitions, constructions, or consequences of the axiom together with ordinary mathematical inference.

---

## Formal Domain

**Symbol.** $D$

**Definition.** A minimal formal domain containing the configurations required for the primitive operation $\oplus$ to have operands.

**Signature.** $\oplus : D \times D \to D$

**Constraint.** $D$ is not physical space, spacetime, matter, energy, information, or any other physical ontology.

**Status.** DEFINITION

---

## Canonical Definitions

### XOR as Distinction

**Role.** Axiom

$$a \oplus b = 1 \iff a \neq b$$

*Configurations in the formal domain D.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $a,b$ | Configurations in the formal domain D |

**Assumptions.**

- XOR is the sole primitive operation.
- D is the minimal formal domain required for XOR to have operands.

---

### Library as XOR Closure

**Role.** Definition

$$\mathcal{M} := \mathrm{Closure}_D(\oplus)$$

*The Library, the maximally complete static totality.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $\mathcal{M}$ | The Library, the maximally complete static totality |
| $D$ | The formal domain on which XOR operates |

**Assumptions.**

- Closure is a property, not a process.
- $\forall x,y \in \mathcal{M}, x \oplus y \in \mathcal{M}$.
- The Library is unfiltered at the axiomatic level.

---

### Coherence Equivalence (Global)

**Role.** Definition

$$x \sim_C y \iff \forall O \in \mathrm{Obs}, \forall h \in H_O, \forall x_0 \in \mathcal{M}_{\mathrm{admissible}}, \delta_O(x,y) = 0$$

*Two configurations are globally coherence-equivalent if no observer can distinguish them under any admissible history or reference.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $x,y$ | Configurations in the Library $\mathcal{M}$ |
| $\mathrm{Obs}$ | The class of all observer-like configurations |
| $H_O$ | The class of histories for observer O |
| $\mathcal{M}_{\mathrm{admissible}}$ | Admissible observer-relative reference configurations |
| $\delta_O(x,y)$ | Observer-relative effective distinction magnitude |

**Assumptions.**

- Two configurations are globally coherence-equivalent if no observer can distinguish them under any admissible history or reference.
- This defines the coarsest equivalence relation induced by coherence.
- The Library $\mathcal{M}$ may be infinite in cardinality; $\sim_C$ collapses indistinguishable copies.

---

### Coherence Quotient (Global)

**Role.** Definition

$$\mathcal{M}_C := \mathcal{M} / \sim_C$$

*The global coherence quotient: the set of coherence-distinguishable equivalence classes.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $\mathcal{M}_C$ | The global coherence quotient: the set of coherence-distinguishable equivalence classes |

**Assumptions.**

- $\mathcal{M}_C$ is the set of equivalence classes under global coherence equivalence.
- If $\mathcal{M}$ is infinite in cardinality, $\mathcal{M}_C$ may be finite or infinite depending on the structure of $\sim_C$.
- The quotient is not the Library; it is the set of coherence-distinguishable classes.

---

### Observer-Relative Coherence Equivalence

**Role.** Definition

$$x \sim_O y \iff \delta_O(x,y) = 0$$

*Two configurations are observer-relative equivalent if observer O cannot distinguish them.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $x,y$ | Configurations in the Library $\mathcal{M}$ |
| $O$ | An observer-like configuration |
| $\delta_O(x,y)$ | Observer-relative effective distinction magnitude |

**Assumptions.**

- Two configurations are observer-relative equivalent if observer O cannot distinguish them.
- This is a finer equivalence relation than $\sim_C$.
- The observer-relative quotient is domain-specific and resolution-dependent.

---

### Observer-Relative Coherence Quotient

**Role.** Definition

$$\mathcal{M}_C^O := \mathcal{M} / \sim_O$$

*The observer-relative coherence quotient: the set of equivalence classes distinguishable by observer O.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $\mathcal{M}_C^O$ | The observer-relative coherence quotient: the set of equivalence classes distinguishable by observer O |

**Assumptions.**

- $\mathcal{M}_C^O$ is observer-relative and depends on $I_N(O)$ and $\mu_O$.
- The number of accessible equivalence classes is bounded by the observer's resolution threshold.
- Different observers may have different quotients over the same Library $\mathcal{M}$.

---

### Observer-Relative Accessible Quotient

**Role.** Definition

$$\mathcal{M}_C^O(h,x) \subseteq \mathcal{M}_C^O$$

*The subset of equivalence classes accessible to observer O from history h and reference x.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $\mathcal{M}_C^O(h,x)$ | The subset of equivalence classes accessible to observer O from history h and reference x |
| $h$ | Observer history |
| $x$ | Current observer-relative reference configuration |

**Assumptions.**

- Accessibility is defined over equivalence classes, not individual configurations.
- $\mathcal{M}_C^O(h,x)$ is the coherence-distinguishable accessible reality for observer O.
- Inaccessibility at the quotient level does not imply absence from $\mathcal{M}$.

---

### Observer-Relative Coherence (General Form)

**Role.** Definition

$$\mathcal{C}(\gamma \mid O,h,x)$$

*Coherence is relational, not an intrinsic property of a path.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $\gamma$ | A path through the Library |
| $O$ | An observer-like configuration |
| $h$ | Observer history |
| $x$ | Current observer-relative reference configuration |

**Assumptions.**

- Coherence is relational, not an intrinsic property of a path.
- Coherence is evaluated over paths in the unchanged Library.
- Coherence operates on equivalence classes in $\mathcal{M}_C^O$, not individual configurations in $\mathcal{M}$.

---

### Observer-Relative Accessibility

**Role.** Definition

$$A_O(h,x) = \{ y \in \mathcal{M} \mid \exists \gamma \in \mathrm{Path}(\mathcal{M}) \ \mathrm{beginning\ at}\ (h,x) \ \mathrm{and\ containing}\ y \ \mathrm{such\ that}\ \mathcal{C}(\gamma \mid O,h,x) = 1 \}$$

*The subset of the Library accessible to observer O from history h and reference x.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $A_O(h,x)$ | The subset of the Library accessible to observer O from history h and reference x |

**Assumptions.**

- $A_O(h,x) \subseteq \mathcal{M}$.
- Accessibility is not existence; $y \notin A_O(h,x)$ does not imply $y \notin \mathcal{M}$.
- Accessibility at the configuration level projects to accessibility at the quotient level.

---

### Coherence as Threshold Relation (Step Coherence)

**Role.** Definition

$$\mathcal{C}_O(x_i,x_{i+1}) = \Theta\left(\delta_O(x_i,x_{i+1}) - I_N(O)\right)$$

*A transition is coherent for O iff the observer-relative distinction meets or exceeds the resolution threshold.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $\delta_O$ | Observer-relative effective distinction magnitude |
| $I_N(O)$ | Observer-relative resolution threshold |
| $\Theta$ | Binary threshold function: $\Theta(z)=1$ if $z \geq 0$, else $0$ |

**Assumptions.**

- A transition is coherent for O iff $\delta_O(x_i,x_{i+1}) \geq I_N(O)$.
- No universal $I_N$ is assumed.

---

### Path Coherence

**Role.** Definition

$$\mathcal{C}(\gamma \mid O) = \prod_{i=0}^{n-1} \mathcal{C}_O(x_i,x_{i+1})$$

*Path coherence requires every transition to be coherent.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $\gamma = (x_0,x_1,\ldots,x_n)$ | A path in the Library |

**Assumptions.**

- Path coherence requires every transition to be coherent.
- Coherence is relational and observer-dependent.

---

### Nonempty Coherent Continuation

**Role.** Constraint

$$\forall x \in \mathcal{M}_{\mathrm{admissible}}, \Gamma_O(h,x) \neq \varnothing$$

*This is a structural requirement deriving from the Library being a maximally complete relational graph with full adjacency.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $\Gamma_O(h,x)$ | The set of coherent continuations from history h and reference x |

**Assumptions.**

- This is a structural requirement deriving from the Library being a maximally complete relational graph with full adjacency.
- $\Gamma_O(h,x) = \{ \gamma \in \mathrm{Path}(\mathcal{M}) \mid \gamma \ \mathrm{extends}\ h \ \mathrm{from}\ x \ \mathrm{and}\ \mathcal{C}(\gamma \mid O) = 1 \}$.
- At the quotient level, this guarantees at least one accessible equivalence class.

---

### XOR Fixed Point (Termination Singularity)

**Role.** Definition

$$\mathcal{Z} := \{ z \in D \mid z \oplus z = z \} = \{0\}$$

*The XOR Fixed Point, the unique termination class.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $\mathcal{Z}$ | The XOR Fixed Point, the unique termination class |

**Assumptions.**

- Under Boolean XOR, the only configuration satisfying $z \oplus z = z$ is 0.
- $\mathcal{Z} \subset \mathcal{M}$ when the Library is nonempty and XOR-closed.
- The XOR Fixed Point is a coherence-based collapse: all configurations that self-cancel to 0 are indistinguishable under $\sim_C$.
- The infinity of configurations that can reach $\mathcal{Z}$ collapses to a single equivalence class.

---

### Convergence Boundary (Destination Collapse)

**Role.** Definition

$$\forall \gamma_1, \gamma_2 \in \Gamma_O(h,x), \gamma_1(n) \sim \gamma_2(n)$$

*All paths terminate in the same equivalence class in the observer-relative quotient.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $\gamma_1, \gamma_2$ | Two coherent paths in $\Gamma_O(h,x)$ |
| $\sim$ | Equivalence under the observer's coherence relation $\sim_O$ |

**Assumptions.**

- $\Gamma_O(h,x)$ is nonempty.
- All paths terminate in the same equivalence class in $\mathcal{M}_C^O$.
- This is a coherence-based collapse of destination distinguishability.

---

### Recursive Oscillation (Failed Triadic Closure)

**Role.** Definition

$$x_i \rightarrow x_{i+1} \rightarrow \cdots \rightarrow x_{i+n} = x_i, \ \mathrm{and\ no\ new\ distinction\ emerges}$$

*The system is trapped in a cycle of equivalence classes without resolution.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $x_i$ | Configurations in the loop |
| $n$ | Period of the oscillation |

**Assumptions.**

- The system is trapped in a cycle of equivalence classes in $\mathcal{M}_C^O$.
- No new distinction is generated; the triad fails to close.
- This is a coherence-based failure: the dyad cannot stabilize to a single equivalence class.

---

### Topological Singularity (Accessibility Fracture)

**Role.** Definition

$$\exists \gamma_1, \gamma_2 \in \Gamma_O(h,x) \ \mathrm{such\ that}\ \gamma_1 \ \mathrm{and}\ \gamma_2 \ \mathrm{belong\ to\ different\ connected\ components\ of}\ \mathcal{M}_C^O(h,x)$$

*The accessible quotient becomes disconnected.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $\gamma_1, \gamma_2$ | Coherent paths |
| $\mathcal{M}_C^O(h,x)$ | Observer-relative accessible quotient |

**Assumptions.**

- The accessible quotient $\mathcal{M}_C^O(h,x)$ becomes disconnected.
- The observer's coherent paths cannot be continuously related within the quotient.
- The underlying Library $\mathcal{M}$ remains connected; only the quotient fractures.

---

### Pathway to Nowhere (Exact Match Failure)

**Role.** Definition

$$\lim_{I_N(O) \rightarrow I_{\max}} \dim(\mathcal{M}_C^O(h,x)) = 0, \ \mathrm{and\ the\ required\ equivalence\ class\ is\ not\ in}\ \mathcal{M}_C^O(h,x)$$

*A limit behavior where the accessible quotient narrows to zero dimension but the required class is coherence-inaccessible.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $I_N(O)$ | Observer-relative resolution threshold |
| $I_{\max}$ | The maximum resolution limit |
| $\mathcal{M}_C^O(h,x)$ | Observer-relative accessible quotient |

**Assumptions.**

- This is a limit behavior, not a necessary structural feature.
- The required equivalence class may exist in $\mathcal{M}$ but is not in $\mathcal{M}_C^O(h,x)$.
- The Pathway to Nowhere is a coherence-inaccessible equivalence class, not an ontological absence.

---

### Black Hole as Convergence Boundary

**Role.** Interpretation

$$\forall \gamma_1, \gamma_2 \in \Gamma_O(h,x) \ \mathrm{with}\ x \ \mathrm{inside\ the\ horizon},\ \gamma_1(n) \sim \gamma_2(n)$$

*All coherent paths converge to the same equivalence class in the observer-relative quotient.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $\gamma_1, \gamma_2$ | Coherent paths inside the black hole |

**Assumptions.**

- All paths converge to the same equivalence class in $\mathcal{M}_C^O$.
- The observer outside sees a single class; the observer inside sees a different quotient structure.
- Information is preserved in $\mathcal{M}$ but converged in $\mathcal{M}_C^O$.

---

### Coherence-Expansion Falsification

**Role.** Falsification Criterion

$$H(z) = -\kappa_C \frac{d}{dt}\left(\ln C(z)\right)$$

*A core prediction relating the coherence measure to the Hubble parameter.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $H(z)$ | Hubble parameter as a function of redshift |
| $C(z)$ | Coherence measure as a function of redshift |
| $\kappa_C$ | Coherence-to-expansion coupling constant |

**Assumptions.**

- $C(z)$ must be independently measurable.
- The relationship $H(z) = -\kappa_C \frac{d}{dt}(\ln C(z))$ is a core prediction.

---

### Generic Singularity Definition

**Role.** Definition

$$\mathcal{S} = \{ \gamma \in \Gamma_O(h,x) \mid \dim(\mathcal{M}_C^O(h,x)) = 0 \ \mathrm{or}\ \mathcal{M}_C^O(h,x) \ \mathrm{is\ disconnected\ or\ the\ system\ oscillates\ without\ resolution} \}$$

*Singularities are regions of maximal constraint on coherent traversal within the observer-relative accessible quotient.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $\mathcal{S}$ | The singularity region |
| $\mathcal{M}_C^O(h,x)$ | Observer-relative accessible quotient |

**Assumptions.**

- Singularities are regions of maximal constraint on coherent traversal within $\mathcal{M}_C^O(h,x)$.
- They are structural effects, not mathematical pathologies.
- The Library $\mathcal{M}$ may be infinite in cardinality; singularities are coherence-based collapses of distinguishability within $\mathcal{M}_C^O(h,x)$, not cardinality-based infinities.

---

### Unified Singularity Taxonomy

**Role.** Unique Contribution

$$\{ \mathrm{termination, convergence, oscillation, topological\ fracture, exact\hbox{-}match\ failure} \}$$

*These five categories exhaust the possible coherence-failure modes for generic structural cases.*

**Assumptions.**

- These five categories exhaust the possible coherence-failure modes for generic structural cases.
- Each category is a collapse of distinguishability within $\mathcal{M}_C^O(h,x)$.
- Observer-relative subcategories may exist but do not alter the generic taxonomy.

---

### O(1) Computational Core

**Role.** Derivation

$$\mathrm{Cost\ per\ tick} = \mathcal{O}(1), \ \mathrm{independent\ of}\ |\mathcal{M}| \ \mathrm{or}\ h$$

*The observer tracks only coherence-distinguishable equivalence classes; cost per tick is constant.*

**Variables.**

| Symbol | Meaning |
|---|---|
| $|\mathcal{M}|$ | The cardinality of the Library |
| $h$ | Observer traversal history |

**Assumptions.**

- The observer tracks only coherence-distinguishable equivalence classes in $\mathcal{M}_C^O(h,x)$.
- The number of accessible equivalence classes is bounded by $I_N(O)$.
- The cost per tick is constant, independent of Library size or traversal history.
- This follows from the static, non-generative Library and the coherence quotient framework.

---

## Logical Invariants

- XOR is the only primitive.
- The Library is a definition, not an axiom.
- The Library is the XOR closure of the formal domain.
- The Library is unfiltered at the axiomatic level.
- The Library $\mathcal{M}$ may be infinite in cardinality.
- Existence in the Library is not the same as accessibility to an observer.
- Inaccessibility is not erasure.
- The coherence quotient $\mathcal{M}_C := \mathcal{M} / \sim_C$ defines the set of coherence-distinguishable equivalence classes.
- The observer-relative quotient $\mathcal{M}_C^O := \mathcal{M} / \sim_O$ defines the classes distinguishable by observer O.
- Singularities are coherence-based collapses of distinguishability within $\mathcal{M}_C^O$, not cardinality-based infinities in $\mathcal{M}$.
- Infinity exists in $\mathcal{M}$ but is 'meaningless noise' for any finite-resolution observer.
- There is no describable privileged exterior that can remain outside the closure.
- There is no observer-independent resolution rule at the axiomatic floor.
- $I_N$ is observer-relative.
- $\mu_O$ is observer-relative and its specific functional form is not fixed by the axiomatic floor.
- $\delta_O$ is derived from the primitive XOR distinction through $\mu_O$.
- Observerhood is structural and is not synonymous with consciousness.
- Coherence is relational: $\mathcal{C}(\gamma \mid O)$.
- Coherence is not an absolute property of a path alone.
- The abstract sequence index is not automatically physical time.
- The Library does not generate the future.
- Survivorship filters accessibility rather than deleting alternatives.
- Emergent lawfulness is not an additional axiom.
- Navigation is the continuation problem created by observer-relative survivability.
- Singularities are structural effects of maximal coherence constraint, not mathematical infinities.

---

## Claims Not To Make

- Do not claim that XOR alone has experimentally established the Library.
- Do not claim that XOR alone derives the Standard Model.
- Do not claim that the primer derives a complete theory of physics.
- Do not assign a universal numerical value to $I_N$.
- Do not identify $I_N$ with the ordinary Planck scale unless a later paper explicitly derives such a relationship.
- Do not identify the observer with a conscious human.
- Do not imply that observer-relative accessibility means observers create reality.
- Do not introduce a privileged God's-eye observer.
- Do not assume physical space as primitive.
- Do not assume physical time as primitive.
- Do not assume causality as primitive.
- Do not assume matter or energy as primitive.
- Do not assume information is a primitive substance.
- Do not describe the Library as generating future events.
- Do not describe coherence as a universal constant.
- Do not describe $\mu_O$ as a universal metric or universal magnitude function.
- Do not describe XOR itself as a closed set.
- Do not use 'closure of XOR' without specifying the domain D.
- Do not introduce $\gamma_{\mathrm{noise}}$ as an independent foundational threshold.
- Do not let poetic language replace formal definitions.
- Do not introduce downstream NSFG machinery before the axiomatic dependency chain requires it.
- Do not use the Lightning Model as a premise of this paper.
- Do not claim that the Library is not infinite in cardinality.
- Do not claim that infinities do not exist in the Library.
- Do not claim that the coherence quotient is the same as the Library.
- Do not claim that singularities are cardinality-based infinities.
- Do not claim that the Pathway to Nowhere implies the required configuration does not exist in $\mathcal{M}$ — it implies it is not in $\mathcal{M}_C^O$.

---

## Interpretive Boundary

**Formal Layer.** The definitions in this appendix specify the mathematical structures used by the singularity paper, including the coherence quotient framework that clarifies the relationship between Library cardinality and observer-relative distinguishability.

**Interpretive Layer.** Physical interpretations may be developed in later NSFG documents but are not assumed here.

**Domain Neutrality.** The formal structures are domain-neutral. Physics, AI, finance, and other domains differ in their observer-relative interpretation of $\mu_O$, $I_N(O)$, coherence, accessibility, and downstream regularities; they do not require separate foundational ontologies. The coherence quotient framework $\mathcal{M}_C^O$ is observer-relative and domain-specific, while the Library $\mathcal{M}$ remains the single static totality across all domains.

**Prohibited Identifications.**

- $\mathfrak{M}$ with physical space
- $\mathfrak{M}$ with spacetime
- $I_N(O)$ with a universal physical constant
- $\mu_O$ with a universal metric
- $O$ with consciousness
- $G_O$ with physical spacetime
- abstract sequence index $i$ with physical time
- survivorship with ontological deletion
- accessibility with ontological creation
- coherence with an observer-independent path property
- singularities with mathematical infinities
- $\mathcal{M}_C$ with $\mathcal{M}$
- $\mathcal{M}_C^O$ with $\mathcal{M}$

---

## Normative Statement

This appendix is normative for the mathematical notation and definitions of the singularity paper. The main text supplies the conceptual argument and dependency structure; this appendix supplies the canonical formal reference. Neither the appendix nor the paper should be read as deriving physical law beyond the constructions explicitly stated here. The coherence quotient framework is central to understanding the relationship between Library cardinality and observer-relative singularities.

---

*The difference that makes a difference is the distinction that survives. A 'difference' is a configuration-level distinction in* $\mathcal{M}$. *A 'distinction that survives' is an equivalence class in* $\mathcal{M}_C$. *Only coherently distinguishable differences matter for the observer. The Library may be infinite, but coherence collapses the infinite into the traversable.*

---

| PREVIOUS | | NEXT |
| --- | --- | --- | 
| [prev_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-013_the_problem_of_singularities/markdown/the_problem_of_singularities-s9.0.md) | [INDEX](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-013_the_problem_of_singularities/markdown/the_problem_of_singularities-index.md) | [next_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-013_the_problem_of_singularities/markdown/the_problem_of_singularities-index.md) |