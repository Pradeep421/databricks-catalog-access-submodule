import argparse
import json
import os
import re
from pathlib import Path


NAME_RE = re.compile(r"^[a-z][a-z0-9_]{2,62}$")
APP_RE = re.compile(r"^[a-z][a-z0-9_-]{1,62}$")
ENV_RE = re.compile(r"^(dev|qa|uat|prod)$")


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


def merge_values(existing, requested):
    merged = list(existing)
    for value in requested:
        if value not in merged:
            merged.append(value)
    return merged


def parse_hcl_list(line):
    match = re.search(r"=\s*(\[.*\])", line)
    if not match:
        return []
    return json.loads(match.group(1))


def parse_catalog_block(block):
    values = {
        "group_readers": [],
        "group_editors": [],
        "spn_readers": [],
        "spn_editors": [],
    }
    section = None

    for raw_line in block.splitlines():
        line = raw_line.strip()
        if line.startswith("group_name = {"):
            section = "group"
        elif line.startswith("spn = {"):
            section = "spn"
        elif line == "}":
            section = None
        elif section == "group" and line.startswith("reader ="):
            values["group_readers"] = parse_hcl_list(line)
        elif section == "group" and line.startswith("editor ="):
            values["group_editors"] = parse_hcl_list(line)
        elif section == "spn" and line.startswith("reader ="):
            values["spn_readers"] = parse_hcl_list(line)
        elif section == "spn" and line.startswith("editor ="):
            values["spn_editors"] = parse_hcl_list(line)

    return values


def catalog_block(catalog_name, readers, editors, spn_readers, spn_editors):
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
    return "\n".join(block)


def find_catalog_block(tfvars, catalog_name):
    match = re.search(rf"^  {re.escape(catalog_name)} = \{{\n", tfvars, re.MULTILINE)
    if not match:
        return None

    depth = 0
    index = match.start()
    while index < len(tfvars):
        char = tfvars[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                if end < len(tfvars) and tfvars[end] == "\n":
                    end += 1
                return match.start(), end
        index += 1

    raise ValueError(f"Catalog {catalog_name} block is not closed correctly.")


def upsert_catalog(tfvars, catalog_name, readers, editors, spn_readers, spn_editors):
    existing = find_catalog_block(tfvars, catalog_name)
    if existing:
        start, end = existing
        current = parse_catalog_block(tfvars[start:end])
        readers = merge_values(current["group_readers"], readers)
        editors = merge_values(current["group_editors"], editors)
        spn_readers = merge_values(current["spn_readers"], spn_readers)
        spn_editors = merge_values(current["spn_editors"], spn_editors)
        block = catalog_block(catalog_name, readers, editors, spn_readers, spn_editors)
        return tfvars[:start] + block + "\n" + tfvars[end:]

    block = catalog_block(catalog_name, readers, editors, spn_readers, spn_editors)
    marker = "\n}\n"
    if marker not in tfvars:
        raise ValueError("Could not find the final catalog map closing brace in the tfvars file.")

    return tfvars.rsplit(marker, 1)[0] + "\n\n" + block + marker


def set_tfvars_string(tfvars, key, value):
    if value == "":
        return tfvars
    escaped = json.dumps(value)
    return re.sub(rf'^{key}\s*=\s*".*"$', f"{key:<11}= {escaped}", tfvars, flags=re.MULTILINE)


def new_tfvars(catalog_url, owner, tag):
    return "\n".join([
        f"catalog_url = {json.dumps(catalog_url)}",
        f"owner       = {json.dumps(owner)}",
        f"tag         = {json.dumps(tag)}",
        "",
        "catalog = {",
        "}",
        "",
    ])


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

    env = fields.get("Environment", "").strip()
    application_name = fields.get("Application name", "").strip()
    catalog_url = fields.get("Catalog URL", "").strip()
    catalog_name = fields.get("Catalog name", "").strip()
    owner = fields.get("Owner", "").strip()
    tag = fields.get("Tag", "").strip()
    readers = list_field(fields.get("AD reader groups", ""))
    editors = list_field(fields.get("AD editor groups", ""))
    spn_readers = list_field(fields.get("SPN readers", ""))
    spn_editors = list_field(fields.get("SPN editors", ""))

    if not ENV_RE.match(env):
        raise ValueError("Environment must be one of: dev, qa, uat, prod.")

    if not APP_RE.match(application_name):
        raise ValueError("Application name must start with a lowercase letter and contain only lowercase letters, numbers, hyphens, and underscores.")

    if not NAME_RE.match(catalog_name):
        raise ValueError("Catalog name must start with a lowercase letter and contain only lowercase letters, numbers, and underscores.")

    if not owner:
        raise ValueError("Owner is required.")

    if not any([readers, editors, spn_readers, spn_editors]):
        raise ValueError("At least one reader or editor principal is required.")

    tfvars_path = Path("tfvars") / env / f"{application_name}.tfvars"
    tfvars_path.parent.mkdir(parents=True, exist_ok=True)

    if tfvars_path.exists():
        tfvars = tfvars_path.read_text(encoding="utf-8")
    else:
        tfvars = new_tfvars(catalog_url, owner, tag)

    tfvars = set_tfvars_string(tfvars, "catalog_url", catalog_url)
    tfvars = set_tfvars_string(tfvars, "owner", owner)
    tfvars = set_tfvars_string(tfvars, "tag", tag)
    tfvars = upsert_catalog(tfvars, catalog_name, readers, editors, spn_readers, spn_editors)
    tfvars_path.write_text(tfvars, encoding="utf-8")
    write_output("env", env)
    write_output("application_name", application_name)
    write_output("catalog_name", catalog_name)
    write_output("tfvars_file", tfvars_path.as_posix())


if __name__ == "__main__":
    main()
