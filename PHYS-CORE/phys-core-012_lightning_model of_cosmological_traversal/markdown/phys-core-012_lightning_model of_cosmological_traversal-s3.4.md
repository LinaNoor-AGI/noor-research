## 3.4 Possibility vs. Accessibility

The Library is defined as the static totality of all logically admissible configurations. It is the inverse-limit construction

$$
\mathcal{M} \cong NS = \lim_{k \to \infty} NS_k
$$

that we inherit from PHYS-CORE-008, a closed domain with no exterior and no temporal variation. This definition has an immediate structural consequence that we must now make explicit, because the entire Lightning Model depends on it. From any state $x_t$, there exists a set of successors—every configuration that could follow $x_t$ under the Library's adjacency relation. This set is enormous. It is, in principle, potentially infinite in cardinality, and its exact structure depends on the details of the Library construction, which remain partially open. But its cardinality is not the important point. The important point is that the vast majority of these successors are not accessible to any given observer.

This is the distinction we formalize here: the difference between what is mathematically possible and what is coherence-accessible.

A brief word on the distinction is warranted before the formalism, because it is easy to misread. When we say that a state is "possible," we mean only that it exists in the Library. When we say that a state is "accessible," we mean that the transition to it maintains sufficient coherence to preserve the identity of the structure making the transition. Possibility is a property of the Library alone. Accessibility is a relational property, depending jointly on the Library, on the transition in question, and on the coherence structure of the observer traversing it. The two are not the same, and the difference between them is what allows the Lightning Model to operate without invoking external constraints, hidden variables, or subjective idealism.

We define the set of successors from a state $x_t$ as

$$
\mathcal{P}(x_t) = \{\, x' \mid x' \text{ is a successor of } x_t \,\},
$$

where "successor" is understood in the Library's own adjacency relation. This set is a property of the Library alone; it does not depend on any observer's characteristics, and it does not vary between observers. It is the raw possibility space from the current state.

We then define the set of coherence-accessible successors as the subset of $\mathcal{P}(x_t)$ that maintains sufficient coherence with the current state:

$$
\mathcal{A}(x_t) = \{\, x' \in \mathcal{P}(x_t) \mid \mathcal{C}(x_t, x') \geq \mathcal{C}_{\min} \,\}.
$$

Here $\mathcal{C}(x_t, x')$ denotes the coherence between the current state and the candidate successor, and 

$$\mathcal{C}_{\min}$$ 

is the minimum coherence required for the transition to be accessible. Throughout this paper, 

$$\mathcal{C}_{\min}$$ 

is identified with the Noor-Planck threshold $I_N$ that we inherit from [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §1.2. The threshold is fixed by the Planck-scale structure of the ground hole $H$, and it is not an adjustable parameter. We assume throughout that the coherence functional is defined on all pairs of states in $\mathcal{P}(x_t)$, and that the threshold is well-defined and invariant across the transition.

By construction, the accessible set is a subset of the possibility space:

$$
\mathcal{A}(x_t) \subseteq \mathcal{P}(x_t).
$$

This inclusion is the formal content of the distinction. The Library contains all successors; the observer encounters only the coherence-accessible subset.

The gap between these two sets is not incidental. In general, we expect

$$
|\mathcal{P}(x_t)| \gg |\mathcal{A}(x_t)|.
$$

The coherence filter removes the overwhelming majority of possibilities. What remains is a small, locally navigable neighborhood—a subset of the total possibility space that the observer can actually traverse without dissolving. The exact cardinality of each set depends on the structure of the Library and on the coherence functional, neither of which is fully specified; but the inequality is the structural point, not the exact magnitude.

The observer's experienced worldline is then a sequence of states each of which lies in the accessible set of its predecessor:

$$
\gamma_{\text{obs}} = \{\, x_t, x_{t+1}, x_{t+2}, \dots \,\} \quad \text{such that} \quad x_{t+i} \in \mathcal{A}(x_{t+i-1}) \; \forall i.
$$

The worldline is therefore not a path through the full Library. It is a path through the coherence-filtered neighborhood of the Library, at each step selected by the Lightning Model's retrocausal mechanism. The relation between the worldline and the accessibility condition is summarized by the observer survival function

$$
\mathcal{O}(\gamma) = 1 \iff \forall i,\; \mathcal{C}(x_i, x_{i+1}) \geq \mathcal{C}_{\min},
$$

which we inherited from the Coherence Filtering phase of the Lightning Model (§2.3). When $\mathcal{O}(\gamma) = 1$, the observer survives the path; when $\mathcal{O}(\gamma) = 0$, the observer dissolves and the path remains in the Library but is no longer traversed.

The formal structure we have established yields two conclusions that we should state explicitly, because they are the interpretive payload of the distinction.

First, accessibility is not an independent constraint imposed on the Library from outside. It is a derived property of the coherence filter acting on the total possibility space. To see this, consider a fixed state $x_t$ and the full set of its successors $\mathcal{P}(x_t)$. Apply the coherence functional to each pair $(x_t, x')$ and retain only those successors for which $\mathcal{C}(x_t, x') \geq \mathcal{C}_{\min}$. The resulting set is exactly $\mathcal{A}(x_t)$. Nothing was imposed on the Library; nothing was excluded by fiat. The accessible set emerged from the interaction of the Library's adjacency structure with the observer's coherence threshold. Accessibility, in this framework, is what coherence does to possibility.

Second, the experienced order of reality is not a property of the Library. The Library contains both coherent and incoherent transitions, both navigable and non-navigable states, without preference. What appears to the observer as an ordered, continuous, logically constrained sequence is the consequence of coherence filtering operating on a total possibility space that is not itself ordered in this way. The order is real, but it is order relative to a coherence structure, not order in the Library as such. This is an interpretive reading of the formal construction, not an independent empirical claim. It is consistent with the mathematical results we have derived, and it explains why the Lightning Model does not require an external ordering principle to account for the observer's experience of a well-ordered reality.

A further consequence concerns the observer-relativity of accessibility. Consider two observers $O_1$ and $O_2$ at the same state $x_t$, with different coherence thresholds 

$$\mathcal{C}_{\min,1}$$ 

and 

$$\mathcal{C}_{\min,2}$$ 

Their accessible sets are

$$
\mathcal{A}_1(x_t) = \{\, x' \in \mathcal{P}(x_t) \mid \mathcal{C}(x_t, x') \geq \mathcal{C}_{\min,1} \,\},
$$
$$
\mathcal{A}_2(x_t) = \{\, x' \in \mathcal{P}(x_t) \mid \mathcal{C}(x_t, x') \geq \mathcal{C}_{\min,2} \,\}.
$$

