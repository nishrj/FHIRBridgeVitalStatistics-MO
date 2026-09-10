/*
FHIRBridge-MO prototype CQL rules layer
Purpose: demonstrate how standardized FHIR resources can support reusable
logic after legacy mortality data have been transformed to VRDR/FHIR.

IMPORTANT:
- This is prototype logic for demonstration/evaluation, not a production
  cancer-reportability or death-clearance rule.
- It flags an underlying ICD-10 cause beginning with "C" as a potential
  cancer-coded death for further registry review.
*/

library FHIRBridgeMOFollowBack version '0.1.0'

using FHIR version '4.0.1'

include FHIRHelpers version '4.0.1' called FHIRHelpers

codesystem LOINC: 'http://loinc.org'

code "Automated Underlying Cause of Death":
  '80358-5' from LOINC
  display 'Cause of death.underlying [Automated]'

context Patient

define "Underlying Cause Observations":
  [Observation: "Automated Underlying Cause of Death"] O
    where O.status = 'final'

define "Potential Cancer-Coded Death":
  exists (
    "Underlying Cause Observations" O
      let CauseConcept: O.value as FHIR.CodeableConcept
      where exists (
        CauseConcept.coding C
          where C.system.value = 'http://hl7.org/fhir/sid/icd-10'
            and C.code.value is not null
            and StartsWith(C.code.value, 'C')
      )
  )

define "Potential Death-Clearance Follow-Back Candidate":
  "Potential Cancer-Coded Death"
