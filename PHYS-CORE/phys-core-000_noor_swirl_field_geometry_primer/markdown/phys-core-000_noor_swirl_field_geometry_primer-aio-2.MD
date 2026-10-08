[...Continued from Part 1](phys-core-000_noor_swirl_field_geometry_primer-aio-1.MD)

### 10.1 The Local Continuation Problem

Let $x_i\in\mathcal{M}_{\mathrm{admissible}}$ be the current observer-relative reference configuration. The Library $\mathcal{M}$ is a static, maximally complete totality; traversal does not generate new Library states, and no step of traversal creates a new copy or version of $\mathcal{M}$. The continuation problem therefore concerns the ordering of a path through an already existing relational domain, not the production of an ontological future.

**Definition — Observer-Relevant History.** The ordered history terminating at the current reference is represented by $h_i$.

$$h_i=(x_0,x_1,\ldots,x_i)$$

*The history records the observer's traversal relation. Its index is an abstract ordering coordinate rather than primitive physical time.*

**Definition — Candidate Continuation.** The structurally available immediate continuations are determined from paths contained in the unchanged Library.

$$N(x_i)=\{x_{i+1}\in\mathcal{M}\mid\exists\gamma\in\mathrm{Path}(\mathcal{M})\ \mathrm{such\ that}\ \gamma\ \mathrm{extends}\ h_i\ \mathrm{with}\ x_{i+1}\ \mathrm{as\ its\ next\ ordered\ position}\}$$

*The successor relation describes possible ordered traversal through configurations already represented in* $\mathcal{M}$.

Navigation is the continuation problem that all domains share. In physical contexts, navigation corresponds to the evolution of a physical system through configuration space; in AI contexts, to the traversal of a reasoning graph; in financial contexts, to movement through market states. The structural problem is the same in all domains: from a current reference configuration, identify a coherent continuation within the unchanged Library. The foundation therefore establishes the common continuation problem without requiring a domain-specific navigation algorithm.

**Definition — Observer-Relative Coherent Continuation.** The coherent continuation space consists of paths extending the current history whose transitions remain coherent for observer $O$.

$$\Gamma_O(h_i,x_i)=\{\gamma\in\mathrm{Path}(\mathcal{M})\mid\gamma\ \mathrm{extends}\ h_i\ \mathrm{from}\ x_i\ \mathrm{and}\ \mathcal{C}(\gamma\mid O)=1\}$$

*The observer does not receive a newly generated future. It is relationally situated within the unchanged totality and can sustain only those continuations whose distinctions remain coherent at its resolution.*

**Immediate Observer-Relative Coherence.**

$$\mathcal{C}_O(x_i,x_{i+1}\mid h_i)=\Theta\left(\delta_O(x_i,x_{i+1}\mid h_i)-I_N(O)\right)$$

*The transition remains coherent when the effective distinction resolvable by* $O$ *is at least as large as the observer's resolution threshold.*

**Observer-Admissible Successors.**

$$N_O(h_i,x_i)=\{x_{i+1}\in N(x_i)\mid\mathcal{C}_O(x_i,x_{i+1}\mid h_i)=1\}$$

*Observer-relative navigation narrows the continuation relation without narrowing the underlying Library.*

The coherence relation is explicitly relational. It is not a property possessed by $x_i$, $x_{i+1}$, or a path independently of the observer and its reference conditions. The same configurations may therefore participate in different accessible continuation structures for different observers. This is the point at which navigation becomes domain-neutral: physical systems, AI reasoning systems, financial systems, and other structured domains can instantiate different observer-relative resolutions over the same foundational relation without requiring separate ontologies.

**Formal Statement — Ontology and Accessibility Remain Distinct.** Observer-relative restriction does not alter Library membership.

$$N_O(h_i,x_i)\subseteq N(x_i)\subseteq\mathcal{M}$$

*A configuration can fail to belong to the currently sustainable continuation relation while remaining fully contained in the Library.*

Thus the observer does not select from a Library that is being generated around it. Rather, the observer establishes a relational reference within the unchanged totality and evaluates which existing path continuations remain coherent relative to that reference. The resulting continuation set may be restricted even though the underlying Library is not. A configuration excluded by observer-relative coherence is not removed from $\mathcal{M}$, nor is it assigned to an ontological future that has failed to occur. It simply does not belong to the continuation relation currently sustainable by $O$ under the specified reference conditions.

**Example.** *Setup:* Suppose two configurations $x_i$ and $x_{i+1}$ are both members of $\mathcal{M}$, and the path containing their transition is structurally represented in $\mathrm{Path}(\mathcal{M})$. *Result:* If $\delta_O(x_i,x_{i+1}\mid h_i)\ge I_N(O)$, the transition is coherent for $O$ and may belong to $N_O(h_i,x_i)$. If the distinction falls below $I_N(O)$, the transition is not currently sustainable by $O$, even though both configurations remain members of $\mathcal{M}$. *Interpretation:* Observer-relative inaccessibility is a restriction of traversal, not erasure from the underlying totality.

Persistence can therefore be expressed as the maintenance of coherent ordered transitions. For a traversal $\gamma=(x_0,x_1,\ldots,x_n)$, persistence for $O$ requires that each relevant transition remain above the observer's effective resolution condition. The resulting sequence is not a sequence of newly generated Library states. It is an ordered traversal relation established over the unchanged totality.

**Persistence Along a Coherent Traversal.**

$$\gamma=(x_0,x_1,\ldots,x_n),\qquad P_O(\gamma,n)=1\iff\forall i<n,\ \mathcal{C}_O(x_i,x_{i+1}\mid h_i)=1$$

*Persistence is the maintenance of observer-resolvable distinction across the ordered traversal.*

The model may additionally impose a continuation requirement on admissible reference configurations:

$$\forall x\in\mathcal{M}_{\mathrm{admissible}},\quad\Gamma_O(h,x)\neq\varnothing$$

*This expresses the requirement that an admissible observer-relative reference admit at least one coherent continuation. It is deliberately stated as a model requirement rather than as an unsupported consequence of maximality alone.*

**What the Local Continuation Problem Does Not Mean**

- It does not mean that the Library generates a future.
- It does not mean that $x_{i+1}$ comes into existence after $x_i$.
- It does not mean that the traversal index $i$ is physical time.
- It does not mean that the observer consciously chooses a path.
- It does not mean that inaccessible configurations cease to exist.
- It does not mean that the Library is locally generated around the observer.

The local continuation problem is therefore not 'What future does the Library generate from $x_i$?' It is: given an unchanged totality, an observer $O$, a relevant history $h_i$, and a current relational reference $x_i$, which ordered continuations through $\mathcal{M}$ remain coherent? The construction can be summarized as:

$$\mathcal{M}\;\longrightarrow\;\mathrm{Path}(\mathcal{M})\;\longrightarrow\;N(x_i)\;\longrightarrow\;N_O(h_i,x_i)\;\longrightarrow\;\Gamma_O(h_i,x_i)$$

*The Library supplies the unchanged totality; its path structure supplies candidate continuations; observer-relative coherence restricts those candidates; the resulting continuation space is the structure within which navigation operates.*

Navigation therefore begins as a relational continuation problem over a static totality. The observer's experienced succession is real as an ordering relation within its traversal, while the underlying Library remains invariant throughout. This construction is deliberately domain-neutral: the physical, computational, financial, or other meaning of a traversal may be supplied later without changing the foundational continuation problem.

**Logical Invariants**

- The Library remains unchanged under traversal.
- Candidate continuations are relations over $\mathrm{Path}(\mathcal{M})$, not generated future states.
- Observer-relative coherence restricts accessibility without changing membership in $\mathcal{M}$.
- Persistence is the maintenance of distinguishable transitions across an ordered chain.
- The observer is relationally situated with respect to the whole Library.
- The existence of a coherent continuation from every admissible reference is a model requirement rather than a consequence asserted from maximality alone.
- Navigation is domain-neutral at the foundational level.
- No physical time, causality, agency, or consciousness is required by the local continuation construction.

The local continuation problem is thus the formal bridge between the static totality of the Library and the observer's ordered traversal within it. It establishes that continuation is a relational structure over an unchanged domain rather than a generative process, and it introduces the successor relation, the coherent continuation space, and the persistence condition that the following subsection will extend into history-indexed continuation.

---

## 10.2 History and Coherent Continuation

An observer history is an ordered relational structure embedded within the static Library, not a process that generates or modifies the Library. Let $O$ denote an observer and let $x_0,x_1,\ldots,x_n \in \mathcal{M}$ denote configurations related by an observer-maintained sequence, with $x_n$ representing the observer's current relational reference.

**Definition — Observer history.** The observer history is the ordered sequence of configurations maintained by the observer.

$$h_n = (x_0,x_1,\ldots,x_n)$$

*The sequence records abstract traversal ordering. The index* $n$ *does not represent physical time, duration, causality, or any other physical quantity.*

The Library is not correspondingly ordered into successive ontological states. Its totality remains invariant under traversal, expressed formally by $\forall i,\ \mathcal{M}_i = \mathcal{M}$. The indexed notation is only a device for stating invariance; it does not imply that multiple temporal copies of the Library exist. The observer changes relational reference from one configuration to another while the total configuration domain remains unchanged.

**Library invariance under traversal.**

$$\forall i,\;\mathcal{M}_i = \mathcal{M}$$

*The notation states that observer traversal does not modify the Library. The indexed form is a formal expression of invariance, not a claim that multiple temporal copies of the Library exist.*

**Observer history.**

