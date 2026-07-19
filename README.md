# databricks-catalog-access-submodule

This repo calls the main Databricks catalog access module and keeps the environment-specific tfvars.

## Catalog request flow

1. Open a GitHub issue with the **New catalog request** template.
2. Select the environment, enter the application name, catalog name, owner, tag, AD groups, and SPN/user access.
3. The `Catalog request` workflow validates the request and opens a pull request that creates or updates `tfvars/<env>/<application_name>.tfvars`.
4. Review and merge the pull request.
5. The `Terraform` workflow runs `terraform apply` from `main`.

Required repository secret:

- `DATABRICKS_TOKEN`

For new application files, the Databricks workspace URL comes from the issue form. For existing files, the old `catalog_url` is kept unless the form provides a new value.
