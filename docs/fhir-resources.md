# FHIR Resources and Technologies

## Release / implementation guide

- FHIR R4
- HL7 Vital Records Death Reporting (VRDR) Implementation Guide v3.0.0

## Resources represented in the current CORE-aligned prototype

| Resource | Role |
|---|---|
| `Bundle` | batch, message, and document containers |
| `Parameters` | certificate, year, jurisdiction, synthetic auxiliary ID |
| `MessageHeader` | message metadata/focus |
| `Composition` | death-certificate document organization |
| `Patient` | decedent |
| `Observation` | death date, underlying cause, supporting observations |
| `Location` | death location/supporting location |
| `Practitioner` | certifier scaffold |
| `Procedure` | death-certification scaffold |
| `RelatedPerson` | supporting family scaffold |
| `Organization` | supporting funeral-home scaffold |
| `Library` | CQL prototype artifact |

## Other technologies

**CQL:** prototype first-pass cancer-coded-death logic; not the production DCO
algorithm.

**Bulk-oriented NDJSON:** one FHIR resource per line grouped by resource type;
not a complete server-side `$export` implementation.

SMART on FHIR and CDS Hooks are not used in the current MVP.
