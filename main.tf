module "catalog_access" {
  source = "https://github.com/Pradeep421/databricks-catalog-access-main.git"

  catalog_url = var.catalog_url
  owner       = var.owner
  tag         = var.tag
  catalog     = var.catalog
}
