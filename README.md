# databricks-catalog-access-submodule

This repo calls the main Databricks catalog access module and keeps the environment-specific tfvars.

## Catalog request flow

1. Open a GitHub issue with the **New catalog request** template.
2. Enter the catalog name, owner, tag, AD groups, and SPN/user access.
3. The `Catalog request` workflow validates the request and opens a pull request that updates `catalog.auto.tfvars`.
4. Review and merge the pull request.
5. The `Terraform` workflow runs `terraform apply` from `main`.

Required repository secret:

- `DATABRICKS_TOKEN`

The Databricks workspace URL still comes from `catalog_url` in `catalog.auto.tfvars`.