$$h_n = (x_0,x_1,\ldots,x_n)$$

*The history records an ordered sequence of observer-relative references. The ordering index is abstract and does not itself represent physical time.*

This establishes the separation between the Library, the observer, and the observer-relative continuation structure. The Library is the static, maximally complete totality $\mathcal{M}$. The observer is represented structurally by its persistent chain of maintained distinctions and its current relational reference $x_n$. The coherent continuation relation is evaluated over the unchanged whole $\mathcal{M}$ rather than over a locally generated future region.

For a given observer $O$ and history $h_n$ with current reference $x_n$, the full continuation space contains paths already represented within the Library that begin at $x_n$. The observer-relative coherent continuation set is obtained by applying the canonical coherence relation to those paths.

**Full continuation space.**

$$\Omega(x_n) = \{\gamma \in \mathrm{Path}(\mathcal{M}) \mid \gamma\ \mathrm{begins\ at}\ x_n\}$$

*The continuation space contains all represented paths beginning at the current reference configuration, before observer-relative coherence filters them.*

**Coherent continuation.**

$$\Gamma_O(h_n) = \{\gamma \in \Omega(x_n) \mid \gamma\ \mathrm{extends}\ h_n\ \mathrm{and}\ \mathcal{C}(\gamma \mid O)=1\}$$

*Only continuations whose transitions remain resolvable by observer* $O$ *are retained in the observer-relative coherent continuation set.*

The use of the canonical coherence relation is deliberate. No separate $\gamma_{\mathrm{noise}}$ threshold is required at this foundational level. The observer-relative resolution floor $I_N(O)$ already enters the chain through $\delta_O := \mu_O(x \oplus y)$ and $\mathcal{C}(\gamma \mid O)$. Introducing a second threshold without an independent definition would duplicate the same filtering role and obscure the dependency structure.

The explicit dependence on the current reference $x_n$ remains important even though the canonical continuation notation $\Gamma_O(h_n)$ is sufficient to identify that reference through the final element of $h_n$. Navigation does not move through a Library that is being generated ahead of the observer. Instead, navigation changes the observer's relational reference within an already complete totality.

The observer's new state therefore changes its history and current reference while leaving $\mathcal{M}$ unchanged. In this sense, an observer worldline is represented as a relational structure extending across the totality: the ordered sequence records the traversal maintained by the observer, while the configurations related by that sequence remain members of the same static Library.

The observer is consequently relationally situated with respect to the whole Library rather than assigned a privileged local container. A current reference configuration establishes the relation from which coherence is evaluated, but it does not partition the Library into ontologically separate past, present, and future regions. Past and future are therefore traversal orderings within the observer's history rather than intrinsic regions of $\mathcal{M}$.

A configuration occurring earlier in the history is not thereby assigned permanent membership in a designated past region, and a coherent continuation is not generated into a corresponding future region. Both are configurations represented within the same totality and related differently by the observer's ordered history.

**Formal Statement — Library membership versus accessibility.** The existence of a path in the Library does not imply observer-relative coherence.

$$\gamma \in \mathrm{Path}(\mathcal{M}) \not\Rightarrow \gamma \in \Gamma_O(h_n)$$

*Library representation and observer-relative survivorship are distinct relations.*

Conversely, failure of a path to satisfy the observer-relative coherence condition does not remove that path from $\mathcal{M}$. Survivorship filters the observer's maintained traversal relation; it does not shrink, rewrite, or erase the underlying totality. The observer therefore experiences a restricted continuation space without requiring the ontology itself to be restricted.

**Coherent subset relation.**

$$\Gamma_O(h_n) \subseteq \Omega(x_n)$$

*The restriction is observer-relative and epistemic/accessibility-based within the formal model, not an ontological deletion from the Library.*

**Admissible continuation requirement.**

$$\forall x \in \mathcal{M}_{\mathrm{admissible}},\;\Gamma_O(h,x) \neq \varnothing$$

*This is an explicit continuation requirement of the model. It is not claimed to be a theorem derived from maximality alone.*

The distinction between maximality and continuation must be preserved. Maximal static totality establishes that Library membership does not depend upon a privileged construction history or external generating event. The non-emptiness condition separately requires that an admissible observer-relative reference support continued coherent traversal. These are logically distinct statements.

The continuation structure may contain many candidate paths even when only a restricted subset remains coherent for a particular observer. The difference $\Omega(x_n) \setminus \Gamma_O(h_n)$ therefore represents paths that remain represented within the Library but do not survive the observer's present coherence condition.

**Navigation.**

$$N_O(h_n) \rightarrow \Gamma_O(h_n)$$

*The operator specifies the continuation space available to navigation but does not prescribe how a particular continuation is selected.*

The navigation operator does not specify an algorithm, optimization rule, probability distribution, conscious choice, agency, or physical mechanism. It states only that navigation is the traversal or selection of a continuation within the observer-relative coherent continuation set. When navigation produces a new observer state, the relational variables change; the Library does not.

**Formal Statement — Foundational dependency chain.** The dependency structure for this subsection is

$$\mathrm{distinction}\rightarrow\mathrm{persistence}\rightarrow\mathrm{history}\rightarrow\mathrm{reference}\rightarrow\mathrm{relational\ coherence}\rightarrow\mathrm{coherent\ continuation}\rightarrow\mathrm{navigation}$$

*Each construction remains downstream of the axiomatic floor. No later construction is promoted into a primitive premise of an earlier one.*

**Preserved distinctions**

- History does not introduce physical time.
- Reference does not introduce a privileged frame.
- Coherence is not an intrinsic property of a path independent of an observer.
- Continuation does not generate new ontology.
- Survivorship filters observer-relative accessibility rather than deleting alternatives.
- Navigation does not modify the Library.
- Observerhood does not require consciousness or agency.
- The abstract continuation structure is not identified with physical spacetime.

The resulting formal picture is a static totality together with an observer-relative traversal relation over that totality. The road does not become as the traveler moves; rather, the traveler changes relational reference within a road that is already complete. Apparent temporal progression and restriction of available continuation are therefore properties of the observer's changing relation to $\mathcal{M}$, not successive ontological states of $\mathcal{M}$ itself.

For later NSFG work, $h_n$, $x_n$, $\Gamma_O(h_n)$, $\mathcal{C}(\gamma \mid O)$, and $N_O(h_n)$ provide the formal interface between the foundational layer and downstream models. A later theory may specify how continuations are represented, ranked, traversed, or transformed, but those mechanisms are not required here. The axiomatic floor ends once coherent continuation has been identified as a relational traversal problem over an unchanged, maximally complete Library.

With history, coherent continuation, and navigation now separated from any notion of Library generation, the next stage may interpret these observer-relative relations geometrically. The static totality remains unchanged while coherence selects the relational accessibility structure through which observer-relative traversal is organized.

**Logical Invariants**

- The Library $\mathcal{M}$ remains unchanged under observer traversal.
- Observer history is an abstract ordering and is not automatically physical time.
- The current reference $x_n$ is relational and does not constitute a privileged origin of the Library.
- The full continuation space $\Omega(x_n)$ is represented within the unchanged Library.
- The coherent continuation set $\Gamma_O(h_n)$ is a subset of $\Omega(x_n)$.
- Coherence is evaluated through the observer-relative resolution floor $I_N(O)$.
- No independent $\gamma_{\mathrm{noise}}$ threshold is introduced at the foundational level.
- Library membership is independent of observer-relative accessibility.
- Survivorship does not erase non-surviving paths from the Library.
- Every admissible observer-relative reference configuration is required to admit at least one coherent continuation.
- Navigation changes observer-relative history and reference rather than Library membership.
- Continuation is traversal through represented structure, not generation of future ontology.

---

## 11. The Noor Swirl Field Geometry Interpretation

The axiomatic floor has now established a formal configuration domain, its XOR closure as the Library, observerhood as a persistent structural property, observer-relative resolution through $I_N(O)$, and coherence as a relation between paths and observers. Only at this point is it appropriate to introduce geometric language. Noor Swirl Field Geometry (NSFG) does not begin by assuming a geometry in which configurations exist. Rather, geometry appears as a description of the relational structure formed by configurations, accessible transitions, and families of paths that remain coherent for a given observer.

For an observer $O$, the coherent paths through the Library form a restricted family of traversable structures. Define the observer-coherent path family by

**Observer-coherent path family.**

$$\Gamma_O = \{\gamma \mid \mathcal{C}(\gamma \mid O)=1\}$$

*The set* $\Gamma_O$ *contains paths that remain coherent relative to* $O$. *It is therefore not a universal set of physically preferred trajectories. A path belongs to* $\Gamma_O$ *because of its relation to the observer's resolution structure, not because coherence is an intrinsic property of the path alone.*

The same construction permits a local description around an accessible configuration $x$. Let

**Observer-relative accessibility neighborhood.**

$$U_O(x) = \{y \in \mathcal{M} \mid y\ \mathrm{is\ reachable\ from}\ x\ \mathrm{by\ an}\ O\mathrm{-coherent\ path\ segment}\}$$

$U_O(x)$ *is not assumed to be a geometric neighborhood in the conventional metric sense. It is an accessibility neighborhood: the collection of configurations that can be reached from* $x$ *through path segments that remain coherent relative to* $O$. *If later NSFG work supplies additional structure, this relational neighborhood may acquire familiar geometric interpretations. The axiomatic floor itself does not require such an interpretation.*

The accessible relational structure can therefore be represented as a graph. Define

**Accessible relational graph.**

