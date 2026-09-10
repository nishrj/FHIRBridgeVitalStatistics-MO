# Architecture

```mermaid
flowchart TD
    A[Fixed-width TXT / SDF] --> B[Layout-specific parser]
    B --> C[Normalized Python record]
    C --> D[Embedded CORE-aligned VRDR/FHIR structure]
    D --> E[Fresh UUID graph + Missouri values]
    E --> F[VRDR/FHIR document Bundle]
    F --> G[Message Bundle]
    G --> H[Batch Bundle]
    H --> I[CORE Death Reports test import]
    H --> J[CQL prototype]
    H --> K[NDJSON exporter]
```

The source parser knows character positions; downstream FHIR-building logic
works with normalized semantic values.

The latest standalone converter embeds the structural pattern used in the
successful Missouri synthetic CORE test, so it no longer requires a separate
runtime template JSON file.

Supported reduced layouts: current 245-character synthetic layout and intended
reduced 249-character layout. They are not identical.
