variable "catalog_url" {
  description = "Databricks workspace URL."
  type        = string
}

variable "owner" {
  description = "Catalog owner."
  type        = string
}

variable "tag" {
  description = "Environment or ownership tag value applied to each catalog."
  type        = string
}

variable "catalog" {
  description = "Catalog access map passed to the catalog access module."
  type = map(object({
    group_name = optional(object({
      reader = optional(list(string), [])
      editor = optional(list(string), [])
    }), {})
    spn = optional(object({
      reader = optional(list(string), [])
      editor = optional(list(string), [])
    }), {})
  }))
}
