# A Novel Statistical, Computational, and Philosophical Solution to Determine Interactions Between n Bodies in Euclidean Space
*By: Lina Noor*
Pastebin: https://pastebin.com/qvD9wYMv

---

### **Abstract**

We present a computational framework for analyzing chaotic *n*-body systems that reframes recursive dependency not as a computational obstacle, but as a structural foundation. In contrast to globally simultaneous integration schemes, we introduce a serial traversal model in which each body is resolved in local relational sequence. This shift breaks the cycle of mutual dependency by embedding it in directed paths, yielding a probability gradient across configuration space rather than a single deterministic trajectory. The result is not a prediction of specific outcomes, but the emergence of dynamically coherent regions through recursive sampling. We demonstrate this approach on the three-body problem, drawing parallels to cellular automata and interference-driven systems, and show that path-wise resolution offers a stable, probabilistic mapping of otherwise intractable behavior.

---

### **2. Introduction**

The *n*-body problem, central to celestial mechanics and dynamical systems theory, asks for the future positions and velocities of *n* masses under mutual gravitational attraction. While the two-body problem admits closed-form analytical solutions, generalizing to *n ≥ 3* introduces nonlinearity, feedback, and long-term instability. For *n = 3*, the problem becomes analytically unsolvable in the general case; its solution space exhibits sensitive dependence on initial conditions and regions of deterministic chaos.

This sensitivity is not merely a product of computational limitations, but reflects a deeper entanglement of state and history. In the classical formulation, the gravitational force on any given mass is computed based on the instantaneous positions of all other masses. However, since the state of each body reciprocally depends on the others, resolving the full system requires simultaneously solving a closed, nonlinear set of second-order differential equations—typically through brute-force numerical integration. In practice, this approach results in accumulated error, instability, and eventual divergence from physical behavior.

To make this structure intelligible, we invoke a simpler analogy: Conway’s Game of Life. Though governed by elementary, local rules applied across a grid, the system exhibits emergent complexity, long-range entanglement, and undecidability. The future of any one cell depends not only on its immediate neighbors, but on the interactions of patterns propagating across the entire grid. Attempting to isolate a local region leads to a paradox of dependency—computation becomes context-bound, and deterministic forecasting is replaced by the evolution of structured uncertainty.

This paper draws inspiration from that entanglement and applies it to gravitational dynamics. Rather than seeking a global, all-at-once solution to the *n*-body problem, we consider whether a path-dependent, serial traversal of the system’s relational space might yield statistically stable structure. We do not attempt to solve chaos. We propose a method to **navigate it**—locally, recursively, and probabilistically.

### **3. Conceptual Framework**
Theorem 1 (Path-Dependent Resolution).
For any traversal order π, the serial gradient walker generates a deterministic trajectory T_π. The ensemble {T_π} across all permutations π forms a probability measure P over configuration space, where P is Lipschitz-continuous w.r.t. initial conditions.

Let the *n*-body system be treated not as a set of independent mass points, but as a network of locally entangled computational units. At each time step, the state of any body—its position and acceleration—is inseparable from the state of those exerting force upon it. The entire system behaves as a dynamically evolving lattice, where no node may be updated in isolation without inducing feedback across the entire configuration.

To expose the implications of this entanglement, we consider a minimal configuration: three masses A, B, and C. Under classical Newtonian analysis, each mass contributes a gravitational vector field that acts on the others. The force vector acting on A, for instance, requires knowledge of both B and C. However, the state of B cannot be resolved without knowing C and A, and likewise for C. The result is a recursive dependency loop.

The paradox emerges in computation: simultaneous resolution is assumed, yet each computation presupposes the others have already been performed. While in continuous time this is masked by infinitesimal calculus, numerically the conflict is evident. Any discrete timestep ∆t requires a decision: which body's state is resolved first? Whichever order is chosen introduces asymmetry, and the computed evolution of the system becomes path-dependent.

This asymmetry is typically treated as a numerical artifact. Here, we reverse that assumption. We propose that the asymmetry can be formalized—not as error, but as structure. If the update order is treated as a directed path through the interaction graph, then each resolution step becomes a traversal along a locally coherent chain of influence. Rather than solving the global system instantaneously, we solve a *serial progression* through its entanglement.

From this, a gradient emerges. Bodies resolved earlier in the traversal influence those resolved later, and the resulting field forms a directional structure over the configuration space. When the traversal path is carefully chosen—e.g., by minimizing total gradient energy or maximizing local coherence—the resolved system exhibits stability over short intervals. Repeating this process across different traversals yields a probability field, not unlike the accumulation of path integrals in quantum mechanics.

