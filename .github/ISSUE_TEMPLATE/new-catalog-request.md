---
name: New Catalog Request
about: Request a new Databricks catalog to be created with access controls
title: "[CATALOG REQUEST] "
labels: catalog-request, automation
assignees: 
---

## Catalog Information

### Catalog Name (Required)
**Naming Convention:** Use lowercase letters, numbers, and underscores only (e.g., `team_name_catalog` or `project_name_prod`)

```
Catalog Name: [Enter catalog name here]
```

### Catalog Owner (Required)
The principal who will own this catalog in Databricks

```
Owner: [Enter owner name/email]
```

### Environment Tag (Required)
Tag to identify the environment (e.g., dev, staging, prod)

```
Tag: [dev/staging/prod]
```

---

## Access Control Configuration

### Group-Based Access (Mandatory)
Azure AD groups that need access to this catalog

#### Readers (Required - minimum one reader group)
Groups with read-only access (USE_CATALOG permission)

```
Reader Groups:
- [Enter AD group 1]
- [Enter AD group 2]
```

#### Editors (Optional)
Groups with read and write access (USE_CATALOG, CREATE_SCHEMA, CREATE_VOLUME permissions)

```
Editor Groups:
- [Enter AD group 1]
- [Enter AD group 2]
```

---

### Service Principal Access (Optional)
Service principals (SPNs) that need access to this catalog

#### SPN Readers (Optional)
Service principals with read-only access

```
SPN Readers:
- [Enter SPN 1]
- [Enter SPN 2]
```

#### SPN Editors (Optional)
Service principals with read and write access

```
SPN Editors:
- [Enter SPN 1]
- [Enter SPN 2]
```

---

## Checklist

- [ ] Catalog name follows naming convention (lowercase, numbers, underscores only)
- [ ] At least one reader group is specified
- [ ] All required fields are filled
- [ ] Verified that this catalog name does not already exist
- [ ] Owners and group names are accurate

---

## Additional Notes

```
Add any additional context or notes here (optional)
```
