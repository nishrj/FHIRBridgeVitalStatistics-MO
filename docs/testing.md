# Testing Status

The project uses two fully synthetic fixed-width mortality records.

The converter checks supported record length, field extraction, date
normalization, certificate conversion, generated-message shape, and internal
`urn:uuid:` references.

A CDC-supplied reference FHIR Death Reports bundle was used as an initial
structural/import baseline. The first reduced Missouri-generated document
differed substantially from that structure. A revised Missouri synthetic test
artifact was aligned to the 24-resource document pattern while retaining the
selected Missouri synthetic values.

That template-aligned Missouri synthetic bundle was accepted by the CORE Death
Reports FHIR import pathway.

The latest `src/create_mo_fhir_core_standalone.py` embeds the accepted structural
pattern and no longer needs an external template JSON file. The bundled
standalone test output contains two records, uses fresh UUIDs, matches the
embedded message structure, and has no unresolved internal UUID references.

Repeatable CORE imports of freshly generated output should continue to be
documented.

CORE parser acceptance is not equivalent to complete VRDR conformance. Planned
evaluation includes applicable VRDR profile validation, field-level
source-to-output fidelity, terminology review, CQL execution/refinement, and
larger synthetic-volume NDJSON testing.
