module "catalog_access" {
  source = "../databricks-catalog-access-main"

  catalog_url = var.catalog_url
  owner       = var.owner
  tag         = var.tag
  catalog     = var.catalog
}
