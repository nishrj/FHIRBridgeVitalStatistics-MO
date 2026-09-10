r"""
create_mo_fhir_core_standalone.py

FHIRBridge-MO standalone synthetic fixed-width -> CORE-aligned VRDR/FHIR
generator.

This version does NOT require an external JSON template file. The structural
pattern used by the previously successful Missouri synthetic CORE import test
is embedded in the script.

The script reads a synthetic 245- or 249-character fixed-width mortality file,
normalizes selected fields, creates fresh UUIDs, substitutes Missouri synthetic
values into the embedded VRDR/FHIR structure, preserves the 24-resource
death-certificate document pattern used by the successful test, validates the
internal UUID graph, and writes a new batch FHIR JSON file.

Input lookup:
1. If MCR_DEATH_2024_SYNTHETIC.txt is beside this script, use it.
2. Otherwise use ../examples/MCR_DEATH_2024_SYNTHETIC.txt.

Output:
MCR_DEATH_2024_SYNTHETIC_MO_FHIR_CORE_GENERATED.json

Synthetic data only. CORE parser acceptance and complete VRDR conformance are
separate tests.
"""



from __future__ import annotations

import base64
import copy
import json
import os
import re
import uuid
import zlib
from datetime import datetime
from pathlib import Path


# ============================================================
# USER SETTINGS / PORTABLE PATHS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent

# Optional environment-variable overrides:
#   FHIRBRIDGE_INPUT
#   FHIRBRIDGE_OUTPUT
#
# If no override is provided, first look beside the script (useful when the
# script is copied to S:\FHIR\working folder2). Otherwise fall back to the
# repository examples folder.

_local_input = SCRIPT_DIR / "MCR_DEATH_2024_SYNTHETIC.txt"
_repo_input = SCRIPT_DIR.parent / "examples" / "MCR_DEATH_2024_SYNTHETIC.txt"
_default_input = _local_input if _local_input.exists() else _repo_input

INPUT_FILE = Path(os.environ.get("FHIRBRIDGE_INPUT", str(_default_input)))

OUTPUT_FILE = Path(
    os.environ.get(
        "FHIRBRIDGE_OUTPUT",
        str(
            INPUT_FILE.parent
            / "MCR_DEATH_2024_SYNTHETIC_MO_FHIR_CORE_GENERATED.json"
        ),
    )
)


# ============================================================
# CONSTANTS
# ============================================================

VRDR = "http://hl7.org/fhir/us/vrdr/StructureDefinition"
JURISDICTION = "MO"
SOURCE_ENDPOINT = "urn:source:mcr-synthetic-sdf"

# ============================================================
# EMBEDDED CORE-ACCEPTED STRUCTURAL TEMPLATE
# ============================================================
#
# This compressed Base64 payload is the structural template used by the
# previously successful CORE parser/import test. Keeping it inside the
# script removes the need for a separate JSON template file.
#
_EMBEDDED_CORE_TEMPLATE_B64 = (
    "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"
)


def load_embedded_core_template() -> dict:
    """Return a fresh Python dict containing the embedded template."""
    raw = zlib.decompress(
        base64.b64decode(_EMBEDDED_CORE_TEMPLATE_B64)
    )
    return json.loads(raw.decode("utf-8"))



# ============================================================
# GENERAL HELPERS
# ============================================================

def clean(value: str) -> str:
    return value.strip()


def parse_mmddyy(value: str) -> tuple[int, int, int] | None:
    """
    Parse MMDDYY.

    Prototype rule retained from the earlier converter:
      YY >= 30 -> 19YY
      YY < 30  -> 20YY
    """
    value = clean(value)

    if len(value) != 6 or not value.isdigit():
        return None

    month = int(value[0:2])
    day = int(value[2:4])
    yy = int(value[4:6])

    year = 1900 + yy if yy >= 30 else 2000 + yy
    return year, month, day


def parse_mmddyyyy(value: str) -> tuple[int, int, int] | None:
    """Parse MMDDYYYY."""
    value = clean(value)

    if len(value) != 8 or not value.isdigit():
        return None

    month = int(value[0:2])
    day = int(value[2:4])
    year = int(value[4:8])
    return year, month, day


def normalize_8_digit_date(value: str) -> str:
    """
    Accept YYYYMMDD or MMDDYYYY and return YYYYMMDD.
    """
    value = clean(value)

    if len(value) != 8 or not value.isdigit():
        return ""

    first_four = int(value[:4])

    if 1800 <= first_four <= 2100:
        return value

    parsed = parse_mmddyyyy(value)

    if parsed is None:
        return ""

    year, month, day = parsed
    return f"{year:04d}{month:02d}{day:02d}"


