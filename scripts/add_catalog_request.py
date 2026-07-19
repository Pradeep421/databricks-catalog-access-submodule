import argparse
import json
import os
import re
from pathlib import Path


TFVARS_PATH = Path("catalog.auto.tfvars")
NAME_RE = re.compile(r"^[a-z][a-z0-9_]{2,62}$")


def parse_issue_form(body):
    fields = {}
    current = None

    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        if line.startswith("### "):
            current = line[4:].strip()
            fields[current] = []
        elif current is not None:
            fields[current].append(line)

    return {key: clean_value(value) for key, value in fields.items()}


def clean_value(lines):
    useful = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped == "_No response_":
            continue
        useful.append(stripped)
    return "\n".join(useful).strip()


def list_field(value):
    values = []
    for line in value.splitlines():
        item = line.strip().strip(",")
        if item:
            values.append(item)
    return values


def hcl_list(values):
    return "[" + ", ".join(json.dumps(value) for value in values) + "]"


def catalog_exists(tfvars, catalog_name):
    return re.search(rf"^\s*{re.escape(catalog_name)}\s*=", tfvars, re.MULTILINE) is not None


def insert_catalog(tfvars, catalog_name, readers, editors, spn_readers, spn_editors):
    block = [
        f"  {catalog_name} = {{",
        "    group_name = {",
        f"      reader = {hcl_list(readers)}",
        f"      editor = {hcl_list(editors)}",
        "    }",
        "    spn = {",
        f"      reader = {hcl_list(spn_readers)}",
        f"      editor = {hcl_list(spn_editors)}",
        "    }",
        "  }",
    ]

    marker = "\n}\n"
    if marker not in tfvars:
        raise ValueError("Could not find the final catalog map closing brace in catalog.auto.tfvars.")

    return tfvars.rsplit(marker, 1)[0] + "\n\n" + "\n".join(block) + marker


def set_tfvars_string(tfvars, key, value):
    escaped = json.dumps(value)
    return re.sub(rf'^{key}\s*=\s*".*"$', f"{key:<11}= {escaped}", tfvars, flags=re.MULTILINE)


def write_output(name, value):
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with Path(output_path).open("a", encoding="utf-8") as output:
            output.write(f"{name}={value}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-body-file", required=True)
    args = parser.parse_args()

    event = json.loads(Path(args.issue_body_file).read_text(encoding="utf-8-sig"))
    fields = parse_issue_form(event["issue"]["body"])

    catalog_name = fields.get("Catalog name", "").strip()
    owner = fields.get("Owner", "").strip()
    tag = fields.get("Tag", "").strip()
    readers = list_field(fields.get("AD reader groups", ""))
    editors = list_field(fields.get("AD editor groups", ""))
    spn_readers = list_field(fields.get("SPN readers", ""))
    spn_editors = list_field(fields.get("SPN editors", ""))

    if not NAME_RE.match(catalog_name):
        raise ValueError("Catalog name must start with a lowercase letter and contain only lowercase letters, numbers, and underscores.")

    if not owner:
        raise ValueError("Owner is required.")

    if not any([readers, editors, spn_readers, spn_editors]):
        raise ValueError("At least one reader or editor principal is required.")

    tfvars = TFVARS_PATH.read_text(encoding="utf-8")
    if catalog_exists(tfvars, catalog_name):
        raise ValueError(f"Catalog {catalog_name} already exists in catalog.auto.tfvars.")

    tfvars = set_tfvars_string(tfvars, "owner", owner)
    tfvars = set_tfvars_string(tfvars, "tag", tag)
    tfvars = insert_catalog(tfvars, catalog_name, readers, editors, spn_readers, spn_editors)
    TFVARS_PATH.write_text(tfvars, encoding="utf-8")
    write_output("catalog_name", catalog_name)


if __name__ == "__main__":
    main()