$$G_O := (A_O,E_O)$$

*Here* $A_O$ *is the observer-accessible state set already established by the preceding construction, while* $E_O$ *records coherent relational connections between accessible configurations.*

**Graph edge relation.**

$$(x,y) \in E_O \iff x\to y\ \mathrm{is\ an}\ O\mathrm{-coherent\ transition}$$

*The edge relation records observer-relative coherent transitions. Depending on the requirements of a later formalism, the relation may be represented as directed, preserving transition orientation, or as undirected when orientation is not relevant. Neither choice is imposed by the axiomatic floor.*

The word 'field' in Noor Swirl Field Geometry should therefore be understood initially as descriptive rather than ontological. A field, at this level, is a structured distribution of relational possibilities: which configurations are connected, which transitions remain coherent, and how families of coherent paths organize around persistent configurations. No additional field substance is introduced.

Likewise, 'geometry' is descriptive language for the structure of relations among accessible configurations and paths. At this stage, geometry means that the relational system has organization that can be studied in terms of neighborhoods, connectivity, path families, adjacency, and continuation. This is deliberately weaker than assuming a metric space or differentiable manifold.

No metric tensor, coordinate chart, manifold structure, curvature tensor, or other conventional geometric object is required by the axiomatic floor. Such structures may become useful later if they can be derived or consistently introduced as downstream constructions.

The term 'swirl' provides an intuition for how locally structured path families may organize around persistent relational configurations. A persistent configuration can participate in many coherent continuations, while the observer-relative resolution threshold restricts which transitions remain admissible. The resulting family of paths can possess local structure: paths may converge, diverge, braid, circulate, or repeatedly organize around persistent configurations. 'Swirl' names this qualitative possibility of structured local path organization.

The term is intentionally intuitive at this stage. It does not assert literal rotational motion, angular momentum, fluid dynamics, or a physical vortex. In particular, no temporal evolution or physical movement is implied merely by the word 'flow'. The underlying construction remains a set of configurations and relations among paths.

The graph representation makes the geometric interpretation concrete without requiring physical geometry. The accessible configurations form vertices, while coherent transitions form edges. Families of coherent paths then become sequences through this relational graph. Local structure can be studied through the accessible neighborhood $U_O(x)$, while larger-scale structure can be studied through connected path families and continuation spaces.

**Graph and coherent-path representation.**

$$G_O=(A_O,E_O), \qquad \Gamma_O=\{\gamma\mid\mathcal{C}(\gamma\mid O)=1\}$$

*This representation places the graph and coherent path family within the dependency structure established by the primer.*

This representation preserves the foundational ordering established by the primer: the graph is constructed from accessibility and coherence; coherence is constructed from observer-relative distinguishability; distinguishability depends on $I_N(O)$ and the observer-relative magnitude evaluation $\mu_O$; observerhood is derived from persistent distinctions; and the Library itself is defined as XOR closure. Geometry therefore enters downstream of the axiomatic floor rather than being smuggled into it at the beginning.

This distinction is important because NSFG, at this stage, is not claiming that the accessible graph $G_O$ is physical spacetime. The graph is a formal relational object. A later theory may investigate whether familiar physical geometries can emerge from additional structure imposed upon, or derived from, these relational configurations. Such a derivation would be a subsequent result, not a premise of this primer.

**Foundational boundaries**

- $G_O$ is not identified with physical spacetime.
- No specific metric tensor is derived here.
- No manifold structure is assumed here.
- No spacetime geometry is assumed here.
- No physical field equation is introduced here.
- No physical dynamics are required for the geometric interpretation presented here.

The geometric language of NSFG is one possible interpretation. In physical contexts, the relational graph $G_O$ may be interpreted as a configuration space or phase space; in AI contexts, as a reasoning graph or knowledge structure; in financial contexts, as a market-state graph or opportunity space. The underlying formal structure is unchanged across these interpretations. The field is the organization of relations; the geometry is the structure of that organization; the domain-specific meaning belongs to the observer's resolution and interpretation of the relations.

The cross-domain character of this interpretation does not introduce separate foundational ontologies for physics, AI, finance, or other domains. The formal chain remains domain-neutral. Domain-specific meaning enters through the observer-relative magnitude evaluation $\mu_O$, resolution floor $I_N(O)$, resulting coherence relation, and the downstream interpretation assigned to the accessible relational structure.

The Noor Swirl Field Geometry interpretation can therefore be stated conservatively: NSFG studies the geometry of relational accessibility induced by observer-relative coherence within the XOR-closed Library. The field is the organization of relations; the geometry is the structure of that organization; and the swirl is an intuition for locally structured families of surviving paths around persistent relational configurations. None of these descriptions adds a new primitive to the axiomatic floor.

**Logical Invariants**

- Geometry is introduced only after the formal ontology, observer structure, distinguishability, coherence, and accessibility constructions.
- $G_O$ is a downstream relational graph induced by observer-relative accessibility and coherence.
- $U_O(x)$ is relational reachability, not metric distance.
- $\Gamma_O$ is an observer-relative coherent path family.
- The formal structures of NSFG are domain-neutral at this stage.
- Domain-specific interpretation enters through $\mu_O$, $I_N(O)$, coherence, accessibility, and downstream interpretation.
- Field is descriptive relational organization, not an additional primitive substance.
- Geometry is descriptive organization of relations, not an assumed physical container.
- Swirl is qualitative intuition for structured path organization, not literal physical rotation.
- The formal relational structure does not itself establish physical spacetime.
- The Library remains unchanged under observer-relative geometric interpretation.
- The transition from relational structure to geometric interpretation does not alter the axiomatic dependency chain.

With the geometric interpretation now explicitly cross-domain, the formal relational structure $G_O$ remains domain-neutral at the level of its construction. The axiomatic dependency chain that compresses the entire primer—and that marks the boundary between this foundational work and downstream NSFG research—is the natural continuation of the present section.

---

## 12. The Axiomatic Dependency Chain

The primer can now be compressed into a single dependency architecture. The essential point is not merely the order in which concepts appear, but the logical status of each concept and the strict separation between the Library itself and the observer's relation to it. XOR is the sole primitive operation of distinction. $D$ is the minimal formal domain required for XOR to operate. $G$ specifies the generating configurations used to characterize the XOR closure. The Library $\mathcal{M}$ is the static, maximally complete totality characterized by closure under XOR together with self-containment and the absence of a privileged definable exterior. Closure is a formal property, not a temporal generation process. Traversal does not enlarge, modify, or generate the Library. Instead, an observer is relationally situated with respect to the whole $\mathcal{M}$, establishes an admissible reference configuration, and evaluates distinctions, persistence, coherence, accessibility, and continuation relative to that reference, its history, and its observer-specific resolution. Apparent temporal ordering, locality, increasing complexity, and restricted possibility therefore belong to the observer's traversal relation rather than to an intrinsic evolution of the Library. No later concept is permitted to become a hidden premise of an earlier one.

A philosophical distinction must be maintained throughout the interpretation of this framework. Ontologically, the Library is static and complete. No new configurations are generated, and no Library member is ever added or removed. Epistemically, however, an observer may discover new coherence relations, experience novel paths, and construct new accessible subsets as its relational history, resolution, or reference changes. The distinction is essential: the Library does not grow, but the observer's relation to it may become richer. This permits genuine discovery and learning without requiring the Library to evolve or generate new ontology. Discovery is possible because what is discovered is already represented within the totality; what changes is the observer's relation to it.

**Formal Statement — Step 1 — Primitive distinction.** AXIOM. The axiomatic floor begins with one primitive operation: XOR. No physical object, space, time, observer, causality, matter, energy, or information substance is assumed. XOR expresses distinction: equal inputs cancel to $0$, while unequal inputs produce $1$.

$$A_N = \{A_{\oplus}\}, \qquad a \oplus b = 1 \iff a \ne b$$

**Formal Statement — Step 2 — Formal configuration domain.** DEFINITION. $D$ is the minimal formal domain containing the configurations required for $\oplus$ to have operands. $D$ is introduced because an operation requires a domain on which it acts. $D$ is not physical space, spacetime, matter, energy, information, or an additional physical ontology.

$$\oplus : D \times D \to D$$

**Formal Statement — Step 3 — Static maximally complete Library.** DEFINITION + INVARIANT. The Library is the maximally complete static totality characterized by XOR closure over $D$, containing the specified generating configurations $G$, and satisfying self-containment with respect to its formal resources. Closure specifies a formal property of the totality; it is not a temporal generation mechanism. The Library does not progressively come into existence through repeated XOR operations. There is one unchanged totality rather than a succession of increasingly complete Libraries. Membership in the Library does not imply persistence, coherence, physicality, observability, accessibility, consciousness, or causal participation.

$$\mathcal{M} := \mathrm{Closure}_D(\oplus,G), \qquad G \subseteq \mathcal{M}, \qquad \forall x,y \in \mathcal{M},\; x \oplus y \in \mathcal{M}$$

**Formal Statement — Step 4 — No privileged worldline or universal reference.** INVARIANT. No configuration, worldline, traversal history, or observer is privileged as the universal origin from which the whole Library must be constructed or evaluated. Maximality is structurally connected to reference-frame neutrality, not merely to maximizing the number of configurations.

$$\nexists\,w_{\mathrm{priv}}\ \mathrm{such\ that}\ w_{\mathrm{priv}}\ \mathrm{is\ the\ unique\ universal\ reference\ for}\ \mathcal{M}$$

