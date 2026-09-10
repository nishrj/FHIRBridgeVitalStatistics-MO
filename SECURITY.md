# Security and Data Governance

FHIRBridge-MO is designed for synthetic-data development and interoperability testing.

## Never commit protected or operational data

Do not upload to a public repository:

- real death-certificate or mortality files;
- Social Security numbers;
- names, addresses, dates, or identifiers from real people;
- protected health information (PHI);
- personally identifiable information (PII);
- production database exports or backups;
- credentials, passwords, tokens, private keys, or connection strings;
- internal-only server names or restricted infrastructure details.

## Testing

Use synthetic test data and, where possible, a non-production CORE environment.

A FHIR file successfully importing into a preprocessing table does not establish clinical correctness, production safety, or standards conformance.

## Reporting a security concern

For an institutional deployment, follow the University of Missouri and Missouri Cancer Registry approved security/reporting process rather than posting sensitive details in a public GitHub issue.
