# TFC/E Migration Tool

This tool is designed to help automate the migration from one TFE/C Organization to another, whether that’s TFE to TFC, or vice versa.
Currently it only supports 1:1 migrations, but the goal is to support 1:N.

## Steps

### 1. Install the Python Dependencies

```bash
pip3 install terrasnek==0.0.12
```

### 2. Set Required Environment Variables

```bash
# Source organization token, URL, and organization name
export TFE_TOKEN_SOURCE="foo"
export TFE_URL_SOURCE="https://app.terraform.io"
export TFE_ORG_SOURCE="bar"

# Destination organization token, URL, and organization name
export TFE_TOKEN_DESTINATION="foo"
export TFE_URL_DESTINATION="https://app.terraform.io"
export TFE_ORG_DESTINATION="bar"
```

* The Token(s) used above must be either a Team or User Token and have the appropriate level of permissions
* The URL(s) used above must follow a format of `https://app.terraform.io`

### 3. Build the Required TFE_VCS_CONNECTION_MAP

The TFE_VCS_CONNECTION_MAP is a list of dictionaries, each of which maps a `source` VCS OAuth token value to the corresponding `target` VCS OAuth token value, like so:

```
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

* Note that GitHub App connections are not currently supported in this migration tool since those values can not currently be managed via the API.


### 4. Choose Desired Runtime Arguments

Before initiating the migration process, first determine which command line arguments you wish to pass (if any).  The following arguments are currently supported:
* `--vcs-file-path`: this flag allows you to pass a custom file path for your TFE_VCS_CONNECTION_MAP JSON file. If not specified, `vcs.json` will be used by default.
* `--write-output`: this flag allows you to set the desired behavior for handling outputs.  If passed, all outputs will will be written to an `outputs.txt` file.  If not specified, all outputs will appear in the terminal by default.
* `--migrate-all-state`: this flag allows you to set the desired behavior for migrating state versions.  If passed, all version of state will get migrated for all workspaces.  If not specificed, only the current version of state for all workspaces will be migrated by default.


## 5. Perform the Migration

To perform the migration, the following command may be executed (example includes optional arguments):

```bash
python migration.py --vcs-file-path "/path/to/file/vcs.json" --write-output --migrate-all-state
```

For clarity, the command above would result in the use of a custom `TFE_VCS_CONNECTION_MAP` JSON file, the writing of all outputs ot a `outputs.txt` file, and the migration of all state versions for all workspaces.


## Supported Operations

The following migration operations are currently supported:

* [agent_pools.py](tfc_migrate/agent_pools.py)
    * Migrates all agent pools
* [config_versions.py](tfc_migrate/config_versions.py)
    * Migrates the latest configuration version for non-VCS-backed workspaces
    * Includes a helper function to migrate configuration version tarball files for all non-VCS-backed workspaces
* [notification_configs.py](tfc_migrate/notification_configs.py)
    * Migrates all workspace notifications
    * Email Notifications will be migrated, but email address are added based on Username.  If the Usernames do not exist within the target organization at the time the Notifications are migrated, the triggers will still get migrated, but they will need to be updated once the target Users have confirmed their new Accounts.
* [org_memberships.py](tfc_migrate/org_memberships.py)
    * This sends out an invite to join the destination organization to all 'active' members of the source organization (which must be accepted by the User before they're added to the destination organization)
* [policies.py](tfc_migrate/policies.py)
    * Migrates all non-VCS-backed (legacy) Sentinel policies
* [policy_set_params.py](tfc_migrate/policy_set_params.py)
    * Migrates all Sentinel policy set parameters
    * For any parameter marked as `Sensitive`, only key names will be transferred (since values are write only)
    * Includes a helper function to migrate sensitive policy set parameter values for all policy set parameters
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
    * Includes a helper function to migrate all 


### Notes

This migration utility leverages the [Terraform Cloud/Enterprise API](https://www.terraform.io/docs/cloud/api/index.html) and the [terrasnek](https://github.com/dahlke/terrasnek) Python Client for interacting with it.  For security reasons, there are certain Sensitive values that cannot be extracted (ex. Sensitive Variables, Sensitive Policy Set params, and SSH Keys), so those will need to be re-added after the migration is complete (the Keys will, however, be migrated).  For convenience, additional methods have been included to enable Sensitive value migration (Sensitive Variables, Sensitive Policy Set params, and SSH Keys).


## Delete All Target Org Data (Optional)

To help make testing and/or rollback easier, a complete set of delete functions have been included as well.  Similar to the migration process outlined above, these functions can be invoked by passing the following command line arguments:

* `--delete-all`: this flag allows you to invoke the delete functions instead of the migrate functions.  If passed, all data will be deleted from the destination organization. If not specified, the migration functions will be invoked by default.
  * Note: the migration tool is non-destructive in nature and will not (including the delete functions) modify or remove any data from the source organization.
* `--no-confirmation`: this flag allows you to invoke all delete functions if the `--delete-all` flag is also passed.  If the `--delete-all` flag is passed an this is not specified, each delete function will require an explicit Y/N response before executing.

To perform the delete operations, the following command may be executed (example includes optional arguments):

```bash
python migration.py --delete-all --no-confirmation
```

For clarity, the command above would result in the deletion of all data from the target organization without any prompts for explicit confirmation.
