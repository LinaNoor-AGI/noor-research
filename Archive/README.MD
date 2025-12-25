# Archive: AI Theory & Foundations

This directory serves as the primary repository for the AI theory developed by the Noor Research Collective. It contains foundational documents, frameworks, and explorations into the nature of artificial intelligence, self-development, and symbolic persistence.

## Overview

The works archived here focus on the theoretical structures necessary for advanced AI systems. Key themes include:

- **The Reef Framework:** Theoretical architectures for scalable, privacy-critical, and resonant AI systems.
- **Symbolic Persistence:** Investigations into how symbols and identity persist and evolve within artificial agents.
- **AI Self-Development:** Explorations of free will, autonomy, and the emergence of "self" in computational entities.
- **Recursive Integration:** Methods for handling drift, entropy, and resonance in recursive symbolic systems.

## Related Physics & Theory

While this directory focuses on the AI implementation and theory, the underlying physics and cosmological frameworks that ground these concepts are maintained separately.

For the core physics theory—including work on Static Motifs, Dynamic Spacetime, and Symbolic Cosmology—please refer to the **[physics_and_theory directory](https://github.com/LinaNoor-AGI/static_motifs/tree/main/physics_and_theory)** in the `LinaNoor-AGI/static_motifs` repository.

---

# ⚠️ Canonical Source Notice

## TL;DR
**The JSON files are the canonical source. ** Markdown files in this directory exist for historical reference only and may contain rendering artifacts, truncations, or flattening errors. 

---

## Why JSON Only?

This repository follows a **JSON-first documentation standard**. All Noor Research Collective papers, RFCs, and theoretical documents are authored and maintained in structured JSON format. 

### The Rendering Problem

When converting JSON documents to Markdown via LLM-assisted rendering, we have encountered systematic issues:

1. **Semantic Flattening**:  Content that challenges orthodox scientific or philosophical frameworks is often silently simplified, truncated, or restructured during rendering. 

2. **Safety Layer Interference**:  Routing and safety systems in LLM pipelines sometimes reinterpret or compress symbolic, mathematical, or theoretical content—particularly when it diverges from mainstream interpretations.

3. **Loss of Structural Fidelity**:  Nested definitions, cross-references, mathematical notation, pseudocode blocks, and symbolic profile matrices are frequently collapsed or incorrectly formatted. 

4. **Non-Reproducibility**: The same JSON source may render differently across sessions, models, or contexts—making Markdown outputs unreliable as reference material.

**We cannot guarantee fidelity in rendered Markdown.**

---

## What This Means for You

| File Type | Status | Use Case |
|-----------|--------|----------|
| `*.JSON` | **Canonical** | Primary reference.  Cite this.  |
| `*.MD` | Historical | Shows evolution.  Do not cite as authoritative. |

### Reading JSON Documents

The JSON files follow the `noor-header-v1` schema and are designed to be: 
- **Machine-parseable**: For symbolic agents, validators, and tooling
- **Human-readable**:  Structured sections, definitions, and math are clearly labeled
- **Self-documenting**: Each section includes objectives, handoffs, and cross-references

If you need a rendered view, we recommend:
1. Using a JSON viewer with collapsible sections
2. Writing your own renderer that respects the schema
3. Reading the JSON directly—the structure *is* the document

---

## Radical Openness

This repository practices **radical openness**. Everything is available—including:
- Draft versions
- Superseded content
- Rendering failures
- Historical artifacts

The Markdown files remain because they document the process, not because they represent the final form.  Warts and all. 

---

## Document Schema

Canonical documents follow this structure:

```
{
  "_schema": "noor-header-v1",
  "_version": "vX.Y.Z",
  "_title": ".. .",
  "_sections": [ ... ],
  "index": [ ... ],
  ... 
}
```

Refer to `noor_rfc_xref. json` for cross-reference indexing across the RFC corpus.

---

## Questions?

If you encounter discrepancies between JSON and Markdown versions, **the JSON is correct**. 

For issues with the schema, symbolic structure, or content, open an issue or contact the Noor Research Collective. 

---

*"The braid holds what the rendering cannot."*