def parse_yyyymmdd(value: str) -> tuple[int, int, int] | None:
    value = clean(value)

    if len(value) != 8 or not value.isdigit():
        return None

    return int(value[:4]), int(value[4:6]), int(value[6:8])


def numeric_certno(source: str) -> tuple[int, str]:
    """
    Convert a synthetic value such as SYN951 to:
      integer: 951
      six-character certificate string: 000951
    """
    digits = "".join(ch for ch in source if ch.isdigit())

    if not digits:
        raise ValueError(
            f"CERTNO has no numeric component: {source!r}"
        )

    cert6 = digits[-6:].zfill(6)
    return int(cert6), cert6


def synthetic_auxiliary_id(cert_int: int) -> str:
    """
    Reduced source does not contain state_auxiliary_id.

    Preserve the four-parameter structure accepted by CORE by generating
    a clearly synthetic deterministic 12-digit value.
    """
    return f"{cert_int:012d}"


def sex_coding(source: str) -> tuple[str, str]:
    mapping = {
        "M": ("male", "Male"),
        "F": ("female", "Female"),
        "U": ("unknown", "Unknown"),
    }
    return mapping.get(
        source.upper(),
        ("unknown", "Unknown"),
    )


def calculate_age(
    birth: tuple[int, int, int] | None,
    death: tuple[int, int, int] | None,
) -> int | None:
    if birth is None or death is None:
        return None

    by, bm, bd = birth
    dy, dm, dd = death

    age = dy - by - ((dm, dd) < (bm, bd))

    if age < 0 or age > 130:
        return None

    return age


# ============================================================
# SOURCE FILE PARSERS
# ============================================================

def parse_current_245(line: str) -> dict[str, str]:
    """
    Parse the 245-character synthetic file that produced the accepted test data.

    Positions:
      1-6     certno
      7-8     stmocd source field
      9-28    unused/filler
      29-53   fname
      54-78   lname
      79      sex
      80-85   dob (MMDDYY)
      86-93   deathdate (MMDDYYYY)
      94-143  por_name
      144-203 por_addr
      204-233 por_city
      234-235 por_state
      236-240 cause
      241-245 trailing filler
    """
    if len(line) != 245:
        raise ValueError(
            f"Expected 245 characters, found {len(line)}"
        )

    dob_parts = parse_mmddyy(line[79:85])
    death_parts = parse_mmddyyyy(line[85:93])

    dob_yyyymmdd = ""
    if dob_parts:
        y, m, d = dob_parts
        dob_yyyymmdd = f"{y:04d}{m:02d}{d:02d}"

    death_yyyymmdd = ""
    if death_parts:
        y, m, d = death_parts
        death_yyyymmdd = f"{y:04d}{m:02d}{d:02d}"

    return {
        "certno": clean(line[0:6]),
        "stmocd_source": clean(line[6:8]),
        "fname": clean(line[28:53]),
        "lname": clean(line[53:78]),
        "sex": clean(line[78:79]),
        "dob_source": clean(line[79:85]),
        "dob_yyyymmdd": dob_yyyymmdd,
        "deathdate_source": clean(line[85:93]),
        "deathdate_yyyymmdd": death_yyyymmdd,
        "por_name": clean(line[93:143]),
        "por_addr": clean(line[143:203]),
        "por_city": clean(line[203:233]),
        "por_state": clean(line[233:235]),
        "por_zip": "",
        "cause": clean(line[235:240]),
    }


def parse_reduced_249(line: str) -> dict[str, str]:
    """
    Parse the intended 249-character reduced layout.

    Positions:
      1-6     certno
      7-8     stmocd
      9-58    fname
      59-108  lname
      109     sex
      110-117 dob
      118-125 deathdate
      126-155 por_name
      156-205 por_addr
      206-233 por_city
      234-235 por_state
      236-244 por_zip
      245-249 cause
    """
    if len(line) != 249:
        raise ValueError(
            f"Expected 249 characters, found {len(line)}"
        )

    dob_source = clean(line[109:117])
    death_source = clean(line[117:125])

    return {
        "certno": clean(line[0:6]),
        "stmocd_source": clean(line[6:8]),
        "fname": clean(line[8:58]),
        "lname": clean(line[58:108]),
        "sex": clean(line[108:109]),
        "dob_source": dob_source,
        "dob_yyyymmdd": normalize_8_digit_date(dob_source),
        "deathdate_source": death_source,
        "deathdate_yyyymmdd": normalize_8_digit_date(death_source),
        "por_name": clean(line[125:155]),
        "por_addr": clean(line[155:205]),
        "por_city": clean(line[205:233]),
        "por_state": clean(line[233:235]),
        "por_zip": clean(line[235:244]),
        "cause": clean(line[244:249]),
    }


