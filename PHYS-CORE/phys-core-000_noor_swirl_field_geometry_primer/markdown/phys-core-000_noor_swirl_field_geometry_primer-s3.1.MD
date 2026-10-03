### 3.1 Closure Under XOR

The primitive operation $\oplus$ specifies distinction on a formal domain $D$. Closure supplies the condition under which a collection of configurations remains internally closed under that operation. Nothing in this definition requires a temporal sequence, a physical space, or a process of construction.

**Definition — Definition 3.1 — Formal XOR Closure.** Let $D$ be the formal domain on which $\oplus$ operates, and let $G\subseteq D$ be a specified set of configurations used as mathematical generators for a representation. The XOR closure of $G$ in $D$ is the smallest subset $S\subseteq D$ containing $G$ and closed under XOR.

$$\mathrm{Closure}_{D}(\oplus;G)=\bigcap\left\{S\subseteq D\mid G\subseteq S\land\forall x,y\in S,\;x\oplus y\in S\right\}$$

The closure construction is mathematical rather than generative. A generator describes a closed structure; it does not become a first physical state, and the closure operation does not describe a sequence through which the Library comes into existence.

**Definition — Definition 3.2 — Static Library.** The Library $\mathcal{M}$ is the maximally complete, unbounded totality satisfying XOR closure and self-containment with respect to the formal resources of the system.

**Library closure property.**

$$\forall x,y\in\mathcal{M},\quad x\oplus y\in\mathcal{M}$$

*XOR does not require an exterior configuration once its operands are within the Library.*

**Definition — Definition 3.3 — Self-Containment.** No configuration outside $\mathcal{M}$ can function as a privileged exterior if it is definable within the system using the same formal resources.

**No describable privileged exterior.**

$$\neg\exists z\notin\mathcal{M}\;\mathrm{such\ that}\ z\ \mathrm{is\ definable\ within\ the\ system\ using\ only}\ \oplus\ \mathrm{and\ elements\ of}\ \mathcal{M}\ \mathrm{over}\ D\ \mathrm{as\ a\ privileged\ exterior}$$

*The formal system contains no describable privileged external reference.*

**Definition — Definition 3.4 — Relational Completeness.** For every represented relation $R\in\mathcal{R}$, any true relation between configurations in $\mathcal{M}$ is representable within $\mathcal{M}$ without requiring $R$ to be introduced as a primitive.

**Relational completeness of the Library.**

$$\forall R\in\mathcal{R},\;\forall x,y\in\mathcal{M},\;R(x,y)=1\Rightarrow R\ \mathrm{is\ representable\ within}\ \mathcal{M}\ \mathrm{without\ requiring}\ R\ \mathrm{to\ be\ a\ primitive\ of\ the\ system}$$

*The Library provides a complete formal relational substrate for later constructions without promoting those relations to new axioms.*

This statement is deliberately structural. It does not assert that every conceivable relation has already been derived, measured, or assigned a physical meaning. It states that relations required by the formal development can be represented within the same totality rather than requiring a privileged relational space outside it.

**Definition — Definition 3.5 — XOR Termination Singleton.** The termination singleton is $\mathcal{Z}:=\{z\in D\mid z\oplus z=z\}=\{0\}$.

**Termination singleton.**

$$\mathcal{Z}:=\{z\in D\mid z\oplus z=z\}=\{0\}$$

*The XOR identity is the unique configuration satisfying the stated fixed-point condition.*

Since $x\oplus x=0$ for every Boolean XOR configuration, self-cancellation terminates internally at $0$. The resulting singleton is therefore not an edge or exterior of the Library.

**Self-cancellation into 𝒵.**

$$\forall x\in\mathcal{M},\quad x\oplus x=0\in\mathcal{Z}\subseteq\mathcal{M}$$

*Self-cancellation remains entirely internal to the Library.*

The identity relation further gives $0\oplus x=x$, and the recursive bounce therefore degenerates at the identity: $(x\oplus0)\oplus0=x$. This is termination of new distinction at the identity state, not erasure of the configuration from the Library.

**Identity-state degeneration.**

$$\left(x\oplus0\right)\oplus0=x$$

*Repeated XOR with the identity introduces no new distinction.*

**XOR equivalence.**

$$x\sim y\iff x\oplus y=0\quad\Longleftrightarrow\quad x=y$$

*Each configuration is its own equivalence class under XOR cancellation.*

No configuration is privileged as the ontological origin of the Library. A mathematical generator, a chosen reference configuration, or an observer-relative origin may be useful for describing relations, but none becomes the origin of $\mathcal{M}$ merely by being selected.

**Reference invariance.**

$$\forall x\in\mathcal{M}_{\mathrm{admissible}},\quad x\ \mathrm{may\ serve\ as\ a\ relational\ reference\ without\ altering}\ \mathcal{M}$$

*Reference relocation changes the relational description, not the underlying totality.*

**Definition — Definition 3.6 — Static Maximality.** The Library is maximally complete relative to the formal ontology of the model. A configuration is not excluded merely because it has not been encountered, resolved, or traversed by an observer.

**Static invariance.**

$$\forall i,\quad\mathcal{M}_{i}=\mathcal{M}$$

*The Library does not change as observer-relative traversal changes.*

Static maximality is a semantic condition of the Library and must not be confused with closure minimality. Closure identifies the smallest XOR-closed set containing a chosen generator. The interpretation of $\mathcal{M}$ as the maximally complete totality is a stronger model-level definition and is not claimed to follow from closure minimality alone.

**Definition — Definition 3.7 — Whole-Library Relationality.** An observer-relative reference configuration is situated relationally with respect to the whole Library. Observer state, history, resolution, and coherence determine accessible relations but do not determine membership in $\mathcal{M}$.

**Accessibility as a relation over the Library.**

$$\mathcal{A}_{O}(h,x)\subseteq\mathcal{M},\qquad x\in\mathcal{M}$$

*Accessibility is observer-relative structure over the Library, not a mechanism that creates or deletes Library membership.*

At this stage, membership in $\mathcal{M}$ therefore carries no implication of persistence, coherence, observability, accessibility, physical realization, consciousness, or causal participation. Those properties belong to later relational constructions over the unchanged totality.

**Logical Invariants**

- XOR is the sole primitive operation of distinction.
- The Library is a definition, not a second axiom.
- Closure_D(⊕;G) is a mathematical characterization rather than a temporal generation process.
- The generating set G is representational and is not an ontological origin.
- The Library is closed under XOR.
- The Library is static and invariant under traversal.
- The Library is relationally complete in the stated representational sense.
- The Library contains no describable privileged exterior under the formal resources of the system.
- 𝒵 is an internal termination/self-cancellation state rather than an exterior.
- Library membership does not imply observer accessibility.
- Accessibility and coherence do not create or delete Library configurations.
- No privileged observer, coordinate, worldline, or origin is introduced.

This subsection has established XOR closure as a property of the Library rather than a temporal generation process, together with self-containment, relational completeness, and the internal status of the termination singleton $\mathcal{Z}$. The Library now stands as a static, maximally complete, relationally complete totality with no describable privileged exterior and no privileged origin. What remains is to characterize it as an unbounded total configuration space and to distinguish that space from any observer-accessible subset, so that the boundary between Library membership and observer-relative accessibility can be drawn without remainder.

---

| PREVIOUS | | NEXT |
| --- | --- | --- | 
| [prev_section](URL) | [INDEX](URL) | [next_section](URL) |
