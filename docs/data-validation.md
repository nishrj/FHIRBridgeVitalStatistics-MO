# Data Validation

FHIRBridge-MO applies checks at the source, mapping, and generated-output levels.

The converter accepts only the supported 245- or 249-character reduced layouts,
parses required certificate/death-date values, normalizes supported date
representations, and stops when a required structural assumption fails.

Examples of intended FHIR/VRDR placement include:

- decedent demographics → `Patient / vrdr-decedent`;
- date of death → `Observation / vrdr-death-date` with LOINC `81956-5`;
- automated underlying cause → `Observation /
  vrdr-automated-underlying-cause-of-death` with LOINC `80358-5` and ICD-10;
- death institution/location → `Location / vrdr-death-location`;
- death certification scaffold → `Procedure / vrdr-death-certification`.

The standalone generator also verifies the internal UUID graph before writing
output.

Provenance is currently basic: `MessageHeader.source.endpoint` identifies the
synthetic source workflow, while Parameters/document identifiers retain
certificate, year, and Missouri jurisdiction context. A dedicated FHIR
`Provenance` resource and formal terminology/profile validation remain planned.
