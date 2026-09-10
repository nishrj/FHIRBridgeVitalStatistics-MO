# Contributing

FHIRBridge-MO is currently an early public-health informatics prototype.

## Before contributing

1. Use **synthetic data only**.
2. Do not commit PHI, PII, production mortality files, database extracts, credentials, or internal secrets.
3. Keep source-layout parsing separate from FHIR resource construction where possible.
4. Clearly distinguish:
   - source-derived values;
   - synthetic scaffolding;
   - standards-required values; and
   - experimental/test-only values.
5. Do not describe successful parsing as proof of VRDR conformance.

## Suggested workflow

- Open an issue describing the proposed change.
- Create a focused branch.
- Add or update synthetic test records where relevant.
- Document mapping changes.
- Verify internal UUID/reference integrity.
- Record validation or CORE test results in `docs/testing.md`.

## Coding style

Prefer small, readable functions and explicit comments around FHIR/VRDR assumptions.