def parse_line(line: str) -> dict[str, str]:
    line = line.rstrip("\r\n")

    if len(line) == 245:
        return parse_current_245(line)

    if len(line) == 249:
        return parse_reduced_249(line)

    raise ValueError(
        f"Unsupported SDF record length {len(line)}. Expected 245 or 249."
    )


# ============================================================
# TEMPLATE HELPERS
# ============================================================

def get_template_message(template: dict) -> dict:
    """
    Accept either:
      * the full accepted outer batch Bundle, or
      * a message Bundle.

    Return one message Bundle to use as the canonical structure.
    """
    if (
        template.get("resourceType") == "Bundle"
        and template.get("type") == "message"
    ):
        return template

    if (
        template.get("resourceType") == "Bundle"
        and template.get("type") == "batch"
    ):
        if not template.get("entry"):
            raise ValueError("Template batch Bundle contains no entries.")

        message = template["entry"][0].get("resource", {})

        if (
            message.get("resourceType") != "Bundle"
            or message.get("type") != "message"
        ):
            raise ValueError(
                "First template entry is not a FHIR message Bundle."
            )

        return message

    raise ValueError(
        "Template must be a batch Bundle or message Bundle."
    )


def remap_uuid_graph(obj: object) -> object:
    """
    Give every UUID-based resource in the copied template a fresh UUID and
    update all matching urn:uuid references/fullUrls.
    """
    old_to_new: dict[str, str] = {}

    def collect(value: object) -> None:
        if isinstance(value, dict):
            resource_id = value.get("id")

            if isinstance(resource_id, str):
                try:
                    uuid.UUID(resource_id)
                    old_to_new.setdefault(
                        resource_id,
                        str(uuid.uuid4()),
                    )
                except ValueError:
                    pass

            for child in value.values():
                collect(child)

        elif isinstance(value, list):
            for child in value:
                collect(child)

    collect(obj)

    def replace(value: object) -> object:
        if isinstance(value, dict):
            output = {}

            for key, child in value.items():
                if (
                    key == "id"
                    and isinstance(child, str)
                    and child in old_to_new
                ):
                    output[key] = old_to_new[child]

                elif (
                    isinstance(child, str)
                    and child.startswith("urn:uuid:")
                    and child[9:] in old_to_new
                ):
                    output[key] = (
                        "urn:uuid:" + old_to_new[child[9:]]
                    )

                else:
                    output[key] = replace(child)

            return output

        if isinstance(value, list):
            return [replace(child) for child in value]

        return value

    return replace(obj)


def profile_suffix(resource: dict) -> str | None:
    profiles = (
        resource.get("meta", {}).get("profile", [])
    )

    if not profiles:
        return None

    return profiles[0].split("/")[-1]


def get_document_bundle(message: dict) -> dict:
    for entry in message.get("entry", []):
        resource = entry.get("resource", {})

        if (
            resource.get("resourceType") == "Bundle"
            and resource.get("type") == "document"
        ):
            return resource

    raise ValueError(
        "Message template does not contain a document Bundle."
    )


def get_resource_by_profile(
    document: dict,
    profile_name: str,
) -> dict:
    for entry in document.get("entry", []):
        resource = entry.get("resource", {})

        if profile_suffix(resource) == profile_name:
            return resource

    raise ValueError(
        f"Required template profile not found: {profile_name}"
    )


def get_parameters(message: dict) -> dict:
    for entry in message.get("entry", []):
        resource = entry.get("resource", {})

        if resource.get("resourceType") == "Parameters":
            return resource

    raise ValueError("Parameters resource not found.")


def get_message_header(message: dict) -> dict:
    for entry in message.get("entry", []):
        resource = entry.get("resource", {})

        if resource.get("resourceType") == "MessageHeader":
            return resource

    raise ValueError("MessageHeader resource not found.")


# ============================================================
# FHIR VALUE UPDATERS
# ============================================================

