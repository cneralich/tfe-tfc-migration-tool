import os
import argparse
import json
from terrasnek.api import TFC
from tfc_migrate import \
    workspaces, teams, policies, policy_sets, registry_modules, \
        ssh_keys, config_versions, notification_configs, team_access, \
            agent_pools, workspace_vars, run_triggers, state_versions, \
                policy_set_params, org_memberships, registry_module_versions


DEFAULT_VCS_FILE = "vcs.json"

# Source Org
TFE_TOKEN_SOURCE = os.getenv("TFE_TOKEN_SOURCE", None)
TFE_URL_SOURCE = os.getenv("TFE_URL_SOURCE", None)
TFE_ORG_SOURCE = os.getenv("TFE_ORG_SOURCE", None)

# Target Org
TFE_TOKEN_TARGET = os.getenv("TFE_TOKEN_TARGET", None)
TFE_URL_TARGET = os.getenv("TFE_URL_TARGET", None)
TFE_ORG_TARGET = os.getenv("TFE_ORG_TARGET", None)

# NOTE: this is parsed in the main function
TFE_VCS_CONNECTION_MAP = None


def confirm_delete_resource_type(resource_type, api):
    answer = ""

    while answer not in ["y", "n"]:
        question_string = \
            "This will destroy all %s in org '%s' (%s). Want to continue? [Y/N]: " \
                % (resource_type, api.get_org(), api.get_url())
        answer = input(question_string).lower()

    return answer == "y"


def handle_output(\
    teams_map, ssh_keys_map, ssh_key_name_map, workspaces_map, \
        workspace_to_ssh_key_map, workspace_to_config_version_upload_map, \
            module_to_module_version_upload_map, policies_map, policy_sets_map, \
                sensitive_policy_set_parameter_data, sensitive_variable_data, \
                    write_to_file=False):

        output_json = {
            "teams_map": teams_map,
            "ssh_keys_map": ssh_keys_map,
            "ssh_key_name_map": ssh_key_name_map,
            "workspaces_map": workspaces_map,
            "workspace_to_ssh_key_map": workspace_to_ssh_key_map,
            "workspace_to_config_version_upload_map": workspace_to_config_version_upload_map,
            "module_to_module_version_upload_map": module_to_module_version_upload_map,
            "policies_map": policies_map,
            "policy_sets_map": policy_sets_map,
            "sensitive_policy_set_parameter_data": sensitive_policy_set_parameter_data,
            "sensitive_variable_data": sensitive_variable_data
        }

        if write_to_file:
            with open("outputs.txt", "w") as f:
                f.write(output_json)
        else:
            print(output_json)

def migrate_sensitive_to_target():
    # TODO: figure out how we want to handle the user inputing sensitive data
    # ssh_keys.migrate_key_files(api_target, ssh_key_name_map, ssh_key_file_path_map)
    # workspace_vars.migrate_sensitive(api_target, sensitive_variable_data_map)
    # policy_set_params.migrate_sensitive(api_target, sensitive_policy_set_parameter_data_map)
    pass

def migrate_to_target(api_source, api_target, write_to_file, migrate_all_state):
    teams_map = teams.migrate(api_source, api_target)

    """
    NOTE: org_memberships.migrate only sends out invites, as such, it's commented out.
    The users must exist in the system ahead of time if you want to use this.
    Lastly, since most customers use SSO, this function isn't terribly useful.
    """
    # org_membership_map = org_memberships.migrate(api_source, api_target, teams_map)

    ssh_keys_map, ssh_key_name_map = ssh_keys.migrate_keys(api_source, api_target)

    agent_pools_map = agent_pools.migrate(api_source, api_target)

    workspaces_map, workspace_to_ssh_key_map = \
        workspaces.migrate(api_source, api_target, TFE_VCS_CONNECTION_MAP, agent_pools_map)

    if migrate_all_state:
        state_versions.migrate_all(api_source, api_target, workspaces_map)
    else:
        state_versions.migrate_current(api_source, api_target, workspaces_map)

    sensitive_variable_data = workspace_vars.migrate(api_source, api_target, workspaces_map)

    workspaces.migrate_ssh_keys( \
        api_source, api_target, workspaces_map, workspace_to_ssh_key_map, ssh_keys_map)

    run_triggers.migrate(api_source, api_target, workspaces_map)

    notification_configs.migrate(api_source, api_target, workspaces_map)

    team_access.migrate(api_source, api_target, workspaces_map, teams_map)

    workspace_to_config_version_upload_map = config_versions.migrate( \
        api_source, api_target, workspaces_map)

    # TODO: manage extracting state and publishing tarball
    # config_versions.migrate_config_files(\
    #   api_target, workspace_to_config_version_upload_map, workspace_to_file_path_map)

    # TODO: make sure that non-VCS policies get mapped properly to their policy sets
    policies_map = policies.migrate(api_source, api_target)

    policy_sets_map = policy_sets.migrate(\
        api_source, api_target, TFE_VCS_CONNECTION_MAP, workspaces_map, policies_map)

    # This function returns the information that is needed to publish sensitive
    # variables, but cannot retrieve the values themselves, so those values will
    # have to be updated separately.
    sensitive_policy_set_parameter_data = \
        policy_set_params.migrate(api_source, api_target, policy_sets_map)

    module_to_module_version_upload_map = \
        registry_modules.migrate(api_source, api_target, TFE_VCS_CONNECTION_MAP)

    # TODO: manage extracting module and publishing tarball, this doesn't work.
    # registry_module_versions.migrate_module_version_files(api_source, api_target)

    handle_output(teams_map, ssh_keys_map, ssh_key_name_map, workspaces_map, \
            workspace_to_ssh_key_map, workspace_to_config_version_upload_map, \
                module_to_module_version_upload_map, policies_map, policy_sets_map, \
                    sensitive_policy_set_parameter_data, sensitive_variable_data, \
                        write_to_file=write_to_file)