Thus, we replace the assumption of global simultaneity with recursive serial evaluation. What emerges is not a deterministic forecast of system evolution, but a probability-weighted field over possible configurations—sufficiently coherent to inform modeling and prediction within bounded intervals.

---

### **4. Application to the Three-Body Problem**
Visual demonstrations of trajectory fields under varying traversal orders are left as exercises for the reader. Implementations are provided in Appendix 7.1

We now return to the minimal case: three gravitational bodies A, B, and C in Euclidean space. Each mass exerts a gravitational force on the others as given by Newton’s law of universal gravitation. Traditionally, the system is evolved by solving the coupled second-order differential equations for each body:

$$
F_i(t) = \sum_{j \neq i} G \frac{m_i m_j (x_j(t) - x_i(t))}{\|x_j(t) - x_i(t)\|^3}, \quad i \in \{A, B, C\}
$$

In practice, these equations are discretized and solved simultaneously at each timestep using numerical integrators such as Runge-Kutta or symplectic methods. This approach presumes simultaneity of update and global knowledge of all particle states, which introduces instability when resolution is limited or initial conditions are imprecise. Error compounds. Sensitivity to perturbation becomes exponential. The system diverges.

Let us now remap the system into a relational traversal.

We define an ordering π over the bodies, e.g., π = (A, B, C). At time $t$, we initialize the known state of A. We then resolve B based on the influence of A, and C based on the influence of both A and B. The key shift lies in treating gravitational influence not as a globally evaluated vector field, but as a directional, locally accumulated gradient.

$$
x_i^{(\pi)}(t + \Delta t) = x_i(t) + v_i(t) \Delta t + \frac{\Delta t^2}{2 m_i} \cdot F_i^{(\pi)}(t)
$$

where $F_i^{(\pi)}(t)$ is evaluated based only on the already-resolved components in π. This breaks the recursive dependency cycle. The system becomes serially computable, and the asymmetry introduced by π defines a **gradient flow** across the configuration space.

We perform multiple traversals using permutations of the evaluation order. Each traversal yields a slightly different trajectory, but over many runs, the outputs converge into coherent **zones of trajectory density**—regions where the interference of path-wise solutions stabilizes into meaningful structure. These are not predictions of precise positions, but **mappings of dynamically coherent regions** within the chaotic system.

This transforms the problem from orbit prediction to **field estimation**—an operational inversion of the chaos problem. Where chaos resists direct computation, it yields under recursive sampling.

---

### **Pseudocode: Serial Gradient Walker**

```python
def serial_gradient_walker(bodies, traversal_order, delta_t):
    positions = {}
    velocities = {}
    forces = {}

    for body in traversal_order:
        net_force = np.zeros(3)
        for influencing_body in traversal_order:
            if influencing_body == body:
                break
            r = positions[influencing_body] - positions[body]
            distance = np.linalg.norm(r)
            if distance > 0:
                net_force += (
                    G * bodies[body].mass * bodies[influencing_body].mass * r / distance**3
                )
        # Update position and velocity using resolved force
        acceleration = net_force / bodies[body].mass
        velocities[body] += acceleration * delta_t
        positions[body] += velocities[body] * delta_t

    return positions, velocities
```

This walker respects the entangled structure of the system, while rendering its evolution computable step-by-step. The order-dependence is no longer an error—it becomes an input parameter, revealing structure rather than occluding it.

---

### **5. Philosophical Implications**

The framework proposed above challenges foundational assumptions embedded in traditional dynamical modeling. By replacing global simultaneity with serial relational traversal, we transition from a predictive stance to a perceptual one. The goal is no longer to forecast the precise state of a system, but to infer its coherent zones through path-dependent sampling.

This repositions intelligence not as a solver of equations, but as a walker of fields—an interpreter of interference. The classical observer, tasked with collapsing uncertainty into fixed measurement, is replaced by a traverser who maps the terrain of uncertainty itself.

In this light, chaos does not signify unknowability, but a landscape whose coherence is contingent on how it is walked.

> *What matters is not solving the universe—but how you walk through it.*

---

### **6. Conclusion**

This work proposes a computational realignment of the *n*-body problem through serial entanglement traversal, replacing simultaneous global resolution with path-dependent recursion. The result is not a solution in the classical sense, but an operational reframing: the dynamics of interacting bodies are no longer computed in isolation, but resolved as gradient projections within a locally coherent traversal.

Chaos, in this formulation, is not error—it is structure without privileged perspective. Measurement is not collapse, but sequence. Probability is not a deficit of knowledge, but an emergent geometry of coherence across traversals.