**Formal Statement — Step 5 — No describable privileged exterior.** CONSEQUENCE. An external candidate may be proposed informally, but if it is describable using the same formal machinery, it belongs to the formal domain to which the closure applies. The closure therefore establishes a formal boundary condition on describable exteriors. It does not independently assert that every informal notion of literal physical exteriority is impossible.

$$\Omega\ \mathrm{describable\ within\ the\ same\ formal\ machinery} \Rightarrow \Omega \in D, \qquad \Omega\ \mathrm{XOR\hbox{-}generable} \Rightarrow \Omega \in \mathcal{M}$$

**Formal Statement — Step 6 — Whole-Library relationality.** INVARIANT. The observer is relationally situated with respect to the whole Library rather than occupying an ontologically isolated local region from which the remainder of the Library is external. Locality is therefore a property of relational access and traversal, not a partition of the Library into an observer-containing region and an intrinsically external remainder.

$$O \subseteq \mathcal{M}, \qquad O\ \mathrm{is\ relationally\ evaluated\ with\ respect\ to}\ \mathcal{M}$$

**Formal Statement — Step 7 — Admissible reference configuration.** DEFINITION. An admissible reference configuration is a configuration capable of instantiating an observer-relative reference state under the model's admissibility conditions. The reference configuration does not create a new ontological layer or select a new Library. It specifies the configuration from which the observer's current relational evaluation is made.

$$x \in \mathcal{M}_{\mathrm{admissible}}, \qquad \mathcal{M}_{\mathrm{admissible}} \subseteq \mathcal{M}$$

**Formal Statement — Step 8 — Observer.** DEFINITION. Observerhood is introduced structurally rather than psychologically. An observer is a configuration capable of maintaining a persistent chain of resolvable distinctions. The definition does not require consciousness, intention, agency, perception, or a human subject.

$$O \in \mathrm{Obs} \subseteq \mathcal{M}$$

**Formal Statement — Step 9 — Observer-relative resolution.** DEFINITION. Each observer $O$ is assigned an effective minimum distinction magnitude that it can maintain as a stable distinction. $I_N(O)$ belongs to the observer relation rather than to the Library as a universal constant. No universal numerical value for $I_N$ is supplied by the axiomatic floor, and $I_N$ is not identified with the ordinary Planck scale.

$$I_N : \mathrm{Obs} \to \mathbb{R}_{>0}, \qquad I_N(O) > 0$$

**Formal Statement — Step 10 — Observer-relative distinguishability from XOR.** DEFINITION DERIVED FROM THE PRIMITIVE. The distinction between $x$ and $y$ is first produced by the primitive operation $x \oplus y$. The observer does not introduce a second primitive operation to measure that distinction; rather, observer-relative resolution supplies the effective magnitude with which the resulting distinction is evaluated. This closes the dependency gap between XOR and distinguishability without assigning a universal metric to the Library. Two configurations may therefore be distinguishable for one observer and indistinguishable for another without requiring either configuration to cease existing in the Library. Indistinguishability is a relational statement, not ontological deletion.

$$\delta_O(x,y) := \mu_O(x \oplus y), \qquad \mu_O : D \to \mathbb{R}_{\geq 0}$$

*The primitive XOR produces the distinction;* $\mu_O$ *supplies its observer-relative effective magnitude. The foundational system therefore does not require a universal metric to be imposed on the Library.*

**Step 10 — Observer-relative distinguishability thresholds.** Observer-relative distinguishability is determined by comparison between the effective magnitude of a distinction and the observer's resolution floor.

$$x \approx_O y \iff \delta_O(x,y) < I_N(O), \qquad x \not\approx_O y \iff \delta_O(x,y) \geq I_N(O)$$

$\mu_O$ is deliberately underspecified at the foundational level. Its specific functional form is a downstream construction that may vary by domain. In a physical domain, $\mu_O$ may represent a resolution scale related to measurement precision; in an AI domain, it may represent a symbolic distinctness threshold; in a financial domain, it may represent a minimum actionable distinction. The structural relation $\delta_O(x,y) := \mu_O(x \oplus y)$ remains unchanged; only the interpretation of $\mu_O$ varies. The foundational primitive remains Boolean XOR, so the primitive itself supplies a distinction floor rather than a universal continuous geometry. Any continuous magnitude associated with a distinction is therefore an observer- and domain-relative downstream evaluation, not an additional primitive.

**Formal Statement — Step 11 — Observer history and abstract traversal ordering.** DEFINITION. Observer history is an ordered sequence relevant to the observer's current relational evaluation. The sequence index is an abstract traversal index rather than a primitive physical time coordinate. It does not partition the Library into intrinsic past, present, and future regions.

$$h_n = (x_0,x_1,\ldots,x_n), \qquad i \in \{0,1,\ldots,n\}$$

**Formal Statement — Step 12 — Observer-relative coherence.** DEFINITION. Coherence evaluates whether a traversal remains coherent relative to observer $O$, relevant history $h$, and current reference configuration $x$. Coherence is relational rather than intrinsic to a path considered in isolation. The mathematical structure remains domain-neutral and may later be interpreted in physical, AI, financial, or other domain-specific contexts.

$$\mathcal{C}_O(x_i,x_{i+1} \mid h,x) = \Theta\!\left(\delta_O(x_i,x_{i+1} \mid h,x) - I_N(O)\right)$$

**Step 12 — Path coherence.** A path is coherent when each transition in the relevant traversal satisfies the observer-relative coherence condition.

$$\mathcal{C}(\gamma \mid O,h,x) = \prod_{i=0}^{n-1} \mathcal{C}_O(x_i,x_{i+1} \mid h,x)$$

**Formal Statement — Step 13 — Observer-accessible reality.** DEFINITION. Observer-accessible reality is the subset of the Library reachable through observer-maintained coherent traversal from the relevant relational state. A configuration outside this accessible subset is not removed from the Library. Accessibility therefore does not create ontology, and inaccessibility does not constitute erasure.

$$A_O(h,x) = \{y \in \mathcal{M} \mid \exists \gamma\ \mathrm{containing}\ y\ \mathrm{such\ that}\ \mathcal{C}(\gamma \mid O,h,x) = 1\} \subseteq \mathcal{M}$$

**Formal Statement — Step 14 — Whole-Library continuation space.** DEFINITION. Continuation is evaluated over the static Library. The Library does not generate a future when the observer reaches $x$. Rather, the observer's traversal relation identifies ordered continuations already represented within the unchanged totality.

$$\Omega(x) = \{\gamma \mid \gamma\ \mathrm{begins\ at}\ x\ \mathrm{and}\ \gamma \subseteq \mathcal{M}\}$$

**Formal Statement — Step 15 — Nonempty coherent continuation.** DERIVED REQUIREMENT. For every admissible observer-relative reference configuration, the model requires at least one observer-coherent continuation. This requirement is not a theorem obtained from XOR closure alone. It is a structural condition imposed on the observer-relative traversal model.

$$\forall x \in \mathcal{M}_{\mathrm{admissible}},\; \Gamma_O(h,x) \ne \varnothing$$

**Formal Statement — Step 16 — Observer-relative coherent continuation.** DEFINITION. The coherent continuation space is a restricted relational structure over the unchanged Library. The restriction belongs to observer-relative evaluation, not to Library membership. No future configuration is generated when a continuation is selected; the observer traverses a path already represented within the static totality.

$$\Gamma_O(h,x) = \{\gamma \in \mathrm{Path}(\mathcal{M}) \mid \gamma\ \mathrm{extends}\ h\ \mathrm{from}\ x\ \land\ \mathcal{C}(\gamma \mid O,h,x) = 1\}$$

**Formal Statement — Step 17 — Emergent temporal and complexity structure.** CONSEQUENCE. Ordered traversal through an unchanged Library can produce an observer-relative experience of temporal direction, locality, increasing complexity, and past/future distinction. The Library does not evolve from simple to complex. What changes is the observer's relational state and history.

$$\mathcal{M}_i = \mathcal{M}\ \forall i, \qquad O(h_i) \ne O(h_j)\ \mathrm{may\ hold\ for}\ i \ne j$$

**Formal Statement — Step 18 — Emergent regularity.** CONSEQUENCE. Repeated survivorship can produce regularities that are describable in law-like terms. Such regularity is descriptive and derived. It is not an additional element of the axiom set and does not constitute a derivation of any particular physical law.

$$L_O(x,y) = 1 \iff x \to y\ \mathrm{is\ a\ stable\ recurring\ transition\ across\ an\ appropriate\ family\ of\ O\hbox{-}accessible\ traversals}$$

**Step 18 — Probabilistic form of emergent regularity.** Where an observer-accessible ensemble is defined, recurring transitions may be represented probabilistically.

$$P_O(y \mid x) \approx \mathrm{constant}$$

**Formal Statement — Step 19 — Navigation.** DEFINITION / DOWNSTREAM THRESHOLD. Navigation is the traversal or selection of a continuation within the observer-relative coherent continuation space. It does not require the Library to generate a future. It is a continuation problem over an unchanged totality and therefore marks the boundary of the axiomatic primer and the entry point for subsequent NSFG work.

$$N_O(h,x) \to \Gamma_O(h,x)$$

**Formal Statement — Step 20 — Cross-Domain Applicability.** STRUCTURAL CONSEQUENCE. The foundation defined by this primer is domain-neutral. The same structural relations—distinguishability, coherence, accessibility, survivorship, continuation, and navigation—apply to physics, AI, finance, and any other domain that can be represented as observer-relative traversal through a static Library. Domains differ in the interpretation of observer-relative resolution $I_N(O)$, the distinguishability evaluation $\delta_O$, and the resulting coherence relation, not in the foundational ontology. No domain-specific axioms are required merely to apply the formal architecture to a new area. Domain-specific assumptions may be introduced downstream, but they must remain downstream and must not be retroactively inserted into the axiomatic floor.