def set_partial_date(
    resource: dict,
    field_name: str,
    year: int,
    month: int,
    day: int,
) -> None:
    """
    Update Year/Month/Day within an existing VRDR PartialDate or
    PartialDateTime extension without changing the template's shape.
    """
    outer_extensions = (
        resource.get(field_name, {}).get("extension", [])
    )

    if not outer_extensions:
        raise ValueError(
            f"Template missing {field_name} extension."
        )

    nested = outer_extensions[0].get("extension", [])

    for item in nested:
        url = item.get("url", "")

        if url.endswith("Date-Year"):
            item["valueUnsignedInt"] = year

        elif url.endswith("Date-Month"):
            item["valueUnsignedInt"] = month

        elif url.endswith("Date-Day"):
            item["valueUnsignedInt"] = day


def split_street(address: str) -> tuple[str, str]:
    """
    Split "8359 Example Street" into ("8359", "Example Street")
    for the existing VRDR address extension structure.
    """
    match = re.match(r"^\s*(\d+)\s+(.*)$", address)

    if match:
        return match.group(1), match.group(2)

    return "1", address or "Synthetic Street"


def set_death_location_address(
    location: dict,
    record: dict[str, str],
) -> None:
    location["name"] = (
        record["por_name"] or "Synthetic Facility"
    )

    address = location.get("address")

    if not isinstance(address, dict):
        raise ValueError(
            "Template death location does not contain an address object."
        )

    address["line"] = [
        record["por_addr"] or "1 Synthetic Street"
    ]
    address["city"] = (
        record["por_city"] or "Synthetic City"
    )
    address["state"] = (
        record["por_state"] or "MO"
    )
    address["country"] = "US"

    # Preserve the accepted template shape. The 245-char source does not
    # contain ZIP, so use a clearly synthetic placeholder if needed.
    if "postalCode" in address:
        address["postalCode"] = (
            record["por_zip"] or "00000"
        )

    street_number, street_name = split_street(
        record["por_addr"]
    )

    for extension in address.get("extension", []):
        url = extension.get("url", "")

        if url.endswith("StreetNumber"):
            extension["valueString"] = street_number

        elif url.endswith("StreetName"):
            extension["valueString"] = street_name


# ============================================================
# BUILD ONE MESSAGE FROM THE ACCEPTED TEMPLATE
# ============================================================

