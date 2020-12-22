# TFC/E Migration Tool

This tool is designed to help automate the migration from one TFC/E Organization to another, whether that’s TFE to TFC, or vice versa. It's organization to organization. Currently it only supports 1:1 migrations, but the goal is to support 1:N. Note that the source and target organizations may be running on different versions, and because of that, some API endpoints may not exist in one or the other.

If you're trying to migrate from one TFE installation to another TFE installation, use the [backup-restore functionality](https://www.terraform.io/docs/enterprise/admin/backup-restore.html), not this tool.

## Steps

### 1. Install the Python Dependencies

```bash
pip3 install terrasnek==0.0.15
```

### 2. Set Required Environment Variables

```bash
# Source organization token, URL, and organization name
export TFE_TOKEN_SOURCE="foo"
export TFE_URL_SOURCE="https://app.terraform.io"
export TFE_ORG_SOURCE="bar"

# Target organization token, URL, and organization name
export TFE_TOKEN_TARGET="foo"
export TFE_URL_TARGET="https://app.terraform.io"
export TFE_ORG_TARGET="bar"
```

* The Token(s) used above must be either a team or user token and have the appropriate level of permissions
* The URL(s) used above must follow a format of `https://app.terraform.io`

### 3. Build the Required TFE_VCS_CONNECTION_MAP

The TFE_VCS_CONNECTION_MAP is a list of dictionaries, each of which maps a `source` VCS OAuth token value to the corresponding `target` VCS OAuth token value, like so:

```json
[
    {
    "source": "ot-foo",
    "target": "ot-bar"
    },
    {
    "source": "ot-bar",
    "target": "ot-baz"
    }
]
```

By default, the migration tool will load these values from a file named `vcs.json`, though a custom file path may also be provided via a command line argument at runtime (more on this below).

> **_Note:_** GitHub App connections are not currently supported in this migration tool since those values can not currently be managed via the API.


### 4. Choose Desired Runtime Arguments

Before initiating the migration process, first determine which command line arguments you wish to pass (if any).  The following arguments are currently supported:
* `--vcs-file-path`: this flag allows you to pass a custom file path for your TFE_VCS_CONNECTION_MAP JSON file. If not specified, `vcs.json` will be used by default.
* `--migrate-all-state`: this flag allows you to set the desired behavior for migrating state versions.  If passed, all versions of state will get migrated for all workspaces.  If not specified, only the current version of state for all workspaces will be migrated by default.
* `> outputs.txt`: this allows you to set the desired behavior for handling outputs.  If passed, all outputs will will be written to an `outputs.txt` file (or file name of your choice).  If not specified, all outputs will appear in the terminal by default.


### 5. Perform the Migration

To perform the migration, the following command may be executed (example includes optional arguments):

```bash
python migration.py --vcs-file-path "/path/to/file/vcs.json" --migrate-all-state > outputs.txt
```

For clarity, the command above would result in the use of a custom `TFE_VCS_CONNECTION_MAP` JSON file, the writing of all outputs to an `outputs.txt` file, and the migration of all state versions for all workspaces.


## Supported Operations

The following migration operations are currently supported:

* [agent_pools.py](tfc_migrate/agent_pools.py)
    * Migrates all agent pools
* [config_versions.py](tfc_migrate/config_versions.py)
    * Migrates the latest configuration version for non-VCS-backed workspaces
    * Includes a helper function to migrate configuration version tarball files for all non-VCS-backed workspaces
* [notification_configs.py](tfc_migrate/notification_configs.py)
    * Migrates all workspace notifications
    * Email notifications will be migrated, but email address are added based on Username.  If the Usernames do not exist within the target organization at the time the email notifications are migrated, the triggers will still get migrated, but they will need to be updated once the target users have confirmed their new accounts.