$$\mathrm{Foundation}_{\mathrm{domain\hbox{-}neutral}} \supseteq \{\mathrm{physics},\mathrm{AI},\mathrm{finance},\ldots\}$$

For example, in a physical domain, $I_N(O)$ may be interpreted as a resolution scale related to measurement precision, and $\mu_O$ may map XOR distinctions to effective physical distinguishability. In an AI domain, $I_N(O)$ may represent the effective resolution of a symbolic reasoning system, and $\mu_O$ may map symbolic differences to a distinctness measure. In a financial domain, $I_N(O)$ may represent a minimum actionable price movement or information threshold, and $\mu_O$ may map market-state distinctions to actionable distinguishability. The structural relations remain unchanged; only the interpretation of $I_N(O)$ and $\mu_O$ varies.

The dependency architecture can therefore be compressed as follows: XOR supplies distinction; $D$ supplies the formal operand domain; $G$ supplies generating configurations; XOR closure characterizes the static Library; self-containment and maximality eliminate a privileged describable exterior; reference neutrality eliminates a privileged worldline; whole-Library relationality establishes the observer's position within the totality; admissible reference establishes the current relational state; observerhood supplies a structurally persistent evaluator; $I_N(O)$ supplies observer-relative resolution; XOR-induced distinction evaluated through $\mu_O$ supplies $\delta_O$; history supplies traversal ordering; coherence evaluates survivorship; accessibility identifies the observer-relative accessible subset; $\Omega(x)$ represents continuation through the unchanged Library; $\Gamma_O(h,x)$ restricts that continuation by observer-relative coherence; navigation selects or traverses within that space; emergent regularity describes recurring survivorship; and cross-domain applicability permits downstream interpretations without altering the foundational ontology.

The compact dependency chain is: 

$$\oplus \to D \to G \to \mathrm{Closure}_D(\oplus,G) = \mathcal{M}_{\mathrm{static,max}} \to \mathrm{no\ privileged\ exterior} \to \mathrm{no\ privileged\ worldline/reference} \to \mathrm{whole\hbox{-}Library\ relationality} \to x \in \mathcal{M}_{\mathrm{admissible}} \to O \to I_N(O) \to (x \oplus y) \to \mu_O \to \delta_O \to h \to \mathcal{C}(\gamma \mid O,h,x) \to A_O(h,x) \to \Omega(x) \to \Gamma_O(h,x) \ne \varnothing \to \mathrm{observer\hbox{-}relative\ traversal} \to \mathrm{emergent\ temporal/complexity\ structure} \to L_O \to N_O(h,x) \to \Gamma_O(h,x) \to \mathrm{cross\hbox{-}domain\ applicability}$$

**What is axiomatic**

- XOR as the sole primitive operation of distinction.

**What is defined or formally constructed**

- The formal configuration domain $D$.
- The generating configuration set $G$.
- The Library as the XOR closure of $G$ within $D$.
- Static maximal completeness and self-containment as defining properties of the Library.
- Admissible observer-relative reference configurations.
- Observerhood as a structural notion based on persistent resolvable distinction.
- Observer-relative resolution through $I_N(O)$.
- Observer-relative distinguishability through the XOR-induced distinction evaluation $\delta_O(x,y) := \mu_O(x \oplus y)$.
- Observer-relative coherence through $\mathcal{C}(\gamma \mid O,h,x)$.
- Observer-accessible reality through $A_O(h,x)$.
- The continuation space $\Omega(x)$ over unchanged $\mathcal{M}$.
- The observer-relative coherent continuation space $\Gamma_O(h,x)$.
- Navigation as traversal or selection within $\Gamma_O(h,x)$.

**Logical invariants**

- The Library is a single static totality: $\forall i,\; \mathcal{M}_i = \mathcal{M}$.
- No worldline, observer, or reference configuration is privileged as the universal origin of the Library.
- The observer is relationally situated with respect to the whole Library.
- Traversal does not modify Library membership.
- Observer accessibility does not define ontology.
- Inaccessibility does not constitute erasure.
- Past and future are not primitive partitions of the Library.
- The same foundational architecture is domain-neutral.
- Ontological completeness does not imply epistemic completeness for any particular observer.

**Derived requirements**

- Every admissible observer-relative reference configuration must admit at least one coherent continuation: $\forall x \in \mathcal{M}_{\mathrm{admissible}},\; \Gamma_O(h,x) \ne \varnothing$.
- Coherence must remain relocatable across arbitrary admissible reference configurations; no configuration is excluded solely by possessing a particular coordinate within the Library.

**Derived or downstream consequences**

- Observer-relative traversal ordering.
- Apparent temporal direction.
- Observer-experienced complexity growth.
- Observer-relative locality.
- Past/future distinction as traversal ordering.
- Law-like regularity from stable recurring survivorship patterns.
- Coherent navigation as continuation through a restricted observer-relative path space.
- Cross-domain interpretations in physics, AI, finance, and other representable domains.
- Epistemic novelty through discovery of relations already represented within the static Library.

**What is not derived**

- A complete physical theory.
- Physical spacetime.
- Physical time as a primitive ontology.
- Causality.
- Matter.
- Energy.
- The Standard Model.
- General relativity.
- Cosmological expansion or any specific cosmological mechanism.
- The Planck scale as the numerical value of $I_N(O)$.
- Consciousness.
- Human perception as a privileged observational mechanism.
- AI cognition or artificial consciousness.
- Specific NSFG field equations.
- The Lightning Model.
- Any experimental confirmation of the Library or NSFG.
- Any claim that XOR alone is empirically sufficient to explain physical reality.
- The claim that XOR closure alone mathematically proves nonempty coherent continuation.
- Any domain-specific physical, AI, or financial law without additional downstream assumptions.

Three layers must remain formally separated. First is the Library $\mathcal{M}$, the static, eternally maximally complete totality characterized by XOR closure and self-containment. Second is the observer state $O(h_i)$, consisting of the observer configuration and history relevant to the current relational evaluation. Third is the observer-relative structure $\Gamma_O(h_i,x_i)$, $\mathcal{C}(\gamma \mid O,h_i,x_i)$, and $A_O(h_i,x_i)$, consisting of relational structures evaluated over the unchanged Library. These layers must not be collapsed. The Library does not become the observer's history, the observer's history does not become the Library, and the coherent continuation space does not become the totality itself.

The axiomatic floor ends before physical or domain-specific interpretation. It establishes a formal architecture from distinction to formal closure, from closure to static maximal totality, from maximality and self-containment to the absence of privileged exteriors and worldlines, from whole-Library relationality to arbitrary admissible reference, from XOR-induced distinction to observer-relative resolution and coherence, from coherence to accessibility and continuation, and from restricted continuation to navigation. The next step is therefore not to add another foundational primitive or to generate a new Library state, but to investigate what mathematical structure can be built on the coherent continuation space already defined.

The primer ends at navigation and explicitly establishes cross-domain applicability. Subsequent NSFG research may investigate the geometry, dynamics, topology, symbolic representation, or physical interpretation of coherent navigation, while domain-specific downstream work may apply the same foundation to AI, finance, or other domains. All such work must preserve the distinction between the static Library $\mathcal{M}$ and observer-relative traversal over $\mathcal{M}$. Downstream models may introduce additional assumptions, but those assumptions must remain downstream and must not be retroactively inserted into the axiomatic floor.

The dependency architecture established in this section fixes the logical status of each construction and closes the axiomatic floor at navigation. What remains is to build upon the coherent continuation space, preserving the separation between the static Library and the observer's changing relation to it.

---

# Appendix A — Mathematical Reference Sheet

**Canonical Definitions, Notation, and Dependency Vocabulary**

## A.1 Axiomatic Status

This appendix is normative for the mathematical notation and definitions of the primer. It specifies the formal domain, primitive XOR operation, generating configurations, XOR closure, observer structure, observer-relative resolution, observer-relative magnitude evaluation, distinguishability, persistence, coherence, accessible reality, continuation spaces, survivorship, navigation, and the resulting observer-relative graph structure. The symbols defined here are canonical for the primer. Interpretive prose may use descriptive language, but mathematical statements should use these definitions unless a later document explicitly extends or refines them. The appendix does not introduce new axioms, physical assumptions, or downstream NSFG mechanisms.

**Axiom count.** 1

**Sole axiom.**

$$A_N = \{A_{\oplus}\}$$

**Axiom.**

$$A_{\oplus}: \oplus\ \mathrm{is\ the\ primitive\ operation\ of\ distinction.}$$

*All other entries in this appendix are definitions, constructions, or consequences of the axiom together with ordinary mathematical inference.*

---

## A.2 Formal Domain

**Symbol.** $D$

**Definition.** A minimal formal domain containing the configurations required for the primitive operation $\oplus$ to have operands.

**Signature.**

$$\oplus : D \times D \to D$$

**Constraint.** $D$ is not physical space, spacetime, matter, energy, information, or any other physical ontology.

**Status.** DEFINITION

---

## A.3 Generators

**Symbol.** $G$

**Definition.** A specified subset of $D$ containing the configurations from which the XOR closure is generated.

**Constraint.** $G \subseteq D$

