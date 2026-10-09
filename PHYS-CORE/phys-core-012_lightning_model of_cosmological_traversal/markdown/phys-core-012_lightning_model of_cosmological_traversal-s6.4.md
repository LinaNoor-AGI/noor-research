## 6.4 The Cost is O(1)

The preceding subsections established what the cost of observation is not. It is not a Landauer cost, because no information is erased. It is not a computation tax levied against a simulated Library, because the Library is not simulated. It is not vacuum energy, because the coherence field is not an ambient substrate in the sense of a cosmological constant. What remains, then, is to state positively what the cost is, and to show that its value is bounded, constant, and independent of every quantity one might naively expect it to depend on.

The cost of observation is the thermodynamic free energy required for the observer to instantiate its next state. When the retrocausal return stroke locks in a path, it selects exactly one state from the static Library and presents it to the observer as the successor of the present configuration. This act of instantiation is a phase transition in the observer's internal state. It is local, and it is paid for by the observer's available free energy gradient. The cost of this transition is what we have been calling \(c_{\text{lock}}\), and its defining relation is

$$
c_{\text{lock}} = \Delta F_{\text{instantiation}},
$$

where \(\Delta F_{\text{instantiation}}\) is the free energy required to maintain the observer's worldline above the Noor-Planck threshold, \(\mathbb{C}(\gamma) \geq I_N\), for the duration of one timestep. The quantity \(I_N\) is not a tunable parameter. It is fixed by the Planck-scale structure of the ground hole \(H\), as established in PHYS-CORE-009 §1.2, and is bounded below by

$$
I_N \;\approx\; \frac{E_P}{T_P \cdot k_B \ln 2}.
$$

Because \(I_N\) is fixed by the ground condition, and because the ground condition does not vary across the Library, the free energy required to maintain coherence above \(I_N\) is constant across every timestep of the observer's existence. This is the first sense in which the cost is \(O(1)\): it depends on a fundamental constant of the framework, not on the observer's history, not on the size of the Library, and not on the number of alternatives that exist as formal possibilities.

The second sense in which the cost is \(O(1)\) concerns what the observer is *not* paying for. In the Lightning Model, the Blind Exploration phase formally considers **ALL** continuations from the present state, but this consideration is not a physical process. The alternatives are not computed. They are not simulated. They are not instantiated in parallel and then collapsed. They are present in the static Library as formal possibilities, and the coherence filter selects among them without ever bringing the non-selected alternatives into physical reality for the observer. The observer pays only for the one state that survives the filter — for the single path segment that is retrocausally locked in. The alternatives remain in the Library, inaccessible but not erased.

This distinction is the difference between the Lightning Model and a naive computational account of cosmology. A computational model in which the universe evaluates all branches in parallel would have a cost that grows with the branching factor, and hence a cost that grows with the size of the configuration space. The Lightning Model has no such growth, because the evaluation of alternatives is not an operation performed by any physical system. It is a structural feature of the static Library. The Library contains all configurations; it does not compute them.

The realized cost at timestep \(t\) can therefore be written as

$$
E_{\text{realized}}(t) = c_{\text{lock}} \cdot \mathbb{I}\{\gamma_{\text{obs}} \text{ exists at } t\},
$$

where the indicator function is one whenever the observer's worldline exists at \(t\) and zero otherwise. The indicator function is not a source of variability in the cost, because it depends only on whether the observer persists — and persistence is guaranteed by the coherence condition \(\mathbb{C}(\gamma(t)) \geq I_N\) that defines the observer in the first place. What remains is \(c_{\text{lock}}\) alone, and \(c_{\text{lock}}\) is constant. Hence

$$
E_{\text{realized}}(t) = \mathcal{O}(1).
$$

The bound is per observer and per timestep. Across a worldline of \(N\) timesteps, the total cost is \(N \cdot c_{\text{lock}}\), which is linear in the observer's proper time but constant in every other respect. The universe does not become more expensive as it ages, because the cost of instantiating the next state does not depend on how many states have already been instantiated. The state carries its own history relationally, in the sense that the current configuration encodes the distinctions that have already been resolved along the worldline, and no separate ledger of past states needs to be consulted in order to determine the next one.

This relational encoding is the formal content of the locality condition

$$
T_{n+1} = f(T_n, T_{n-1}),
$$

which states that the next state of the system is a function of the current state and its immediate predecessor, and of nothing else. The operation is local and constant-time. No global sum over the history of the universe is required. No recalculation of past states is performed. The state contains its own history, in the sense that \(\operatorname{History}(T_n) \subset T_n\), and the cost of evolving the state forward is therefore bounded by a constant \(\tau_{\text{tick}}\) that does not depend on \(n\). This is the third sense in which the cost is \(O(1)\): it is a property of the local, relational structure of the evolution, not an additional assumption imposed on top of the model.

It is worth being explicit about the epistemic status of this result. The \(O(1)\) bound is a derived consequence of three premises: the staticity of the Library, the locality of the retrocausal lock-in, and the fact that the Noor-Planck threshold is fixed by the Planck-scale ground condition rather than tuned to the observer. It is not an independent postulate, and it does not require any additional physical mechanism beyond those already present in the Lightning Model. Given the framework, the bound follows.

The result also has a thermodynamic reading that is worth stating, provided the reading is not mistaken for a derivation. The instantiation of the next state is the thermodynamic equivalent of a phase transition: the observer's internal configuration changes, entropy is produced and exported, and free energy is consumed. The analogy is useful because it connects the abstract language of the Lightning Model to the concrete language of non-equilibrium thermodynamics, but the analogy is not a proof. The exact thermodynamic interpretation of \(c_{\text{lock}}\), and its precise relationship to quantities such as entropy production, heat dissipation, and information-theoretic cost, remains a matter for future formalization. What the present subsection establishes is the bound, not the microscopic mechanism that realizes it.

Several questions remain open. The exact quantitative relationship between \(c_{\text{lock}}\) and \(I_N\) has not been derived from first principles; the identification \(c_{\text{lock}} = \Delta F_{\text{instantiation}}\) defines the cost in terms of a free energy that must itself be specified by a microscopic model. The thermodynamic interpretation of the cost as a phase transition is conceptual. The question of whether the \(O(1)\) bound holds for all classes of observers — including the global coherence operators discussed in PHYS-CORE-009 §4 — has not been settled. And the interaction between observers, if such interaction has a thermodynamic cost, is not accounted for by the per-observer bound derived here. These are not defects of the framework. They are the boundaries of what the present subsection establishes, and they mark the directions in which the energy accounting must be extended if it is to become a complete physical theory.

What the subsection does establish is this. The observer pays a fixed price to be real. That price is the free energy required to maintain coherence above the Noor-Planck threshold for one timestep, and it does not depend on the size of the Library, on the number of alternatives that exist as formal possibilities, or on the age of the universe. The universe does not get more expensive as it ages, because the calculation that advances it is local, relational, and constant-time. The cost of observation is \(O(1)\).

---

| PREVIOUS | | NEXT |
| --- | --- | --- | 
| [prev_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-s6.3.md) | [INDEX](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-index.md) | [next_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-s7.0.md) |
