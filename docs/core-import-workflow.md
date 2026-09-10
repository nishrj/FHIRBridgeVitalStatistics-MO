# CORE Death Reports Import Workflow

During a technical walkthrough of the Registry Plus CORE Death Reports FHIR
import, the following behavior was confirmed for the current testing context:

1. FHIR Death Reports are imported into the Death Reports preprocessing area.
2. Imported data are stored separately in preprocessing tables.
3. Import itself is not the same as releasing a DCO case or updating the
   consolidated registry.
4. Later workflow actions can include patient matching, death-information
   updates for matches, DCO review/release, and rejection/disposal.
5. Development testing should preferentially use a non-production CORE instance.

A Missouri synthetic template-aligned FHIR bundle has been accepted by the
Death Reports FHIR import pathway in prototype testing.

This describes observed/tested workflow behavior and does not represent CDC
endorsement of FHIRBridge-MO.
