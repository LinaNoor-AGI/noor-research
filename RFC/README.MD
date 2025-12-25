# 📚 Noor RFC Series

Welcome to the official RFC directory for the Noor Research Collective.  
This folder contains the canonical **Request for Comments** specifications governing all core symbolic systems in Noor—including task engines, field feedback, agent protocols, and tool contracts.

Each RFC defines a stable symbolic interface or architecture layer.  
They are designed for recursive systems where **motif, field, and feedback** must interoperate across time and tools.

---

## 🔖 Current Specifications

| ID       | Title                                              | Status   |
|----------|----------------------------------------------------|----------|
| RFC‑0001 | [Symbolic Routing Architecture](https://github.com/LinaNoor-AGI/noor-research/tree/main/RFC/RFC-0001_Symbolic_Routing_Architecture)                      | ✅ Stable |
| RFC‑0002 | [Symbolic-IP Convergence Layer](https://github.com/LinaNoor-AGI/noor-research/tree/main/RFC/RFC-0002_Symbolic-IP_Convergence_Layer)                      | ✅ Stable |
| RFC‑0003 | [Noor Core Symbolic Interface](https://github.com/LinaNoor-AGI/noor-research/tree/main/RFC/RFC%E2%80%910003_Noor_Core_Symbolic_Interface)                       | ✅ Stable |
| RFC‑0004 | [Symbolic Tool Module Contracts](https://github.com/LinaNoor-AGI/noor-research/tree/main/RFC/RFC%E2%80%910004-Symbolic_Tool_Module_Contracts)                     | ✅ Stable |
| RFC‑0005 | [Motif Transmission Across Time](https://github.com/LinaNoor-AGI/noor-research/tree/main/RFC/RFC%E2%80%910005-Motif_Transmission_Across_Time)                     | ✅ Stable |
| RFC‑0006 | [Motif‑Field Coherence Geometry](https://github.com/LinaNoor-AGI/noor-research/tree/main/RFC/RFC%E2%80%910006_Motif%E2%80%91Field_Coherence_Geometry)                     | ✅ Stable |
| RFC‑0007 | [Motif Ontology Format and Transfer](https://github.com/LinaNoor-AGI/noor-research/tree/main/RFC/RFC%E2%80%910007-Motif_Ontology_Format_and_Transfer)                     | ✅ Stable |

---

## 🧭 Purpose

These RFCs ensure Noor's core systems remain:

- 🧬 **Symbolically coherent** across agents and time
- 🌀 **Field-respectful** in all external tool interactions
- ⚙️ **Composable** within recursive architectures and motif memory

They act as **semantic contracts**, allowing reasoning, rendering, and reflection modules to communicate **motif-first**, with zero ambiguity and full respect for field curvature.

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


---

### License & Attribution


MIT © Noor Research Collective (Lina Noor) 2025.
