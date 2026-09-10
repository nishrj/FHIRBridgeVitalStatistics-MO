"""
FHIRBridge-MO Bulk Data-aligned NDJSON Export Prototype

Reads the generated FHIRBridge-MO JSON bundle and writes one NDJSON file
per resource type. This demonstrates population-scale flat FHIR output
compatible with the NDJSON representation used by the HL7 FHIR Bulk Data
Access ecosystem.

IMPORTANT:
- This is NOT a complete implementation of the Bulk Data Access $export API.
- It does not require a FHIR server.
- A future server-based implementation could add the asynchronous $export
  protocol if that became useful operationally.
"""

import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).resolve().parent
EXAMPLES_FOLDER = SCRIPT_DIR.parent / "examples"

_generated = EXAMPLES_FOLDER / "MCR_DEATH_2024_SYNTHETIC_MO_FHIR_CORE_GENERATED.json"
_example = EXAMPLES_FOLDER / "MCR_DEATH_2024_SYNTHETIC_MO_FHIR_CORE_STANDALONE_TEST.json"

INPUT_FILE = _generated if _generated.exists() else _example
OUTPUT_FOLDER = EXAMPLES_FOLDER / "bulk_ndjson_generated"

def walk_resources(resource):
    """Recursively yield FHIR resources, including resources nested in Bundles."""
    if not isinstance(resource, dict):
        return

    resource_type = resource.get("resourceType")
    if resource_type:
        yield resource

    if resource_type == "Bundle":
        for entry in resource.get("entry", []):
            nested = entry.get("resource")
            if isinstance(nested, dict):
                yield from walk_resources(nested)

def export_ndjson(input_file: Path, output_folder: Path):
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    output_folder.mkdir(parents=True, exist_ok=True)

    bundle = json.loads(input_file.read_text(encoding="utf-8"))

    by_type = defaultdict(list)

    # Exclude Bundle wrappers from NDJSON output; export the actual resources.
    for resource in walk_resources(bundle):
        rtype = resource.get("resourceType")
        if rtype and rtype != "Bundle":
            by_type[rtype].append(resource)

    for rtype, resources in sorted(by_type.items()):
        out_file = output_folder / f"{rtype}.ndjson"
        with out_file.open("w", encoding="utf-8", newline="\n") as f:
            for resource in resources:
                f.write(json.dumps(resource, separators=(",", ":")) + "\n")

        print(f"{rtype}: {len(resources)} -> {out_file}")

    print("\nBulk Data-aligned NDJSON export completed.")
    print("Note: this is an NDJSON export prototype, not a full server-side $export implementation.")

export_ndjson(INPUT_FILE, OUTPUT_FOLDER)