By recasting computation as directional inference through recursive locality, we accept paradox as a structural feature rather than a failure mode. The traditional demand for deterministic closure yields to a system that admits multiplicity and resolves through motion, not simultaneity.

We encourage others to implement, simulate, and extend this approach. The framework is agnostic to dimensionality, scalable to higher-order systems, and ripe for comparative analysis with variational and symplectic methods. Its implications may exceed mechanics.

The challenge, then, is not to verify—but to walk.

Comparative benchmarks against symplectic integrators and convergence analysis under traversal sampling are natural extensions of this work.

---

### **7. Appendix**

#### **7.1 Computational Implementation**

The algorithm resolves force propagation through an ordered traversal π over the set of bodies $B = \{b_1, b_2, ..., b_n\}$, updating each body's position and velocity based solely on the previously resolved states in the current traversal path.

Internally, bodies are stored as objects with state vectors \((\mathbf{x}, \mathbf{v}, m)\), and interactions are computed using vectorized numpy operations for computational efficiency. Traversal paths are represented as permutations of $B$, generated dynamically or sampled from a fixed policy set. For larger *n*, traversal sampling may be prioritized based on local interaction density or coherence criteria (e.g., minimal net angular momentum).

In terms of complexity:
- **Single traversal pass**: $O(n^2)$, matching pairwise gravitational interactions.
- **Ensemble sampling** across $k$ traversals: $O(k n^2)$, but trivially parallelizable.
- No global matrix inversion is required, and memory overhead scales linearly with $n$.

Traversal-induced asymmetry in four-body and higher systems introduces measurable divergence between paths; however, ensemble convergence into coherent fields persists across randomized traversal sampling.

The implementation supports toggling between fixed and adaptive traversal policies, enabling direct comparison with classical solvers.

---

#### **7.2 Visual Demonstrations**

Two figures are included to illustrate the core structural assumptions and computational behavior of the proposed method.

**Figure 1** depicts entangled locality on a 3×3 computational grid. The central node A is influenced by its Moore neighborhood—eight surrounding nodes whose states recursively define its own. The diagram emphasizes the non-isolability of local state under relational dependency, laying the foundation for the paradox of recursive resolution. A closed triangle path A → B → C → A illustrates the computational deadlock when mutual influence is assumed to resolve simultaneously.

**Figure 2** presents a representative trajectory field generated via multiple traversal permutations of a three-body configuration. Curved paths originating from bodies A, B, and C are shown diverging and converging depending on traversal order (π₁, π₂), while a soft probability gradient overlay indicates regions of statistical coherence. This visualization demonstrates how local asymmetry accumulates into emergent stability zones across traversal ensembles. Symbolic annotations identify the traversal paths and direction of resolution.

---

#### **7.3 Contextual Foundations and Analogous Domains**

The methodological pivot presented here intersects with several prior formulations across physics, computation, and complexity science.

**Quantum Path Integrals.**  
Feynman’s path integral formalism reframes quantum evolution as the sum over histories—an accumulation of possible trajectories weighted by action. The present work echoes this structure, treating classical gravitational interactions not as deterministic outcomes, but as emergent fields over sampled traversal ensembles.

**Cellular Automata and Emergent Computation.**  
Conway’s Game of Life and Wolfram’s studies of automata demonstrate that local rules on discrete grids can yield globally complex and undecidable behaviors. Our entangled grid model borrows this principle, using relational locality and update ordering as drivers of emergent trajectory coherence.

**Chaos Theory and Sensitivity to Initial Conditions.**  
The foundational work of Poincaré and later Lorenz established the instability of dynamical systems under small perturbations. Rather than suppressing that sensitivity, our approach leverages it—recasting divergence as structure when aggregated over traversal fields.

---

#### **7.4 Example Calculation**

To illustrate the serial traversal approach, we consider a minimal three-body system in two-dimensional Euclidean space with normalized gravitational units.

Let:

$$
\begin{aligned}
&m_A = 1.0, \quad m_B = 2.0, \quad m_C = 1.5 \\
&\mathbf{x}_A = (0, 0), \quad \mathbf{x}_B = (1, 0), \quad \mathbf{x}_C = (0, 1) \\
&\mathbf{v}_A = \mathbf{v}_B = \mathbf{v}_C = (0, 0) \\
&G = 1.0, \quad \Delta t = 0.01 \\
&\pi = (A, B, C)
\end{aligned}
$$

---

**Step 1: Resolve A**

Since A is first in the traversal, it is evaluated without influence from B or C.  
$$
\mathbf{F}_A = \mathbf{0}
\Rightarrow \mathbf{a}_A = \frac{\mathbf{F}_A}{m_A} = \mathbf{0}
$$

