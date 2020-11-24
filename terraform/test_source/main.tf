resource "tfe_organization" "migration-test-org" {
  name  = var.org_name
}

# Create users

# Create teams
resource "tfe_team" "migration-test-foo" {
  name         = "migration-test-foo"
  organization = var.org_name
}

resource "tfe_team" "migration-test-bar" {
  name         = "migration-test-bar"
  organization = var.org_name
}

# Create SSH Keys
resource "tfe_ssh_key" "test" {
  name         = "migration-test-ssh-key"
  organization = var.org_name
  key          = "-----BEGIN RSA PRIVATE KEY-----\n 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\n -----END RSA PRIVATE KEY-----"
}

# Create Agent Pools
resource "tfe_agent_pool" "test-agent-pool" {
  name         = "migration-test-agent-pool"
  organization = tfe_organization.migration-test-org.id
}

# Create Workspaces w/ VCS

# Create Workspaces w/o VCS

# Add variables to workspaces

# Add sensitive variables to workspaces

# Add env variables to workspaces

# Add sensitive env variables to workspaces

# Create state versions

# Create run triggers

# Create notification configs

# Set up team access to workspaces

# Create policies w/ VCS

# Create policies w/o VCS

# Create policy sets w/ VCS

# Create policy sets w/o VCS

# Create policy sets params

# Create sensitive policy sets params

# Create registry modules
