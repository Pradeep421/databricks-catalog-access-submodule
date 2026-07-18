catalog_url = ""
owner       = "dev_owner"
tag         = ""

catalog = {
  ad_catalog = {
    group_name = {
      reader = ["ad_readr_group_dev"]
      editor = ["ad_editr_group_dev"]
    }
    spn = {
      reader = ["dev.user1", "dev.user2"]
    }
  }

  ad_catalog_backup = {
    group_name = {
      reader = ["ad_readr_group_dev"]
      editor = ["ad_editr_group_dev"]
    }
    spn = {
      reader = ["dev.user1", "dev.user2"]
    }
  }
}
