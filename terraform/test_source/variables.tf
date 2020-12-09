variable "hostname" {
    type = string
    default = "http://app.terraform.io"
}

variable "org_name" {
    type = string
}

variable "prefix" {
    type = string
    default = "migration"
}

variable "working_directory" {
    type = string
    default = ""
}

variable "oauth_token_id" {
    type = string
}

variable "repo_identifier" {
    type = string
}

variable "email" {
    type = string
}