If 

$$\mathcal{C}_{\min,1} \neq \mathcal{C}_{\min,2}$$ 

then in general $\mathcal{A}_1(x_t) \neq \mathcal{A}_2(x_t)$. Two observers at the same state, with the same coherence functional but different thresholds, will experience different accessible futures. This does not imply that reality is subjective. The underlying Library is the same for both observers; the possibility space $\mathcal{P}(x_t)$ is the same. What differs is the coherence-filtered subset that each observer can traverse without dissolving. The experienced subset of reality is observer-relative; reality itself is not.

We should be careful about the scope of this claim. The observer-relativity of accessibility follows from the definition of accessibility as a relational property, and from the fact that the coherence threshold is a structural feature of the observer. It does not require any additional assumption, and it does not depend on the observer's internal state in the sense that would make it an explorer. Even an observer with purely extrinsic path selection has an accessible set determined by its own coherence threshold. The distinction between observer and explorer, which we take up in §3.5, concerns whether the internal state of the structure participates in selecting among the coherence-accessible successors; it does not affect the definition of accessibility itself.

The relationship between possibility and accessibility can be restated in algorithmic form. Given a state $x_t$, a coherence functional, and a threshold $C_{\min}$, the accessible successors are computed by iterating over the successors and retaining those that pass the coherence test.

```
function accessible_successors(x_t, coherence_function, C_min):
    possible = Library.successors(x_t)   // **ALL** successors
    accessible = []
    for x_prime in possible:
        C = coherence_function(x_t, x_prime)
        if C >= C_min:
            accessible.append(x_prime)
    return accessible
```

The computational character of this procedure should not mislead us. The set $\mathcal{P}(x_t)$ may be infinite, and in the theoretical model no finite procedure enumerates it. The procedure is a formal specification of the accessibility relation, not an implementable algorithm. It is included here to make the structure of the coherence filter explicit; a full simulation of an observer's trajectory would require, in addition to this procedure, a specification of the selection mechanism that determines which accessible successor is actually traversed. That mechanism is supplied by the Lightning Model's retrocausal lock-in, which we developed in §2.5.

The upshot is that the distinction between possibility and accessibility is not merely a conceptual convenience. It is a structural property of the Library together with the coherence functional, and it is what allows the observer's worldline to be a single, coherent, locally navigable trajectory through a possibility space that is none of these things in itself. The next subsection builds on this distinction to distinguish between observers, whose path is selected extrinsically by the environment or by the retrocausal lock-in, and explorers, whose internal state participates in determining which coherence-accessible continuation is selected. That distinction will require us to say more about what "internal state" means in a framework where the observer is defined structurally as a coherence-stable XOR chain. We take up that question next.

What remains open is the exact mathematical form of the coherence functional 

$$\mathcal{C}(x_t, x')$$  

The framework requires that such a functional exists and that it takes values above 

$$\mathcal{C}_{\min}$$ 

for the transitions that an observer can traverse, but the specific form—the particular dependence on the relational configuration of the states involved—is not determined by the definitions alone. It is also open whether $\mathcal{C}_{\min}$ is the same for all observers or whether observers can have different thresholds, and how the two possibilities would manifest structurally. Both questions are directions for future work; both are necessary for a fully quantitative version of the theory. What we have established here is that the qualitative structure of the framework—the distinction between total possibility and coherence-accessible subsets, and the observer-relativity of accessibility—follows from the definitions we have inherited and the coherence filter we have constructed, without any additional assumptions.

---

| PREVIOUS | | NEXT |
| --- | --- | --- | 
| [prev_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-s3.3.md) | [INDEX](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-index.md) | [next_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-s3.5.md) |