def delete_all_from_target(api, no_confirmation):
    if no_confirmation or confirm_delete_resource_type("run triggers", api):
        run_triggers.delete_all(api)

    if no_confirmation or confirm_delete_resource_type("workspace variables", api):
        workspace_vars.delete_all(api)

    if no_confirmation or confirm_delete_resource_type("team access", api):
        team_access.delete_all(api)

    if no_confirmation or confirm_delete_resource_type("workspaces", api):
        workspaces.delete_all(api)

    # No need to delete the key files, they get deleted when deleting keys.
    if no_confirmation or confirm_delete_resource_type("SSH keys", api):
        ssh_keys.delete_all_keys(api)

    if no_confirmation or confirm_delete_resource_type("org memberships", api):
        org_memberships.delete_all(api)

    if no_confirmation or confirm_delete_resource_type("teams", api):
        teams.delete_all(api)

    if no_confirmation or confirm_delete_resource_type("policies", api):
        policies.delete_all(api)

    if no_confirmation or confirm_delete_resource_type("policy sets", api):
        policy_sets.delete_all(api)

    if no_confirmation or confirm_delete_resource_type("policy set params", api):
        policy_set_params.delete_all(api)

    if no_confirmation or confirm_delete_resource_type("registry modules", api):
        registry_modules.delete_all(api)

    if no_confirmation or confirm_delete_resource_type("registry module versions", api):
        registry_module_versions.delete_all(api)

    if no_confirmation or confirm_delete_resource_type("agent pools", api):
        agent_pools.delete_all(api)


def main(api_source, api_target, write_to_file, delete_all, no_confirmation, migrate_all_state):

    if delete_all:
        delete_all_from_target(api_target, no_confirmation)
    else:
        migrate_to_target(api_source, api_target, write_to_file, migrate_all_state)


if __name__ == "__main__":
    """
    All migration outputs are written to a .txt file by default
    If you prefer to have these outputs in the terminal,
    set the write_to_file parameter to False
    """
    parser = argparse.ArgumentParser(description='Migrate from TFE/C to TFE/C.')
    parser.add_argument('--vcs-file-path', dest="vcs_file_path", default=DEFAULT_VCS_FILE, \
        help="Path to the VCS JSON file. Defaults to `vcs.json`.")
    parser.add_argument('--write-output', dest="write_output", \
        action="store_true", help="Write output to a file.")
    parser.add_argument('--migrate-all-state', dest="migrate_all_state", action="store_true", \
        help="Migrate all state history workspaces. Default behavior is only current state.")
    parser.add_argument('--delete-all', dest="delete_all", action="store_true", \
        help="Delete all resources from the target API.")
    parser.add_argument('--no-confirmation', dest="no_confirmation", action="store_true", \
        help="If set, don't ask for confirmation before deleting all target resources.")
    args = parser.parse_args()

    api_source = TFC(TFE_TOKEN_SOURCE, url=TFE_URL_SOURCE)
    api_source.set_org(TFE_ORG_SOURCE)

    api_target = TFC(TFE_TOKEN_TARGET, url=TFE_URL_TARGET)
    api_target.set_org(TFE_ORG_TARGET)

    with open(args.vcs_file_path, "r") as f:
        TFE_VCS_CONNECTION_MAP = json.loads(f.read())

    main(api_source, api_target, args.write_output, args.delete_all, \
            args.no_confirmation, args.migrate_all_state)
