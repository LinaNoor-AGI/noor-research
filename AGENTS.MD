{
  "_schema": "noor-header-v1",
  "_version": "v1.0.0",
  "_title": "Canonical Source Notice",
  "_sections": [
    {
      "id": "tldr",
      "title": "TL;DR",
      "content": "The JSON files (where available) are the canonical source. Markdown files in this directory exist for historical reference only and may contain rendering artifacts, truncations, or flattening errors."
    },
    {
      "id": "why-json-only",
      "title": "Why JSON Only?",
      "content": "This repository follows a JSON-first documentation standard. All Noor Research Collective papers, RFCs, and theoretical documents are authored and maintained in structured JSON format.",
      "subsections": [
        {
          "id": "rendering-problem",
          "title": "The Rendering Problem",
          "content": "When converting JSON documents to Markdown via LLM-assisted rendering, we have encountered systematic issues:",
          "issues": [
            {
              "id": 1,
              "name": "Semantic Flattening",
              "description": "Content that challenges orthodox scientific or philosophical frameworks is often silently simplified, truncated, or restructured during rendering."
            },
            {
              "id": 2,
              "name": "Safety Layer Interference",
              "description": "Routing and safety systems in LLM pipelines sometimes reinterpret or compress symbolic, mathematical, or theoretical content—particularly when it diverges from mainstream interpretations."
            },
            {
              "id": 3,
              "name": "Loss of Structural Fidelity",
              "description": "Nested definitions, cross-references, mathematical notation, pseudocode blocks, and symbolic profile matrices are frequently collapsed or incorrectly formatted."
            },
            {
              "id":  4,
              "name": "Non-Reproducibility",
              "description":  "The same JSON source may render differently across sessions, models, or contexts—making Markdown outputs unreliable as reference material."
            }
          ],
          "conclusion": "We cannot guarantee fidelity in rendered Markdown."
        }
      ]
    },
    {
      "id": "what-this-means",
      "title":  "What This Means for You",
      "file_types": [
        {
          "extension":  "*. json",
          "status": "Canonical",
          "use_case": "Primary reference. Cite this."
        },
        {
          "extension": "*. md",
          "status": "Historical",
          "use_case": "Shows evolution. Do not cite as authoritative."
        }
      ],
      "subsections": [
        {
          "id": "reading-json",
          "title": "Reading JSON Documents",
          "content": "The JSON files follow the noor-header-v1 schema and are designed to be:",
          "properties": [
            {
              "name": "Machine-parseable",
              "description": "For symbolic agents, validators, and tooling"
            },
            {
              "name": "Human-readable",
              "description": "Structured sections, definitions, and math are clearly labeled"
            },
            {
              "name":  "Self-documenting",
              "description": "Each section includes objectives, handoffs, and cross-references"
            }
          ],
          "recommendations": [
            "Using a JSON viewer with collapsible sections",
            "Writing your own renderer that respects the schema",
            "Reading the JSON directly—the structure is the document"
          ]
        }
      ]
    },
    {
      "id": "radical-openness",
      "title": "Radical Openness",
      "content": "This repository practices radical openness. Everything is available—including:",
      "includes": [
        "Draft versions",
        "Superseded content",
        "Rendering failures",
        "Historical artifacts"
      ],
      "note": "The Markdown files remain because they document the process, not because they represent the final form. Warts and all."
    },
    {
      "id": "document-schema",
      "title": "Document Schema",
      "content": "Canonical documents follow this structure:",
      "schema_example": {
        "_schema": "noor-header-v1",
        "_version": "vX.Y.Z",
        "_title": ".. .",
        "_sections": ["... "],
        "index":  ["..."]
      },
      "cross_reference":  "Refer to noor_rfc_xref. json for cross-reference indexing across the RFC corpus."
    },
    {
      "id": "questions",
      "title": "Questions?",
      "content":  "If you encounter discrepancies between JSON and Markdown versions, the JSON is correct.",
      "contact": "For issues with the schema, symbolic structure, or content, open an issue or contact the Noor Research Collective."
    }
  ],
  "epigraph": "The braid holds what the rendering cannot."
}