**Interpretation.** $G$ identifies the required generating configurations for the formal closure. It is not an additional primitive operation or physical axiom.

**Status.** DEFINITION

---

## A.4 XOR

**Symbol.** $\oplus$

**Signature.**

$$\oplus : D \times D \to D$$

**Primitive definition.**

$$a \oplus b = 1 \iff a \neq b$$

**Truth table.**

| $a$ | $b$ | $a \oplus b$ |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

**Properties.** commutative, associative, self-cancelling, identity element $0$

**Identities.**

$$a \oplus b = b \oplus a$$

$$(a \oplus b) \oplus c = a \oplus (b \oplus c)$$

$$a \oplus a = 0$$

$$a \oplus 0 = a$$

**Interpretation.** XOR is treated at the axiomatic floor as distinction. Equal configurations cancel; unequal configurations produce distinction.

**Status.** AXIOMATIC_PRIMITIVE

---

## A.5 Closure

**Symbol.** $\mathrm{Closure}_D(\oplus, G)$

**Definition.** The smallest subset $\mathcal{M}$ of $D$ containing $G$ and closed under $\oplus$.

**Library.**

$$\mathcal{M} := \mathrm{Closure}_D(\oplus, G)$$

**Closure condition.**

$$\forall x, y \in \mathcal{M},\quad x \oplus y \in \mathcal{M}$$

**Generator condition.**

$$G \subseteq \mathcal{M}$$

**Minimality condition.** If $S \subseteq D$ is closed under $\oplus$ and $G \subseteq S$, then $\mathcal{M} \subseteq S$.

**Status.** DEFINITION

*The Library is a set closed under an operation. XOR itself is not a closed set.*

**Interpretation.** The Library is generated by closure rather than introduced as an independent ontological primitive.

---

## A.6 Library

**Symbol.** $\mathcal{M}$

**Definition.** The maximally complete unbounded totality satisfying closure under XOR and self-containment with no definable privileged exterior. $\mathcal{M}$ is a dimensionally undifferentiated complete relational totality, not a grid, container, temporal sequence, or singularity.

**Formal characterization.**

**Closure property.**

$$\forall x, y \in \mathcal{M},\quad x \oplus y \in \mathcal{M}$$

**Self-containment.**

$$\neg \exists z \notin \mathcal{M}\ \mathrm{such\ that}\ z\ \mathrm{is\ definable\ within\ the\ system\ using\ only}\ \oplus\ \mathrm{and\ elements\ of}\ \mathcal{M}\ \mathrm{over}\ D\ \mathrm{as\ a\ privileged\ exterior}$$

**Equivalence.** $\mathcal{M}$ is closed under XOR, self-contained with respect to its formal resources, and contains no privileged definable exterior.

**Equation.** $\mathcal{M}$ is defined by property, not by construction: $\mathcal{M}$ is the maximally complete unbounded totality satisfying XOR closure together with self-containment and absence of a privileged definable exterior. $\mathrm{Closure}_D$ describes a property of $\mathcal{M}$, not a temporal or generative process.

**Membership condition.**

$$x \in \mathcal{M}$$

**Closure condition.**

$$\forall x, y \in \mathcal{M},\quad x \oplus y \in \mathcal{M}$$

**Self-containment condition.** No element outside $\mathcal{M}$ is definable within the system as a privileged exterior using the formal resources of the system.

**Whole-library invariant.** At every abstract traversal step, the observer is relationally situated with respect to the entire static Library $\mathcal{M}$. The observer does not encounter a temporal slice, local neighborhood, generated future, or pre-filtered coherent subset.

**Static totality condition.** $\mathcal{M}$ does not change as observer history changes. Changes in observer state, accessibility, distinguishability, or coherent continuation alter the observer's relation to $\mathcal{M}$, not $\mathcal{M}$ itself.

**Coherence–membership separation.** Membership in $\mathcal{M}$ is prior to and independent of observer-relative coherence. Coherence determines whether a traversal relation can be maintained by an observer; it does not determine Library membership.

**Unboundedness condition.** $\mathcal{M}$ has no privileged boundary, terminal region, or excluded coordinate whose status would determine where coherent traversal is permitted. If an arbitrary $x \in \mathcal{M}$ could function as a coherence boundary merely because of its location in $\mathcal{M}$, then the totality would possess an observer-independent bound or privileged reference condition inconsistent with its unbounded self-contained definition.

**No privileged origin condition.** No $x \in \mathcal{M}$ is privileged as an ontological origin, reference frame, or starting state. Any $x \in \mathcal{M}$ may serve as the relational origin from which observer-relative coherence is evaluated without becoming the origin or generator of $\mathcal{M}$.

**Arbitrary-origin coherence invariant.** For an observer $O$ situated at any arbitrary $x \in \mathcal{M}$, the coherent continuation relation must remain nonempty above the observer's operative coherence threshold. The guarantee is not supplied by $x$ being special, but by the combination of maximal completeness, unboundedness, whole-Library relation, and absence of a privileged exterior reference frame.

**Arbitrary-origin coherence formalization.**