def build_message_from_template(
    canonical_message: dict,
    record: dict[str, str],
    generated_at: datetime,
) -> dict:
    message = remap_uuid_graph(
        copy.deepcopy(canonical_message)
    )

    cert_int, cert6 = numeric_certno(
        record["certno"]
    )
    aux_id = synthetic_auxiliary_id(cert_int)

    death_parts = parse_yyyymmdd(
        record["deathdate_yyyymmdd"]
    )
    birth_parts = parse_yyyymmdd(
        record["dob_yyyymmdd"]
    )

    if death_parts is None:
        raise ValueError(
            f"Invalid death date for {record['certno']}: "
            f"{record['deathdate_source']!r}"
        )

    death_year, death_month, death_day = death_parts
    death_iso = (
        f"{death_year:04d}-"
        f"{death_month:02d}-"
        f"{death_day:02d}"
    )

    generated_iso = generated_at.isoformat()
    generated_date = generated_at.date().isoformat()

    # --------------------------------------------------------
    # Message Bundle
    # --------------------------------------------------------

    message["timestamp"] = generated_iso

    # --------------------------------------------------------
    # Parameters: keep same four-item order as accepted file
    # --------------------------------------------------------

    parameters = get_parameters(message)

    parameters["parameter"] = [
        {
            "name": "cert_no",
            "valueUnsignedInt": cert_int,
        },
        {
            "name": "state_auxiliary_id",
            "valueString": aux_id,
        },
        {
            "name": "death_year",
            "valueUnsignedInt": death_year,
        },
        {
            "name": "jurisdiction_id",
            "valueString": JURISDICTION,
        },
    ]

    # --------------------------------------------------------
    # VRDR document Bundle
    # --------------------------------------------------------

    document = get_document_bundle(message)
    document["timestamp"] = generated_iso

    document["identifier"]["extension"] = [
        {
            "url": (
                f"{VRDR}/AuxiliaryStateIdentifier1"
            ),
            "valueString": aux_id,
        },
        {
            "url": (
                f"{VRDR}/CertificateNumber"
            ),
            "valueString": cert6,
        },
    ]

    document["identifier"]["value"] = (
        f"{death_year}{JURISDICTION}{cert6}"
    )

    # --------------------------------------------------------
    # Composition
    # --------------------------------------------------------

    composition = get_resource_by_profile(
        document,
        "vrdr-death-certificate",
    )

    composition["date"] = generated_date

    if composition.get("attester"):
        composition["attester"][0]["time"] = death_iso

    # --------------------------------------------------------
    # Patient / Decedent
    # --------------------------------------------------------

    patient = get_resource_by_profile(
        document,
        "vrdr-decedent",
    )

    sex_code, sex_display = sex_coding(
        record["sex"]
    )

    for extension in patient.get("extension", []):
        if extension.get("url", "").endswith(
            "NVSS-SexAtDeath"
        ):
            coding = (
                extension["valueCodeableConcept"]
                ["coding"][0]
            )
            coding["code"] = sex_code
            coding["display"] = sex_display

    if patient.get("name"):
        patient["name"][0]["family"] = record["lname"]

        # Keep same two-element given[] shape as the accepted template.
        patient["name"][0]["given"] = [
            record["fname"],
            "Synthetic",
        ]

    if birth_parts:
        birth_year, birth_month, birth_day = birth_parts

        set_partial_date(
            patient,
            "_birthDate",
            birth_year,
            birth_month,
            birth_day,
        )

    # Explicitly keep SSN as synthetic placeholder because the accepted
    # template contains this structure and the reduced source has no SSN.
    for identifier in patient.get("identifier", []):
        if identifier.get("system") == (
            "http://hl7.org/fhir/sid/us-ssn"
        ):
            identifier["value"] = "000000000"

    # --------------------------------------------------------
    # Death certification Procedure
    # --------------------------------------------------------

    certification = get_resource_by_profile(
        document,
        "vrdr-death-certification",
    )
    certification["performedDateTime"] = death_iso

    # --------------------------------------------------------
    # Death Date Observation
    # --------------------------------------------------------

    death_date = get_resource_by_profile(
        document,
        "vrdr-death-date",
    )

    set_partial_date(
        death_date,
        "_valueDateTime",
        death_year,
        death_month,
        death_day,
    )

    # --------------------------------------------------------
    # Death location
    # --------------------------------------------------------

    death_location = get_resource_by_profile(
        document,
        "vrdr-death-location",
    )

    set_death_location_address(
        death_location,
        record,
    )

    # --------------------------------------------------------
    # Cause of death Part I scaffold
    # --------------------------------------------------------

    cause_part1 = get_resource_by_profile(
        document,
        "vrdr-cause-of-death-part1",
    )

    cause_part1["valueCodeableConcept"]["text"] = (
        "Synthetic coded cause "
        + (record["cause"] or "UNK")
    )

    # --------------------------------------------------------
    # Automated underlying cause
    # --------------------------------------------------------

    underlying = get_resource_by_profile(
        document,
        "vrdr-automated-underlying-cause-of-death",
    )

    underlying["valueCodeableConcept"]["coding"][0]["code"] = (
        record["cause"] or "UNK"
    )

    # --------------------------------------------------------
    # Age at death: compute instead of retaining template age
    # --------------------------------------------------------

    try:
        age_resource = get_resource_by_profile(
            document,
            "vrdr-decedent-age",
        )

        age = calculate_age(
            birth_parts,
            death_parts,
        )

        if age is not None:
            age_resource["valueQuantity"]["value"] = age

    except ValueError:
        # Should not happen with the accepted 24-resource template,
        # but do not fail solely on this optional update.
        pass

    # --------------------------------------------------------
    # Keep generic synthetic scaffold values explicitly synthetic
    # --------------------------------------------------------

    certifier = get_resource_by_profile(
        document,
        "vrdr-certifier",
    )
    if certifier.get("name"):
        certifier["name"][0]["family"] = "Certifier"
        certifier["name"][0]["given"] = [
            "Synthetic",
            "T",
        ]

    try:
        disposition = get_resource_by_profile(
            document,
            "vrdr-disposition-location",
        )
        disposition["name"] = (
            "Synthetic Disposition Site"
        )
    except ValueError:
        pass

    try:
        funeral_home = get_resource_by_profile(
            document,
            "vrdr-funeral-home",
        )
        funeral_home["name"] = (
            "Synthetic Funeral Home"
        )
    except ValueError:
        pass

    # --------------------------------------------------------
    # MessageHeader
    # --------------------------------------------------------

    header = get_message_header(message)

    if "source" not in header:
        header["source"] = {}

    header["source"]["endpoint"] = SOURCE_ENDPOINT

    return message


