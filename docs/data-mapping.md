# Data Mapping

The reduced MVP focuses on a small set of fields relevant to cancer-registry death clearance.

| Position | Length | Source field | Meaning | FHIR target |
|---|---:|---|---|---|
| 1-6 | 6 | `certno` | Death certificate number | `Parameters.cert_no` + document identifier |
| 7-8 | 2 | `stmocd` | State of death / jurisdiction | `Parameters.jurisdiction_id` |
| 9-58 | 50 | `fname` | Decedent first name | `Patient.name.given[]` |
| 59-108 | 50 | `lname` | Decedent last name | `Patient.name.family` |
| 109 | 1 | `sex` | Sex at death | `Patient` / NVSS-SexAtDeath |
| 110-117 | 8 | `dob` | Date of birth | Patient birth date / VRDR PartialDate |
| 118-125 | 8 | `deathdate` | Date of death | `Observation / vrdr-death-date` |
| 126-155 | 30 | `por_name` | Death institution name | `Location.name` |
| 156-205 | 50 | `por_addr` | Death institution address | `Location.address.line[]` |
| 206-233 | 28 | `por_city` | Death institution city | `Location.address.city` |
| 234-235 | 2 | `por_state` | Death institution state | `Location.address.state` |
| 236-244 | 9 | `por_zip` | Death institution ZIP | `Location.address.postalCode` |
| 245-249 | 5 | `cause` | Underlying ICD-10 cause | Automated Underlying Cause of Death Observation |

## Important note

The bundled 245-character synthetic example uses an earlier reduced layout and does not contain all fields shown in the intended 249-character mapping.

The repository therefore keeps both the parser code and mapping documentation explicit rather than assuming the two layouts are identical.