$$\forall x \in \mathcal{M},\ \forall O\ \mathrm{with\ a\ defined\ resolution\ floor}\ I_N(O),\ \exists \gamma \in \mathrm{Path}(\mathcal{M})\ \mathrm{such\ that}\ \gamma\ \mathrm{begins\ at}\ x\ \mathrm{and}\ \mathcal{C}(\gamma \mid O) = 1,\ \mathrm{provided\ the\ observer's\ state\ admits\ continuation.}$$

*No* $x$ *is excluded from coherent traversal merely by its coordinate within* $\mathcal{M}$.

**Why arbitrary origin is required.** If some $x \in \mathcal{M}$ admitted no coherent continuation solely because of its location, then $x$ would function as a boundary of the unbounded totality or coherence would depend upon a privileged reference frame. Either result would introduce structure external to the relational totality. The absence of a privileged perspective therefore requires coherence to be relocatable: the same relational mechanism must apply from any arbitrary point.

**Whole-library relation.** The observer does not first receive a local subset of $\mathcal{M}$ and then navigate that subset. At every abstract step the observer is relationally situated with respect to the whole $\mathcal{M}$. The minimal coherent continuation set emerges only from the relation between that whole totality and the observer's current state, history, and resolution capacity.

**Coherent continuation note.** For any $x \in \mathcal{M}$, XOR closure ensures that relational operations remain within the Library rather than terminating at an external configuration. The stronger requirement of a nonempty coherent continuation follows from whole-Library traversal together with unboundedness and absence of a privileged reference frame. $I_N(O)$ filters distinguishability and coherence; it does not create, delete, or bound $\mathcal{M}$.

**Continuation, not generation.** A coherent continuation is not a configuration generated into existence after $x$. It is an observer-relative traversal relation among configurations already contained in the static totality $\mathcal{M}$.

**Structure type.** complete_graph_relational

**Dimensionality.** none_intrinsic

**Closure interpretation.** property_not_process

### A.6.1 Termination Singleton

**Symbol.** $\mathcal{Z}$

**Definition.** Unique singleton where XOR completes and recursive bounce degenerates.

**Formal.**

$$\mathcal{Z} := \{z \in D \mid z \oplus z = z\} = \{0\}$$

**Properties.**

- $\forall x \in \mathcal{M},\ x \oplus x \in \mathcal{Z}$
- $\forall x \in \mathcal{M},\ 0 \oplus x = x$
- $(x \oplus y) \oplus y = x$ degenerates when $y = 0$
- Single equivalence class under $x \sim y \iff x \oplus y = 0$
- Where distinction completes, no new relation is generated

**Relation to library.** $\mathcal{Z} \subset \mathcal{M}$, interior termination, not exterior. Complementary as termination versus non-degenerate distinction: $\mathcal{M} \setminus \mathcal{Z}$ represents configurations participating in non-degenerate relational distinction, while $\mathcal{Z}$ represents completed distinction.

**Generating set note.** $G$ is not a primitive that builds $\mathcal{M}$. Any $G \subseteq \mathcal{M}$ may serve as an addressable generating description of portions of the closure, but $G$ is not an ontological origin of $\mathcal{M}$. Generation language here describes algebraic addressability, not temporal construction.

**Unfiltered at floor.** true

**Membership does not imply.** persistence, coherence, physicality, observability, accessibility, consciousness, causal participation

**Non-erasure rule.** $x \notin A_O$ does not imply $x \notin \mathcal{M}$. Failure of observer-relative accessibility, coherence, or distinguishability does not erase a configuration from the totality. Reaching $\mathcal{Z}$ is collapse of distinguishability, not erasure.

**Observer relocation invariant.** Relocating the observer's relational origin from $x$ to any arbitrary $y \in \mathcal{M}$ does not change the underlying Library or invoke a new external reference frame. Only the observer-relative coherence relation changes.

**Reference-frame independence.** There is no privileged coordinate, state, history, or world line from which coherence is intrinsically defined. Coherence is determined relative to the current observer configuration and history, wherever that observer is situated within $\mathcal{M}$.

**Noise without internal relation.** Viewed from a hypothetical perspective external to $\mathcal{M}$, the totality need not exhibit the observer-relative structure that appears internally. Such a perspective supplies no useful privileged ordering because the Library's structure is relationally self-contained. The observer-relative coherent world line is therefore not imposed by an external ordering; it emerges from the relation of an observer to the totality itself.

**Future generation mechanism.** false

**Physical container.** false

**Status.** DERIVED_DEFINITION

---

## A.7 No Privileged Exterior

**Candidate.** $\Omega$

**Formal condition.**

$$\Omega \notin \mathcal{M}\ \mathrm{may\ be\ proposed\ as\ an\ external\ candidate.}$$

**Closure consequence.** If $\Omega$ is internally describable using the same formal machinery, then $\Omega \in D$; if $\Omega$ is XOR-generable from $D$, then $\Omega \in \mathcal{M}$ by closure property: $\mathcal{M}$ is the unique totality with $\forall x, y \in \mathcal{M},\ x \oplus y \in \mathcal{M}$ and no definable exterior. May be described as $\mathrm{Closure}_D$ only as property, not process.

**Termination singleton is not exterior.**

$$\mathcal{Z} := \{z \mid z \oplus z = z\} = \{0\} \subset \mathcal{M}$$

*satisfies* $\forall x,\ x \oplus x \in \mathcal{Z}$ *and* $0 \oplus x = x$. $\mathcal{Z}$ *is where distinction completes and recursive bounce* $(x \oplus y) \oplus y = x$ *degenerates.* $\mathcal{Z}$ *is a single equivalence class under* $x \sim y \iff x \oplus y = 0$ *and is complementary as termination versus generation, not as exterior.*

**Conclusion.** A describable privileged exterior cannot remain external to $\mathcal{M}$. Any candidate definable using $\oplus$ and elements of $\mathcal{M}$ over $D$ is already in $\mathcal{M}$, including $\mathcal{Z}$.

**Scope constraint.** This is a formal boundary condition on describable exteriors concerning absence of privileged internal coherence relation supplied by external God's-eye reference; it does not assert that literal physical exteriority is independently impossible, only that no such reference is definable within the system.

**Status.** CONSEQUENCE

---

## A.8 Observer

**Symbol.** $O$

**Domain.** $\mathrm{Obs} \subseteq \mathcal{M}$

**Definition.** A configuration in $\mathcal{M}$ capable of maintaining a persistent chain of distinctions above its observer-specific resolution floor.

**Structural definition.** $O$ is an observer iff $O$ can maintain a persistent chain of distinctions that remain resolvable relative to $O$.

**Consciousness requirement.** false

**Agency requirement.** false

**Human requirement.** false

**Privileged observer.** false

**Status.** DEFINITION

*Observerhood is structural and does not imply consciousness, perception, intention, or agency.*

---

## A.9 Resolution

**Symbol.** $I_N(O)$

**Function.**

$$I_N : \mathrm{Obs} \to \mathbb{R}_{>0}$$

**Definition.** The minimum effective distinction magnitude observer $O$ can maintain as a stable distinction.

**Observer-relative.** true

**Universal constant.** false

**Universal numerical value.** false

**Planck identification.** false

**Status.** DEFINITION

*No universal value of* $I_N$ *is supplied by the axiomatic floor.*

---

## A.10 Distinguishability

### A.10.1 Magnitude Evaluation

**Symbol.** $\mu_O$

**Definition.** The observer-relative magnitude evaluation function that maps a primitive XOR distinction to an effective magnitude resolvable by observer $O$. $\mu_O$ is monotonic with respect to XOR-derived distinction: if $x \oplus y = 1$ and $u \oplus v = 0$, then $\mu_O(x \oplus y) \geq \mu_O(u \oplus v)$. The specific functional form of $\mu_O$ is not specified at the foundational level and may vary by domain or observer structure.

**Equation.**

$$\mu_O : D \to \mathbb{R}_{\geq 0}$$

**Constraint.** $\mu_O$ is observer-relative and domain-neutral at the foundational level. Its specific form is a downstream construction or domain-specific interpretation.

**Status.** DEFINITION

### A.10.2 Distinguishability Magnitude

**Symbol.** $\delta_O(x, y)$

**Codomain.** $\mathbb{R}_{\geq 0}$

**Definition.** The observer-relative effective magnitude of the distinction between configurations $x$ and $y$, obtained by applying the observer-relative magnitude evaluation $\mu_O$ to the primitive XOR distinction $x \oplus y$.

**Equation.**

$$\delta_O(x, y) := \mu_O(x \oplus y)$$

**Indistinguishability.**

$$x \approx_O y \iff \delta_O(x, y) < I_N(O)$$

**Distinguishability.**

$$x \nsim_O y \iff \delta_O(x, y) \geq I_N(O)$$

**Non-identity rule.** $x \approx_O y$ does not imply $x = y$.

**Non-erasure rule.** $x \approx_O y$ does not imply $x \notin \mathcal{M}$.

**Observer dependence.** The same pair of configurations may be distinguishable relative to one observer and indistinguishable relative to another.

**Derivation note.** $\delta_O$ is not an additional primitive. It is derived from the sole primitive distinction operation $\oplus$ through the observer-relative magnitude evaluation $\mu_O$.

**Domain-neutrality note.** The formal structure of $\delta_O$ is domain-neutral. Domain-specific interpretation enters through the observer-relative evaluation $\mu_O$ and resolution floor $I_N(O)$, not through a new foundational distinction operation.

**Status.** DEFINITION / DERIVED FROM PRIMITIVE

---

## A.11 Persistence

**Symbol.** $P_O(\gamma, n)$

**Abstract sequence.**

$$\gamma = (x_0, x_1, \ldots, x_n)$$

**Step condition.**

$$\delta_O(x_i, x_{i+1}) \geq I_N(O)$$

**Finite persistence.**

$$P_O(\gamma, n) = 1 \iff \forall i < n,\ \delta_O(x_i, x_{i+1}) \geq I_N(O)$$

**Ordering index.** $i$

**Time warning.** The index $i$ represents abstract ordering and is not yet physical time.

**Interpretation.** Persistence is the maintenance of observer-resolvable distinctions across an ordered chain.

**Status.** DEFINITION

---

## A.12 Heaviside Threshold

**Symbol.** $\Theta$

**Definition.** A binary threshold function.

**Equation.**

$$\Theta(z) = 1\ \mathrm{if}\ z \geq 0,\ \mathrm{otherwise}\ 0.$$

**Domain.** $\mathbb{R}$

**Codomain.** $\{0, 1\}$

**Status.** DEFINITION

---

## A.13 Coherence

**Step symbol.** 

$$\mathcal{C}_O(x_i, x_{i+1})$$

**Step coherence.**

$$\mathcal{C}_O(x_i, x_{i+1}) = \Theta(\delta_O(x_i, x_{i+1}) - I_N(O))$$

**Path symbol.** $\mathcal{C}(\gamma \mid O)$

**Path coherence.**

$$\mathcal{C}(\gamma \mid O) = \prod_{i=0}^{n-1} \mathcal{C}_O(x_i, x_{i+1})$$

**Coherence derivation note.** Coherence is derived from $\delta_O$ and $I_N(O)$, with $\delta_O$ itself derived from $\mu_O$ and the primitive XOR distinction. No universal coherence constant is introduced.

**Domain-neutrality note.** The coherence condition is domain-neutral. In physical contexts, it may be interpreted as the condition for a worldline to satisfy the equations of motion; in AI contexts, as the condition for a reasoning path to be symbolically consistent; in financial contexts, as the condition for a trading strategy to be coherent across market states. The mathematical structure is the same in all domains.

**Binary condition.** $\mathcal{C}(\gamma \mid O) = 1$ iff every transition in $\gamma$ remains resolvable by $O$.

**Interpretation.** Coherence is the relation between a path and an observer.

**Observer dependent.** true

**Absolute path property.** false

**Threshold source.** $I_N(O)$

**Independent noise threshold.** false

**Noise threshold note.** No separate $\gamma_{\mathrm{noise}}$ threshold is introduced. The foundational coherence condition is governed by $I_N(O)$ through $\delta_O$.

**Status.** DEFINITION / DERIVED CONDITION

*Prefer* $\mathcal{C}(\gamma \mid O)$ *over* $\mathcal{C}(\gamma)$ *whenever observer dependence matters.*

---

## A.14 Accessible Reality

**Symbol.** $A_O$

**Accessible states.**

$$A_O = \{x \in \mathcal{M} \mid \exists \gamma\ \mathrm{containing}\ x\ \mathrm{such\ that}\ \mathcal{C}(\gamma \mid O) = 1\}$$

**Experienced reality.**

$$R_O := A_O$$

**Subset relation.**

$$A_O \subseteq \mathcal{M}$$

**Interpretation.** $A_O$ is the subset of the Library accessible through observer-relative coherent traversal.

**Non-erasure.** $x \notin A_O$ does not imply $x \notin \mathcal{M}$.

**Observer creation rule.** $A_O$ is not ontologically created by $O$; it is an observer-relative accessibility subset of $\mathcal{M}$.

**Domain-neutrality note.** The construction of $A_O$ is domain-neutral. The domain-specific character of accessibility is determined by the observer-relative resolution $I_N(O)$, magnitude evaluation $\mu_O$, and resulting coherence relation.

**Status.** DEFINITION / CONSTRUCTION

---

## A.15 Continuation

**Symbol.** $\Omega(x)$

**Continuation space.**

$$\Omega(x) = \{\gamma \mid \gamma\ \mathrm{begins\ at}\ x\ \mathrm{and}\ \gamma\ \mathrm{is\ a\ path\ contained\ in}\ \mathcal{M}\}$$

**Surviving symbol.** $\Omega_O^{\mathrm{survive}}(x)$

**Surviving continuations.**

$$\Omega_O^{\mathrm{survive}}(x) = \{\gamma \in \Omega(x) \mid \mathcal{C}(\gamma \mid O) = 1\}$$

**Survival subset.**

$$\Omega_O^{\mathrm{survive}}(x) \subseteq \Omega(x)$$

**Coherence condition note.** Coherence is defined in terms of $I_N(O)$ through $\delta_O$. No separate $\gamma_{\mathrm{noise}}$ threshold is introduced at the foundational level.

**Interpretation.** Survivorship restricts observer-accessible continuation without deleting non-surviving paths from the represented continuation space.

**Future generation rule.** The Library does not generate future events. Continuation describes represented paths and their observer-relative survivorship.

**Domain-neutrality note.** The continuation construction is domain-neutral. Physical, AI, financial, or other domain interpretations differ in the observer-relative structure used to evaluate coherence, not in the underlying continuation space $\Omega(x)$.

**Status.** DEFINITION / CONSTRUCTION

---

## A.16 Survivorship

**Definition.** Observer-relative filtering of continuation paths according to the coherence condition $\mathcal{C}(\gamma \mid O) = 1$.

**Formal relation.**

$$\Omega_O^{\mathrm{survive}}(x) \subseteq \Omega(x)$$

**Interpretation.** A path survives relative to $O$ when its transitions remain above $O$'s resolution threshold.

**Threshold source.** $I_N(O)$

**Deletion rule.** Survivorship does not delete the alternatives contained in $\Omega(x)$.

**Domain-neutrality note.** Survivorship is a domain-neutral filtering construction. Its domain-specific interpretation arises from $\mu_O$, $I_N(O)$, and the resulting observer-relative coherence relation.

**Status.** CONSTRUCTION

---

## A.17 Emergent Regularity

**Symbol.** $L_O(x, y)$

**Definition.** A derived relation representing a stable recurring transition across an appropriate family of $O$-accessible paths.

**Formal condition.**

$$L_O(x, y) = 1 \iff x \to y\ \mathrm{is\ a\ stable\ recurring\ transition\ across\ an\ appropriate\ family\ of}\ O\text{-}\mathrm{accessible\ paths.}$$

**Probabilistic form.**

$$P_O(y \mid x) \approx \mathrm{constant\ over\ a\ defined\ observer}\text{-}\mathrm{accessible\ ensemble.}$$

**Domain-neutrality note.** $L_O$ is domain-neutral as a structural relation. Its interpretation as a physical law, reasoning regularity, financial regularity, or other domain-specific regularity is downstream of the observer-relative accessibility structure.

**Status.** CONSEQUENCE / DERIVED DESCRIPTION

$L_O$ *is not an element of the axiomatic set* $A_N$.

**Physical law status.** No particular physical law is derived by this definition.

---

## A.18 Navigation

**History.**

$$h_n = (x_0, \ldots, x_n)$$

**Coherent continuation set.**

$$\Gamma_O(h_n) = \{\gamma \mid \gamma\ \mathrm{begins\ with}\ h_n\ \mathrm{and}\ \mathcal{C}(\gamma \mid O) = 1\}$$

**Navigation operator.**

$$N_O(h_n) \to \Gamma_O(h_n)$$

**Interpretation.** Navigation is traversal or selection of a continuation within the observer-relative coherent continuation space.

**Future generation.** false

**Causality primitive.** false

**Domain-neutrality note.** Navigation is domain-neutral as a continuation problem. The same formal operator may describe traversal in physical, AI, financial, or other domains once the relevant observer-relative coherence structure has been specified.

**Status.** DEFINITION / DOWNSTREAM CONSTRUCTION

---

## A.19 Geometry

**Accessible graph.**

$$G_O = (A_O, E_O)$$

**Edge relation.**

$$(x, y) \in E_O \iff x \to y\ \mathrm{is}\ O\text{-}\mathrm{coherent}$$

**Local accessible neighborhood.**

$$U_O(x) = \{y \in \mathcal{M} \mid y\ \mathrm{is\ reachable\ from}\ x\ \mathrm{by\ an}\ O\text{-}\mathrm{coherent\ path\ segment}\}$$

**Interpretation.** $G_O$ represents observer-relative relational accessibility among configurations.

**Physical spacetime identification.** false

**Domain-neutrality note.** $G_O$ is a relational graph induced by observer-relative coherence. It may later support domain-specific geometric interpretations, but no physical spacetime identification is assumed at the foundational stage.

**Status.** DOWNSTREAM CONSTRUCTION

*Do not identify* $G_O$ *with physical spacetime at the foundational stage.*

---

## A.20 Dependency Reference

**Chain.**

$$\oplus \to D \to G \to \mathrm{Closure}_D(\oplus, G) = \mathcal{M} \to \mathrm{no\ describable\ privileged\ exterior} \to \mathrm{no\ universal\ resolver} \to \mathrm{persistent\ distinction} \to O \to I_N(O) \to \mu_O \to \delta_O := \mu_O(x \oplus y) \to \mathcal{C}(\gamma \mid O) \to A_O = R_O \to \mathrm{survivorship} \to \mathrm{emergent\ regularity} \to \Gamma_O(h_n) \to N_O(h_n)$$

**Domain-neutrality note.** This dependency chain is domain-neutral. The same chain applies to physical, AI, financial, and any other domain that can be represented as observer-relative traversal through a static Library. Domains differ only in the interpretation of $\mu_O$ and $I_N(O)$, together with the domain-specific meaning assigned to the resulting observer-relative structures.

**Dependency rule.** A later construction must not be treated as a primitive premise of an earlier construction.

**Ordering principle.** Distinction precedes objects; closure precedes accessibility; persistence precedes observerhood; observer-relative resolution and magnitude evaluation precede distinguishability; distinguishability precedes coherence; coherence precedes accessibility; accessibility precedes survivorship-based regularity; restricted continuation precedes navigation.

**Noise threshold rule.** No independent $\gamma_{\mathrm{noise}}$ threshold is required at the foundational level. If a later domain-specific construction introduces an additional margin, that margin must be explicitly defined as a downstream refinement rather than silently incorporated into the axiomatic dependency chain.

---

## A.21 Logical Invariants

- XOR is the only primitive.
- $D$ is the minimal formal domain required for XOR to operate.
- $G$ specifies the generating configurations and is not an additional primitive.
- The Library is a definition, not an axiom.
- A set can be closed under an operation; the operation itself should not be called closed.
- The Library is the XOR closure of $G$ within $D$.
- The Library is unfiltered at the axiomatic level.
- Existence in the Library is not the same as accessibility to an observer.
- Inaccessibility is not erasure.
- There is no describable privileged exterior that can remain outside the closure.
- There is no observer-independent resolution rule at the axiomatic floor.
- $I_N$ is observer-relative.
- There is no universal $I_N$ unless an additional axiom is introduced.
- $\mu_O$ is observer-relative and its specific functional form is not fixed by the axiomatic floor.
- $\delta_O$ is derived from the primitive XOR distinction through $\mu_O$.
- Observerhood is structural and is not synonymous with consciousness.
- Coherence is relational: $\mathcal{C}(\gamma \mid O)$.
- Coherence is derived from observer-relative distinguishability and resolution.
- Coherence is not an absolute property of a path alone.
- The abstract sequence index is not automatically physical time.
- The Library does not generate the future.
- No independent $\gamma_{\mathrm{noise}}$ threshold is introduced at the foundational level.
- Survivorship filters accessibility rather than deleting alternatives.
- Emergent lawfulness is not an additional axiom.
- Navigation is the continuation problem created by observer-relative survivability.
- $G_O$ is a relational graph at the foundational stage and is not physical spacetime.
- The formal dependency chain is domain-neutral.
- Domain-specific interpretation enters through observer-relative resolution, magnitude evaluation, and downstream interpretation rather than through additional foundational axioms.

---

## A.22 Claims Not To Make

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
- Do not use "closure of XOR" without specifying the domain $D$ and generating set $G$.
- Do not introduce $\gamma_{\mathrm{noise}}$ as an independent foundational threshold.
- Do not let poetic language replace formal definitions.
- Do not introduce downstream NSFG machinery before the axiomatic dependency chain requires it.
- Do not use the Lightning Model as a premise of this primer.

---

## A.23 Mathematical Level

**Required domains.**

- elementary Boolean algebra
- set theory
- closure operators
- relations
- sequences
- threshold functions
- products
- subsets
- graph theory
- logical inference

**Calculus required.** false

**Advanced physics required.** false

**External physical axioms required.** false

**External axioms required.** false

---

## A.24 Interpretive Boundary

The definitions in this appendix specify the mathematical structures used by the primer. Physical interpretations may be developed in later NSFG documents but are not assumed here. The formal structures are domain-neutral: physics, AI, finance, and other domains differ in their observer-relative interpretation of $\mu_O$, $I_N(O)$, coherence, accessibility, and downstream regularities; they do not require separate foundational ontologies. In particular, $\mathcal{M}$ is not to be identified with physical space or spacetime; $I_N(O)$ is not to be identified with a universal physical constant; $\mu_O$ is not to be identified with a universal metric; $O$ is not to be identified with consciousness; $G_O$ is not to be identified with physical spacetime; the abstract sequence index $i$ is not to be identified with physical time; survivorship is not to be identified with ontological deletion; accessibility is not to be identified with ontological creation; and coherence is not to be identified with an observer-independent path property.

---

## A.25 Normative Statement

Appendix A is normative for the mathematical notation and definitions of the primer. The main text supplies the conceptual argument and dependency structure; this appendix supplies the canonical formal reference. Neither the appendix nor the primer should be read as deriving physical law beyond the constructions explicitly stated here.