# ============================================================
# VALIDATION HELPERS
# ============================================================

def structure_shape(value: object) -> object:
    """
    Compare JSON STRUCTURE, not values.

    Dict keys and list lengths must match the accepted template.
    """
    if isinstance(value, dict):
        return {
            key: structure_shape(child)
            for key, child in value.items()
        }

    if isinstance(value, list):
        return [
            structure_shape(child)
            for child in value
        ]

    return type(value).__name__


def unresolved_uuid_references(
    value: object,
) -> list[str]:
    ids: set[str] = set()
    refs: list[str] = []

    def walk(child: object) -> None:
        if isinstance(child, dict):
            resource_id = child.get("id")

            if isinstance(resource_id, str):
                ids.add(resource_id)

            for item in child.values():
                if (
                    isinstance(item, str)
                    and item.startswith("urn:uuid:")
                ):
                    refs.append(item[9:])

                walk(item)

        elif isinstance(child, list):
            for item in child:
                walk(item)

    walk(value)

    return [
        ref
        for ref in refs
        if ref not in ids
    ]


def verify_required_template_structure(
    canonical_message: dict,
) -> None:
    document = get_document_bundle(
        canonical_message
    )

    expected_profiles = {
        "vrdr-death-certificate",
        "vrdr-decedent",
        "vrdr-certifier",
        "vrdr-death-certification",
        "vrdr-death-date",
        "vrdr-decedent-age",
        "vrdr-death-location",
        "vrdr-cause-of-death-part1",
        "vrdr-automated-underlying-cause-of-death",
    }

    actual_profiles = {
        profile_suffix(entry.get("resource", {}))
        for entry in document.get("entry", [])
    }

    missing = expected_profiles - actual_profiles

    if missing:
        raise ValueError(
            "Template is missing expected profiles: "
            + ", ".join(sorted(missing))
        )

    if len(document.get("entry", [])) != 24:
        raise ValueError(
            "The supplied accepted template does not have "
            "the expected 24-resource document structure."
        )


# ============================================================
# CONVERT COMPLETE FILE
# ============================================================

def convert_sdf_to_core_aligned_fhir(
    input_file: Path,
    output_file: Path,
) -> None:

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input file not found:\n{input_file}"
        )


    template = load_embedded_core_template()

    canonical_message = get_template_message(
        template
    )

    verify_required_template_structure(
        canonical_message
    )

    raw_lines = input_file.read_text(
        encoding="cp1252"
    ).splitlines()

    lines = [
        line
        for line in raw_lines
        if line.strip()
    ]

    if not lines:
        raise ValueError(
            "Input file contains no records."
        )

    records = [
        parse_line(line)
        for line in lines
    ]

    generated_at = (
        datetime.now().astimezone()
    )

    output_entries = []

    for record_number, record in enumerate(
        records,
        start=1,
    ):
        message = build_message_from_template(
            canonical_message,
            record,
            generated_at,
        )

        # Structural check against the accepted template message.
        if structure_shape(message) != structure_shape(
            canonical_message
        ):
            raise ValueError(
                f"Record {record_number}: generated JSON shape "
                "does not match accepted template."
            )

        broken = unresolved_uuid_references(
            message
        )

        if broken:
            raise ValueError(
                f"Record {record_number}: unresolved UUID references: "
                + ", ".join(broken)
            )

        output_entries.append(
            {
                "fullUrl": (
                    "urn:uuid:" + message["id"]
                ),
                "resource": message,
            }
        )

    output_bundle = {
        "resourceType": "Bundle",
        "type": "batch",
        "timestamp": generated_at.isoformat(),
        "total": len(output_entries),
        "entry": output_entries,
    }

    output_file.write_text(
        json.dumps(
            output_bundle,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=" * 64)
    print("FHIRBridge-MO CORE-template-aligned conversion complete")
    print("=" * 64)
    print(f"Input:       {input_file}")
    print("Template:    embedded in Python script")
    print(f"Records:     {len(records)}")
    print(f"Output:      {output_file}")
    print()
    print("Checks:")
    print("  [PASS] Accepted 24-resource template found")
    print("  [PASS] Generated message shape matches accepted template")
    print("  [PASS] No unresolved internal UUID references")
    print()
    print(
        "Next step: test this GENERATED output in the CORE TEST "
        "environment. Successful parsing does not by itself establish "
        "VRDR conformance."
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    convert_sdf_to_core_aligned_fhir(
        INPUT_FILE,
        OUTPUT_FILE,
    )
