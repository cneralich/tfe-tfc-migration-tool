provider "tfe" {
  hostname = var.hostname
}

# Pull User Data
data "tfe_organization_membership" "migration-test-user" {
  organization  = var.org_name
  email = var.email
}

# Create teams
resource "tfe_team" "migration-test-team-one" {
  name         = "${var.prefix}-test-team-one"
  organization = var.org_name
}

resource "tfe_team" "migration-test-team-two" {
  name         = "${var.prefix}-test-team-two"
  organization = var.org_name
}

# Create SSH Keys
resource "tfe_ssh_key" "migration-test-ssh-key" {
  name         = "${var.prefix}-test-ssh-key"
  organization = var.org_name
  key          = "-----BEGIN RSA PRIVATE KEY-----\n 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\n -----END RSA PRIVATE KEY-----"
}

# Create Agent Pools
resource "tfe_agent_pool" "migration-test-agent-pool" {
  name         = "${var.prefix}-test-agent-pool"
  organization = var.org_name
}

# Create Workspaces w/ VCS
resource "tfe_workspace" "migration-test-workspace-vcs" {
  name         = "${var.prefix}-test-workspace-vcs"
  organization = var.org_name
  auto_apply     = true

  working_directory = var.working_directory
  vcs_repo {
    identifier     = var.repo_identifier
    oauth_token_id = var.oauth_token_id
  }
}

# Create Workspaces w/o VCS
resource "tfe_workspace" "migration-test-workspace-api" {
  name         = "${var.prefix}-test-workspace-api"
  organization = var.org_name
}

# Create Workspace w/ Agent Pool
resource "tfe_workspace" "migration-test-workspace-agent-pool" {
  name           = "${var.prefix}-test-workspace-agent-pool"
  organization   = var.org_name
  agent_pool_id  = tfe_agent_pool.migration-test-agent-pool.id
  execution_mode = "agent"
  ssh_key_id     = tfe_ssh_key.migration-test-ssh-key.id

  working_directory = var.working_directory
  vcs_repo {
    identifier     = var.repo_identifier
    oauth_token_id = var.oauth_token_id
  }
}

# Add variables to workspaces
resource "tfe_variable" "non-sensitive-tf-vars-vcs" {
  for_each     = var.tf_vars
  key          = each.key
  value        = each.value
  category     = "terraform"
  sensitive    = false
  workspace_id = tfe_workspace.migration-test-workspace-vcs.id
}

resource "tfe_variable" "non-sensitive-tf-vars-api" {
  for_each     = var.tf_vars
  key          = each.key
  value        = each.value
  category     = "terraform"
  sensitive    = false
  workspace_id = tfe_workspace.migration-test-workspace-api.id
}

resource "tfe_variable" "non-sensitive-tf-vars-agent" {
  for_each     = var.tf_vars
  key          = each.key
  value        = each.value
  category     = "terraform"
  sensitive    = false
  workspace_id = tfe_workspace.migration-test-workspace-agent-pool.id
}

# Add sensitive variables to workspaces
resource "tfe_variable" "sensitive-tf-vars-vcs" {
  for_each     = var.sensitive_tf_vars
  key          = each.key
  value        = each.value
  category     = "terraform"
  sensitive    = true
  workspace_id = tfe_workspace.migration-test-workspace-vcs.id
}

resource "tfe_variable" "sensitive-tf-vars-api" {
  for_each     = var.sensitive_tf_vars
  key          = each.key
  value        = each.value
  category     = "terraform"
  sensitive    = true
  workspace_id = tfe_workspace.migration-test-workspace-api.id
}

resource "tfe_variable" "sensitive-tf-vars-agent" {
  for_each     = var.sensitive_tf_vars
  key          = each.key
  value        = each.value
  category     = "terraform"
  sensitive    = true
  workspace_id = tfe_workspace.migration-test-workspace-agent-pool.id
}

# Add env variables to workspaces
resource "tfe_variable" "env-vars-vcs" {
  for_each     = var.env_vars
  key          = each.key
  value        = each.value
  category     = "env"
  sensitive    = false
  workspace_id = tfe_workspace.migration-test-workspace-vcs.id
}

resource "tfe_variable" "env-vars-api" {
  for_each     = var.env_vars
  key          = each.key
  value        = each.value
  category     = "env"
  sensitive    = false
  workspace_id = tfe_workspace.migration-test-workspace-api.id
}

resource "tfe_variable" "env-vars-agent" {
  for_each     = var.env_vars
  key          = each.key
  value        = each.value
  category     = "env"
  sensitive    = false
  workspace_id = tfe_workspace.migration-test-workspace-agent-pool.id
}

# Add sensitive env variables to workspaces
resource "tfe_variable" "sensitive-env-vars-vcs" {
  for_each     = var.sensitive_env_vars
  key          = each.key
  value        = each.value
  category     = "env"
  sensitive    = true
  workspace_id = tfe_workspace.migration-test-workspace-vcs.id
}

resource "tfe_variable" "sensitive-env-vars-api" {
  for_each     = var.sensitive_env_vars
  key          = each.key
  value        = each.value
  category     = "env"
  sensitive    = true
  workspace_id = tfe_workspace.migration-test-workspace-api.id
}

resource "tfe_variable" "sensitive-env-vars-agent" {
  for_each     = var.sensitive_env_vars
  key          = each.key
  value        = each.value
  category     = "env"
  sensitive    = true
  workspace_id = tfe_workspace.migration-test-workspace-agent-pool.id
}

# Create state versions

# Create run triggers
resource "tfe_run_trigger" "api-to-agent" {
  workspace_id  = tfe_workspace.migration-test-workspace-agent-pool.id
  sourceable_id = tfe_workspace.migration-test-workspace-api.id
}

resource "tfe_run_trigger" "vcs-to-agent" {
  workspace_id  = tfe_workspace.migration-test-workspace-agent-pool.id
  sourceable_id = tfe_workspace.migration-test-workspace-vcs.id
}

# Create run triggers
resource "tfe_run_trigger" "api-to-vcs" {
  workspace_id  = tfe_workspace.migration-test-workspace-vcs.id
  sourceable_id = tfe_workspace.migration-test-workspace-api.id
}

# Create email notification configs
resource "tfe_notification_configuration" "email-notification" {
  name                  = "${var.prefix}-test-notification-email"
  enabled               = true
  destination_type      = "email"
  email_user_ids        = [data.tfe_organization_membership.migration-test-user.user_id]
  triggers              = ["run:created", "run:planning", "run:errored"]
  workspace_id = tfe_workspace.migration-test-workspace-vcs.id
}

# Create Slack notification configs
resource "tfe_notification_configuration" "slack-notification" {
  name                      = "${var.prefix}-test-notification-slack"
  enabled                   = true
  destination_type          = "slack"
  triggers                  = ["run:created", "run:planning", "run:errored"]
  url                       = var.slack_notification_url
  workspace_id     = tfe_workspace.migration-test-workspace-api.id
}

# Create generic endpoint notification configs
resource "tfe_notification_configuration" "generic-notification" {
  name                      = "${var.prefix}-test-notification-generic"
  enabled                   = true
  destination_type          = "generic"
  triggers                  = ["run:created", "run:planning", "run:errored"]
  url                       = var.generic_notification_url
  workspace_id     = tfe_workspace.migration-test-workspace-agent-pool.id
}

# Set up team access to workspaces

# Create policies w/ VCS

# Create policies w/o VCS

# Create policy sets w/ VCS

# Create policy sets w/o VCS

# Create policy sets params

# Create sensitive policy sets params

# Create registry modules