* [org_memberships.py](tfc_migrate/org_memberships.py)
    * This sends out an invite to join the target organization to all 'active' members of the source organization (which must be accepted by the user before they'll be added to the target organization)
* [policies.py](tfc_migrate/policies.py)
    * Migrates all non-VCS-backed (legacy) Sentinel policies
* [policy_set_params.py](tfc_migrate/policy_set_params.py)
    * Migrates all Sentinel policy set parameters
    * For any parameter marked as `Sensitive`, only key names will be transferred (since values are write only)
    * Includes a helper function to migrate sensitive policy set parameter values for all sensitive policy set parameters
* [policy_sets.py](tfc_migrate/policy_sets.py)
    * Migrates all policy sets (for both VCS-backed and non-VCS-backed policies)
* [registry_module_versions.py](tfc_migrate/registry_module_versions.py)
    * Migrates all non-VCS-backed modules
* [registry_modules.py](tfc_migrate/registry_modules.py)
    * Migrates all VCS-backed modules
* [run_triggers.py](tfc_migrate/run_triggers.py)
    * Migrates all workspace run triggers
* [ssh_keys.py](tfc_migrate/run_triggers.py.py)
    * Migrates all org-level SSH keys
    * Only key names will be transferred (since values are write only)
    * Includes a helper function to migrate SSH key files for all SSH keys
* [state_versions.py](tfc_migrate/state_versions.py)
    * Migrates either all state versions for all workspaces or only the current state version for all workspaces
* [team_access.py](tfc_migrate/team_access.py)
    * Migrates team access settings for all workspaces
* [teams.py](tfc_migrate/teams.py)
    * Migrates all teams
* [workspace_ssh_keys.py](tfc_migrate/workspace_ssh_keys.py)
    * Migrate all workspace SSH keys for all workspaces
* [workspace_vars.py](tfc_migrate/workspace_vars.py)
    * Migrates all workspace variables for all workspaces
    * For any variable marked as `Sensitive`, only key names will be transferred (since values are write only)
    * Includes a helper function to migrate sensitive workspace variable values for all workspaces
* [workspaces.py](tfc_migrate/workspaces.py)
    * Migrates all workspaces


## Outputs

Each of the supported operations outlined above are performed by separate functions that are all chained together as part of the overall migration progress. It’s important to highlight that many of the functions are designed to return outputs after completion that are then consumed as required arguments by other subsequently-run functions. As noted above, all of these outputs will be returned in the terminal once the migration is complete, though it's highly recommended to save these outputs to a file (see instructions above) for use in future operations.  For clarity, the following outputs are currently created and returned in JSON format:

* `teams_map`: a dictionary that maps the team ID from the source organization to the corresponding team ID that's created in the target organization
* `ssh_keys_map`: a dictionary that maps the SSH key ID from the source organization to the corresponding SSH key ID that's created in the target organization
* `ssh_key_name_map`: a dictionary that maps the SSH key name from the source organization to the corresponding SSH key ID that's created in the target organization
* `workspaces_map`: a dictionary that maps the workspace ID from the source organization to the corresponding workspace ID that's created in the target organization
* `workspace_to_ssh_key_map`: a dictionary that maps the workspace ID in the source organization to the SSH key ID assigned to that workspace in the source organization
* `policies_map`: a dictionary that maps the policy ID from the source organization to the corresponding policy ID that's created in the target organization
* `policy_sets_map`: a dictionary that maps the policy set ID from the source organization to the corresponding policy set ID that's created in the target organization
* `workspace_to_config_version_upload_url_map`: a dictionary that maps the workspace name in the target organization to the configuration version upload URL for that workspace in the target organization
* `workspace_to_config_version_file_path_map`: a list of dictionaries, each of which contains a workspace name, workspace ID, and file path for the config version files associated with that workspace in the target organization
* `ssh_key_to_file_path_map`: a list of dictionaries, each of which contains a SSH key name and file path for the SSH key files associated with that SSH key in the target organization
* `sensitive_policy_set_parameter_data`: a list of dictionaries, each of which includes a policy set name, policy set ID, policy set parameter ID, policy set parameter key, policy set parameter value, and policy set parameter category for all policy set parameters in the destination organization that were created from policy set parameters in the source organization that were marked as 'sensitive'
* `sensitive_variable_data`: a list of dictionaries, each of which includes a workspace name, workspace ID, variable key, variable value, variable description, variable category, and variable type for all workspace variables in the destination organization that were created from workspace variables in the source organization that were marked as 'sensitive'

> **_IMPORTANT:_** These outputs are needed in order to migrate any sensitive values to the target organization (more on this below), so be sure to save them after the initial migration is complete.


## Sensitive Value and File Migration

This migration tool leverages the [Terraform Cloud/Enterprise API](https://www.terraform.io/docs/cloud/api/index.html) and the [terrasnek](https://github.com/dahlke/terrasnek) Python Client for interacting with it.  For security reasons, there are certain sensitive values and files that cannot be extracted via the API, including sensitive workspace variables, sensitive policy set params, SSH keys, and configuration version files. For that reason, those items will need to be re-added after the initial migration is finished by completing the following steps:

### 1. Update all Missing Values

Once the initial migration is complete and the outputs are generated, save them to a file (if not done initially using the instructions above) and complete the following:

* In the `workspace_to_config_version_file_path_map` list, update the `path_to_config_version_file` value in each dictionary with the correct local file path for that configuration version's configuration version files

* In the `ssh_key_to_file_path_map` list, update the `path_to_ssh_key_file` value in each dictionary with the correct local file path for that SSH key's SSH key files 

* In the `sensitive_policy_set_parameter_data` list, update the `parameter_value` value in each dictionary with the sensitive parameter value for that sensitive parameter key

* In the `sensitive_variable_data` list, update the `variable_value` value in each dictionary with the sensitive parameter value for that sensitive parameter key

> **_NOTE:_** For sensitive workspace variables, sensitive policy set params, and SSH keys, the key name will be migrated to the target organization during the initial migration, but the corresponding key value will not.


### 2. Perform the Migration

To help with this process, a complete set of sensitive value and file migration functions have been included as well. Similar to the migration process outlined above, the functions can be invoked by passing the following command line arguments:

* `--sensitive-data-file-path`: this flag allows you to pass a custom file path for your SENSITIVE_DATA_MAP JSON file. If not specified, `sensitive_data.txt` will be used by default.
* `--migrate-sensitive-data`: this flag allows you to invoke the sensitive value and file migration functions instead of the original migrate functions.

To perform the sensitive value and file migration, the following command may be executed (example includes optional arguments):

```bash
python migration.py --sensitive-data-file-path "/path/to/file/sensitive_data.txt" --migrate-sensitive-data
```

For clarity, the command above would result in the use of a custom `SENSITIVE_DATA_MAP` JSON file and the migration of all sensitive values and files contained within it.


## Delete All Target Organization Data (Optional)

To help make testing and/or rollback easier, a complete set of delete functions have been included as well.  Similar to the migration process outlined above, these functions can be invoked by passing the following command line arguments:

* `--delete-all`: this flag allows you to invoke the delete functions instead of the migrate functions.  If passed, all data will be deleted from the target organization. If not specified, the migration functions will be invoked by default.
* `--no-confirmation`: this flag allows you to invoke all delete functions if the `--delete-all` flag is also passed.  If the `--delete-all` flag is passed and this is not specified, each delete function will require an explicit Y/N response before executing.

To perform the delete operations, the following command may be executed (example includes optional arguments):

```bash
python migration.py --delete-all --no-confirmation
```

For clarity, the command above would result in the deletion of all data from the target organization without any prompts for explicit confirmation.

> **_IMPORTANT:_** This migration tool is non-destructive in nature and will not (including these delete functions) modify or remove any data from the source organization.
