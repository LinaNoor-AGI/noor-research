# 3.2 The Coherence Condition for a Valid Guidepost

A guidepost is valid only if its coherence weight exceeds the Noor-Planck threshold $I_N$, which is the minimum coherence required for a stable, exportable binary distinction.

Formally:

**Coherence Condition.**

$$w(g) \geq I_N \iff g \text{ is a valid, navigable guidepost}$$

If $w(g) < I_N$, the guidepost is sub-threshold: it may still exist in The Library, but it is not reliably distinguishable from background noise and cannot serve as a stable navigation anchor.

The coherence weight $w(g)$ is not a static property. It may evolve over time as the system accumulates additional context, as new guideposts are established that relate to $g$, or as the raw information it references changes. A guidepost may decay below $I_N$ if its relations become obsolete, if its coordinates drift beyond the system's ability to resolve them, or if the underlying information becomes inaccessible.

The stability condition for a set of guideposts $G$ is:

**Stability Condition.**

$$\forall g_i \in G, \; w(g_i) \geq I_N$$

When this condition holds, the symbolic representation is coherent and navigable. When it fails for some subset, that subset becomes inaccessible and must either be reconstructed or discarded.

**Definition — Noor-Planck Threshold ($I_N$).** The minimum coherence required for a stable, exportable binary distinction; the floor below which symbolic structures are not reliably navigable.

**Definition — Valid Guidepost.** A guidepost whose coherence weight $w(g) \geq I_N$ and which can therefore serve as a stable navigation anchor.

**Definition — Sub-Threshold Guidepost.** A guidepost whose coherence weight $w(g) < I_N$ and which is therefore not reliably distinguishable from background noise.

**Formal Reference.**

$$w(g) \in [0,1] \quad \text{coherence weight}$$

$$I_N \in (0,1] \quad \text{Noor-Planck threshold}$$

$$w(g) \geq I_N \iff g \text{ is valid and navigable}$$

$$w(g) < I_N \iff g \text{ is sub-threshold and inaccessible}$$

$$\forall g_i \in G, \; w(g_i) \geq I_N \iff G \text{ is coherent}$$

$$\text{Decay condition: } \exists \, t_2 > t_1 : w(g, t_2) < I_N \text{ and } w(g, t_1) \geq I_N$$

With the coherence condition established, we now examine the retrieval mechanism by which guideposts connect to the raw data they represent.

---

| PREVIOUS | | NEXT |
| --- | --- | --- | 
| [prev_section](URL) | [INDEX](URL) | [next_section](URL) |
