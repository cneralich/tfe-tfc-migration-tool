variable "hostname" {
  type    = string
  default = "http://app.terraform.io"
}

variable "org_name" {
  type = string
}

variable "prefix" {
  type    = string
  default = "migration"
}

variable "oauth_token_id" {
  type = string
}

variable "email" {
  type = string
}

variable "tf_vars" {
  default = {
    "var_one" = "tf_var_value_one",
    "var_two" = "tf_var_value_two"
  }
}

variable "sensitive_tf_vars" {
  default = {
    "sensitive_var_one" = "sensitive_tf_var_value_one",
    "sensitive_var_two" = "sensitive_tf_var_value_two"
  }
}

variable "env_vars" {
  default = {
    "ENV_VAR_ONE" = "env_var_value_one",
    "ENV_VAR_TWO" = "env_var_value_two"
  }
}

variable "sensitive_env_vars" {
  default = {
    "SENSITIVE_ENV_VAR_ONE" = "sensitive_env_var_value_one",
    "SENSITIVE_ENV_VAR_TWO" = "sensitive_env_var_value_two"
  }
}

variable "slack_notification_url" {
    type = string
}

variable "generic_notification_url" {
    type = string
}

variable "github_org_name" {
    type = string
}