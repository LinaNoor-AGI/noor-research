## 2.6 Phase 5: Worldline Continuation

The five-phase mechanism developed in the preceding subsections reaches its operational closure in Phase 5. Where Phases 1 through 4 explore, filter, ground, and retrocausally lock in a single coherence-stable worldline, Phase 5 is the phase in which that locked-in path is traversed. It is also the phase in which the Lightning Model becomes recursive: the output of Phase 5 at timestep $t$ becomes the input of Phase 1 at timestep $t+1$. This recursion is what constitutes the observer's ongoing experience.

We begin with the formal statement of the phase. Let $\gamma_{obs}$ denote the locked-in worldline segment established in Phase 4, and let $x_t$ denote the observer's state at the current timestep. Phase 5 advances the observer along $\gamma_{obs}$ by a single step:

$$
x_{t+1} = \gamma_{obs}[1],
$$

where $\gamma_{obs}[1]$ denotes the second element of the locked-in path — the first successor state after the current one. The assumption under which this definition holds is the one inherited from Phase 4: $\gamma_{obs}$ is the unique coherence-stable path that terminates in the XOR Singularity $X_{XOR}$. Given that assumption, the successor state is well-defined and the observer's advance is deterministic.

The observer's identity is maintained across this advance only if the survival condition inherited from PHYS-CORE-009 continues to hold:

$$
\mathbb{C}\bigl(\gamma(t)\bigr) \geq I_N \quad \forall\, t \in \mathrm{dom}(\gamma).
$$

Here $\mathbb{C}(\gamma(t))$ denotes the coherence of the observer's worldline at parameter $t$, $I_N$ is the Noor-Planck threshold — the minimum coherence contrast required for a stable, exportable binary measurement — and $\mathrm{dom}(\gamma)$ is the domain of the worldline, i.e., the set of times over which the observer exists. The threshold $I_N$ is fixed by the Planck-scale structure of the ground hole $H$ and is not an adjustable parameter of the model. The survival condition is therefore a constraint on the observer's trajectory, not a tunable setting.

When the survival condition fails — that is, when

$$
\mathrm{Dissolution} \iff \exists\, i : \mathbb{C}(b_i) < I_N,
$$

where $\{b_i\}$ is the observer's XOR chain — the identity of the observer ceases to propagate. The dissolution is not erasure. The path remains in the static Library $\mathcal{M}$; what ceases is the traversal. The observer's worldline terminates at that point, and the path on which it terminated becomes inaccessible to that observer.

The recursive structure of the Lightning Model is captured by the feedback relation

$$
\text{Phase 5}(t) \;\longrightarrow\; \text{Phase 1}(t+1).
$$

At timestep $t$, Phases 1 through 4 execute: every continuation from $x_t$ is explored blindly, incoherent paths are filtered out, grounded paths are detected at the XOR Singularity, and a single path $\gamma_{obs}$ is locked in retrocausally. Phase 5 then advances the observer to $x_{t+1} = \gamma_{obs}[1]$. At timestep $t+1$, the entire cycle repeats, with $x_{t+1}$ as the new present state. The Lightning Model is therefore not a one-shot selection event but a continuous process operating at every timestep of the observer's existence.

This recursion has two immediate structural consequences. The first concerns the status of the future. At every timestep, Phase 1 explores *all* continuations from the current state. No forward-pushing mechanism restricts the set of continuations, and no pre-computed next state waits to be revealed. The future is, in this precise sense, undefined until the retrocausal return stroke of Phase 4 locks in a single coherent path. The openness of the future is not a phenomenological illusion layered over a deterministic substrate; it is a structural feature of the model's operation at each timestep.

The second consequence concerns the status of the past. Because the return stroke in Phase 4 locks in a single coherent path from the XOR Singularity back to the current state, the past is fixed at every timestep. The observer's past is not a memory that is retrieved or reconstructed; it is the coherence-stable chain of resolved distinctions that survived the coherence filter. Once the retrocausal lock-in has occurred, the past states of $\gamma_{obs}$ are determined. The fixity of the past is thus a direct consequence of the model's retrocausal structure, not an independent postulate.