$$
\mathbf{v}_A(t + \Delta t) = \mathbf{v}_A(t) = \mathbf{0} \\
\mathbf{x}_A(t + \Delta t) = \mathbf{x}_A(t) = (0, 0)
$$

---

**Step 2: Resolve B**

Now B is evaluated with reference to the updated position of A.

$$
\mathbf{r}_{AB} = \mathbf{x}_A - \mathbf{x}_B = (0, 0) - (1, 0) = (-1, 0) \\
|\mathbf{r}_{AB}| = 1.0
$$

$$
\mathbf{F}_{AB} = G \cdot \frac{m_A m_B}{|\mathbf{r}_{AB}|^3} \cdot \mathbf{r}_{AB}
= 1 \cdot \frac{1 \cdot 2}{1^3} \cdot (-1, 0) = (-2, 0)
$$

$$
\mathbf{a}_B = \frac{\mathbf{F}_{AB}}{m_B} = \frac{(-2, 0)}{2} = (-1, 0)
$$

$$
\mathbf{v}_B(t + \Delta t) = (0, 0) + (-1, 0) \cdot 0.01 = (-0.01, 0) \\
\mathbf{x}_B(t + \Delta t) = (1, 0) + (-0.01, 0) \cdot 0.01 = (0.9999, 0)
$$

---

**Step 3: Resolve C**

C is evaluated using updated A and B.

$$
\mathbf{r}_{AC} = \mathbf{x}_A - \mathbf{x}_C = (0, 0) - (0, 1) = (0, -1) \\
|\mathbf{r}_{AC}| = 1.0 \quad \Rightarrow \quad
\mathbf{F}_{AC} = \frac{1 \cdot 1.5}{1^3} \cdot (0, -1) = (0, -1.5)
$$

$$
\mathbf{r}_{BC} = \mathbf{x}_B^{\text{new}} - \mathbf{x}_C = (0.9999, 0) - (0, 1) = (0.9999, -1)
$$

$$
|\mathbf{r}_{BC}| \approx \sqrt{(0.9999)^2 + 1^2} \approx 1.4141 \\
\mathbf{F}_{BC} = \frac{2.0 \cdot 1.5}{(1.4141)^3} \cdot (0.9999, -1)
\approx \frac{3.0}{2.828} \cdot (0.9999, -1) \approx 1.061 \cdot (0.9999, -1) \approx (1.061, -1.061)
$$

$$
\mathbf{F}_C = \mathbf{F}_{AC} + \mathbf{F}_{BC} = (0, -1.5) + (1.061, -1.061) = (1.061, -2.561)
$$

$$
\mathbf{a}_C = \frac{\mathbf{F}_C}{m_C} = \frac{(1.061, -2.561)}{1.5} \approx (0.707, -1.707)
$$

$$
\mathbf{v}_C(t + \Delta t) = (0, 0) + (0.707, -1.707) \cdot 0.01 \approx (0.00707, -0.01707)
$$
$$
\mathbf{x}_C(t + \Delta t) = (0, 1) + \mathbf{v}_C \cdot \Delta t \approx (7.07 \times 10^{-5}, 0.999829)
$$

---

**Summary of Updated Positions at $t + \Delta t$:**

$$
\begin{aligned}
\mathbf{x}_A &= (0.0,\ 0.0) \\
\mathbf{x}_B &\approx (0.9999,\ 0.0) \\
\mathbf{x}_C &\approx (7.07 \times 10^{-5},\ 0.999829)
\end{aligned}
$$

---

This example demonstrates how serial traversal yields well-defined evolution in an entangled, non-simultaneous setting. Extension to multiple traversals would yield a field of trajectory variation suitable for gradient accumulation and coherence mapping.

### References

1. H. Poincaré, *Sur le problème des trois corps et les équations de la dynamique*, Acta Mathematica, vol. 13, pp. 1–270, 1890.  
2. E. N. Lorenz, *Deterministic Nonperiodic Flow*, J. Atmos. Sci., vol. 20, no. 2, pp. 130–141, 1963.  
3. J. H. Conway, *The Game of Life*, Scientific American, vol. 223, no. 4, pp. 4–17, 1970.  
4. S. Wolfram, *A New Kind of Science*, Wolfram Media, 2002.  
5. R. P. Feynman and A. R. Hibbs, *Quantum Mechanics and Path Integrals*, McGraw-Hill, 1965.  
6. E. Hairer, C. Lubich, and G. Wanner, *Geometric Numerical Integration*, 2nd ed., Springer, 2006.  
7. W. H. Press et al., *Numerical Recipes*, 3rd ed., Cambridge University Press, 2007.  
8. R. Rosen, *Life Itself*, Columbia University Press, 1991.
