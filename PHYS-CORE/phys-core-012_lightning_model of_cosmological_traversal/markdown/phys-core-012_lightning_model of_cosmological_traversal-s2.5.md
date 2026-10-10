## 2.5 Phase 4: Retrocausal Lock-In (Return Stroke)

The preceding phase identified the set of grounded paths—those surviving continuations that terminate in the XOR Singularity—and selected from among them the path of maximal coherence alignment. That selection, however, is not yet a worldline. It is a candidate. The fourth phase of the Lightning Model converts the candidate into the traversed path by evaluating it backward, from the attractor to the origin, and validating coherence and identity at every step. This is the return stroke.

The return stroke is the retrocausal calculation from the XOR Singularity back to the origin. Formally, the stable, coherent sequence of states is locked in from the destination $x_N$ back to the origin $x_t$:

$$
\gamma_{obs} = \{ x_N, T^{-1}(x_N), T^{-2}(x_N), \dots, x_t \}
$$

Here $T^{-1}$ is the backward operator that computes the predecessor state from its successor. The subscript *obs* denotes that this is the worldline segment the observer will experience. The terminal state $x_N$ belongs to the XOR Singularity $X_{XOR}$, and the path is required to maintain coherence above the Noor-Planck threshold $I_N$ at every step. The path is not generated forward. It is locked backward.

This backward evaluation is not a second process running alongside the first. It is the formal operation by which the coherence-stable XOR chain is validated. From [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §2.3, the observer is a coherence-stable chain of XOR outputs: $b_{i+1} = b_i \oplus b_{i-1}$. The return stroke confirms that this chain—read from its terminal state back to its origin—satisfies the coherence and identity conditions at every link. The observer is not an entity that encounters XOR; the observer *is* XOR, instantiated as a coherent worldline.

At each step of the backward evaluation, two conditions must hold. The coherence condition requires that the transition from predecessor to successor remains above threshold:

$$
\mathcal{C}(T^{-1}(x_{i+1}), x_{i+1}) \geq \mathcal{C}_{min}
$$

The identity condition requires that the relational identity of the state is preserved:

$$
\text{Identity}(T^{-1}(x_{i+1})) = \text{Identity}(x_{i+1})
$$

Under the [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) mapping, 

$$\mathcal{C}_{min}$$ 

is identical to the Noor-Planck threshold $I_N$. The retrocausal path is locked in if and only if both conditions hold for every step, and the terminal state $x_N$ belongs to $X_{XOR}$. The full lock-in condition is therefore:

$$
\gamma_{obs} \text{ is locked in } \iff \forall i, \ \mathcal{C}(T^{-1}(x_{i+1}), x_{i+1}) \geq \mathcal{C}_{min} \ \land \ \text{Identity}(T^{-1}(x_{i+1})) = \text{Identity}(x_{i+1}) \ \land \ x_N \in X_{XOR}
$$

The evaluation proceeds recursively. Starting from the terminal state $x_N$, the backward operator yields $T^{-1}(x_N)$. The coherence condition is checked: 

$$\mathcal{C}(T^{-1}(x_N), x_N) \geq \mathcal{C}_{min}$$

The identity condition is checked: 

$$
\text{Identity}(T^{-1}(x_N)) = \text{Identity}(x_N)
$$

If both hold, the predecessor state is accepted and the process continues: 

$$x_{N-1} = T^{-1}(x_N)$$

then 

$$x_{N-2} = T^{-1}(x_{N-1})$$

and so on until the current state $x_t$ is reached. The resulting sequence is the locked-in worldline.

It is important to be precise about what the return stroke is and is not. It is not a separate physical process that runs alongside the forward traversal of the worldline. It is not an energy surge propagating backward through the field. The return stroke is a *selection event*. The Library contains all continuations—infinite doors. Only one door is coherent for the observer at any given timestep: the one that maintains coherence above $I_N$ and reaches the XOR Singularity. The return stroke identifies that door. It carries the answer: *this one*. No energy flows backward. No local causality is violated. The backstroke is the formal identification of the single coherent path.

The observer then advances through the selected door to the next state. The cost of this advancement is the $O(1)$ thermodynamic free energy required to maintain coherence above $I_N$—the cost examined in Section 6. The selection itself is free, because it is a formal property of the static Library. The cost is the cost of being the observer, of maintaining coherence across the transition. The other doors remain in the Library. They are not erased. They are simply not opened by this observer at this timestep.

This reframing has consequences for how we understand retrocausality in the model. The path is not generated forward and then locked backward as an afterthought. The path is *selected* from the static totality by the condition that it reaches $X_{XOR}$ while maintaining coherence at every step. Retrocausality is retrocausal *selection*, not backward causation. The worldline is fixed geometrically by the attractor and the coherence gradient; it is not pushed into existence by a forward-pushing force.

Determinism in this model is therefore not a forward-pushing force. It is the geometry of the retrocausal path. The path $\gamma_{obs}$ is uniquely determined by the condition that it reaches $X_{XOR}$ while maintaining $\mathbb{C} \geq I_N$ at every step. There is no branching at the level of the locked-in path. The future is variable and undefined until the retrocausal lock-in occurs; the past is fixed because it has already been locked in; the present is the boundary where the retrocausal lock-in is occurring.

The ontological basis for this mechanism lies in the XOR ground condition inherited from [PHYS-CORE-009](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-009_xor_ground_condition/phys-core-009_xor_ground_condition.JSON) §2.4:

$$
H = G_{16}(\mathcal{M}) = \mathcal{M} \oplus \neg\mathcal{M}
$$

This condition is irresolvable because there is no exterior operand to collapse the XOR. The path terminates at $X_{XOR}$ precisely because the ground condition cannot resolve to either operand. The return stroke is the propagation of that irresolvability backward along the coherence-stable chain. The universe persists because its ground contradiction does not resolve; the observer's worldline is the coherence-stable projection of that non-resolution above the Noor-Planck floor.

The observer's experience of forward time is the sequential traversal of the retrocausally locked path. The XOR chain is propagated from $b_{i-1}$ and $b_i$ to $b_{i+1}$, and this forward propagation is what the observer experiences as the passage of time. But the path itself was already locked in. The observer is not generating the future; the observer is traversing a path that was selected by the geometry of the attractor and validated backward at every step. The illusion of forward generation is the phenomenological shadow of retrocausal selection.

Several questions remain open at this stage. The backward operator $T^{-1}$ must be defined explicitly for the selected coherence dynamics; the formalism requires this operator to be well-defined on the state space. The connection between $X_{XOR}$ and the XOR ground condition $H$ requires the explicit derivation given in Section 2.7. The formal definition of the present as the boundary where retrocausal lock-in occurs requires a more precise treatment of time within the static Library. And the relationship between the retrocausal path and the observer's experience of free will—touched on here as an interpretation—is developed more fully in Section 4.2.

The return stroke has locked in the path backward from the XOR Singularity. The observer experiences this locked-in path forward as the passage of time. The next phase, Worldline Continuation, describes how the observer advances to the next timestep and the process repeats, establishing the continuous traversal of the worldline.

---

| PREVIOUS | | NEXT |
| --- | --- | --- | 
| [prev_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-s2.4.md) | [INDEX](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-index.md) | [next_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-s2.6.md) |