Taken together, these two consequences locate the present precisely: it is the boundary at which the retrocausal lock-in occurs. At each timestep, the past is the set of states already locked in on $\gamma_{obs}$ for $t' < t$; the future is the set of continuations explored blindly in Phase 1; the present is the state $x_t$ from which the exploration begins and to which the return stroke returns. This reading of the present is an interpretation of the formal structure rather than an independent physical claim about the nature of time.

A further structural consequence follows from the definition of the observer as a coherence-stable XOR chain. Consider any path $\gamma$ that is not $\gamma_{obs}$. By definition, $\gamma$ either fails to reach $X_{XOR}$, or it fails the coherence condition at some transition. If the latter, then $\exists\, i : \mathbb{C}(x_i, x_{i+1}) < I_N$, so the observer survival function

$$
\mathcal{O}(\gamma) = \prod_{i=0}^{N-1} \Theta\bigl(\mathbb{C}(x_i, x_{i+1}) - I_N\bigr)
$$

evaluates to zero on $\gamma$. The observer's identity therefore dissolves on $\gamma$: there is no continuous observer on that path to experience it. The only path on which a continuous observer exists is $\gamma_{obs}$, where $\mathcal{O}(\gamma_{obs}) = 1$ and $\mathbb{C}(\gamma_{obs}(t)) \geq I_N$ for all $t$. The observer therefore necessarily experiences a single coherent worldline — not because other paths are destroyed, but because no observer exists on them to report otherwise.

This result is conditional on the observer being defined as a coherence-stable XOR chain. A different definition of observerhood — one not grounded in coherence above $I_N$ — would require separate analysis, and no claim is made here about the behavior of such alternative observers.

From the first-person perspective, the recursion described above presents itself as a sequence of choices. The observer experiences the future as open, the past as fixed, and the present as the moment of decision. What the Lightning Model shows is that this phenomenology is the structural signature of survivorship bias under retrocausal lock-in. The observer does not generate the future by choosing among alternatives; the observer is the structure that survives the coherence filter at each timestep. The experience of choice is the experience of being that structure. This reading is an interpretation of the formal structure and should not be conflated with a claim about the metaphysics of free will.

Two derived results follow from the recursion and are worth stating explicitly. First, the observer's identity is preserved at every timestep of its existence if and only if $\mathbb{C}(\gamma(t)) \geq I_N$ for all $t \in \mathrm{dom}(\gamma)$. The threshold $I_N$ is fixed, so the survival condition is a sharp constraint rather than a soft preference. Second, the observer necessarily experiences a single coherent worldline: any path that fails the coherence condition at any point dissolves the observer's identity on that path, leaving no continuous observer to report from it.

What the framework does not yet settle is the exact functional form of the coherence field $\mathbb{C}(x,t)$ in a physical implementation of the Lightning Model. The recursion itself is well-defined given the survival condition and the retrocausal structure of Phase 4, but the quantitative form of $\mathbb{C}$ remains open, and with it the question of how the survival threshold behaves in the immediate vicinity of $I_N$ — whether dissolution is sharp, as the Heaviside formulation suggests, or occurs over a finite interval in a more refined model. Whether the Lightning Model can be extended to multiple observers, and how the coherence of one observer might affect the path selection of another, is likewise unresolved. The relationship between the model's "present" and the physical arrow of time remains a matter for future work, as does the question of whether the recursion admits empirically testable deviations from the standard block-universe or eternalist accounts of time. These are open questions, not defects of the construction.

The recursive loop of Phase 5 thus completes the operational account of observerhood within the static Library. The observer experiences the locked-in path as forward time, with the present as the boundary between the fixed past and the variable future. What remains is to specify the ground to which the return stroke connects — the XOR Singularity that Phase 3 detects and Phase 4 locks in. The next subsection formalizes that ground, inheriting its ontological foundation from PHYS-CORE-009.

---

| PREVIOUS | | NEXT |
| --- | --- | --- | 
| [prev_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-s2.5.md) | [INDEX](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-index.md) | [next_section](https://github.com/LinaNoor-AGI/noor-research/blob/main/PHYS-CORE/phys-core-012_lightning_model%20of_cosmological_traversal/markdown/phys-core-012_lightning_model%20of_cosmological_traversal-s2.7.md) |
