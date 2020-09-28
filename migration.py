import os
from terrasnek.api import TFC
from functions import *

# SOURCE ORG
TFE_TOKEN_ORIGINAL = os.getenv("TFE_TOKEN_ORIGINAL", None)
TFE_URL_ORIGINAL = os.getenv("TFE_URL_ORIGINAL", None)
TFE_ORG_ORIGINAL = os.getenv("TFE_ORG_ORIGINAL", None)

api_original = TFC(TFE_TOKEN_ORIGINAL, url=TFE_URL_ORIGINAL)
api_original.set_org(TFE_ORG_ORIGINAL)

# NEW ORG
TFE_TOKEN_NEW = os.getenv("TFE_TOKEN_NEW", None)
TFE_URL_NEW = os.getenv("TFE_URL_NEW", None)
TFE_ORG_NEW = os.getenv("TFE_ORG_NEW", None)
TFE_OAUTH_NEW = os.getenv("TFE_OAUTH_NEW", None)

api_new = TFC(TFE_TOKEN_NEW, url=TFE_URL_NEW)
api_new.set_org(TFE_ORG_NEW)


if __name__ == "__main__":
    teams_map = migrate_teams(api_original, api_new)
    print('teams successfully migrated')

    # migrate_organization_memberships(api_original, api_new, teams_map)
    # print('organization memberships successfully migrated')

    ssh_keys_map, ssh_key_name_map = migrate_ssh_keys(api_original, api_new)
    print('ssh keys successfully migrated')

    # migrate_ssh_key_files(api_new, ssh_key_name_map, ssh_key_file_path_map)
    # print('ssh key files successfully migrated')

    agent_pool_id = migrate_agent_pools(
        api_original, api_new, TFE_ORG_ORIGINAL, TFE_ORG_NEW)
    print('agent pools successfully migrated')

    workspaces_map, workspace_to_ssh_key_map = migrate_workspaces(
        api_original, api_new, TFE_OAUTH_NEW, agent_pool_id)
    print('workspaces successfully migrated')

    # migrate_all_state(api_original, api_new, TFE_ORG_ORIGINAL, workspaces_map)
    migrate_current_state(api_original, api_new,
                          TFE_ORG_ORIGINAL, workspaces_map)
    print('state successfully migrated')

    # Note: if you wish to generate a map of Sensitive variables that can be used to update
    # those values via the migrate_workspace_sensitive_variables method, pass True as the final argument (defaults to False)
    sensitive_variable_data = migrate_workspace_variables(
        api_original, api_new, TFE_ORG_ORIGINAL, workspaces_map)
    print('workspace variables successfully migrated')

    # migrate_workspace_sensitive_variables(api_new, sensitive_variable_data_map)
    # print('workspace sensitive variables successfully migrated')

    migrate_ssh_keys_to_workspaces(
        api_original, api_new, workspaces_map, workspace_to_ssh_key_map, ssh_keys_map)
    print('workspace ssh keys successfully migrated')

    migrate_workspace_run_triggers(api_original, api_new, workspaces_map)
    print('workspace run triggers successfully migrated')

    migrate_workspace_notifications(api_original, api_new, workspaces_map)
    print('workspace notifications successfully migrated')

    migrate_workspace_team_access(
        api_original, api_new, workspaces_map, teams_map)
    print('workspace team access successfully migrated')

    workspace_to_configuration_version_map = migrate_configuration_versions(
        api_original, api_new, workspaces_map)
    print('workspace configuration versions successfully migrated')

    # migrate_configuration_files(api_new, workspace_to_configuration_version_map, workspace_to_file_path_map)
    # print('workspace configuration files successfully migrated)

    policies_map = migrate_policies(
        api_original, api_new, TFE_TOKEN_ORIGINAL, TFE_URL_ORIGINAL)
    print('policies successfully migrated')

    policy_sets_map = migrate_policy_sets(
        api_original, api_new, TFE_OAUTH_NEW, workspaces_map, policies_map)
    print('policy sets successfully migrated')

    # Note: if you wish to generate a map of Sensitive policy set parameters that can be used to update
    # those values via the migrate_policy_set_sensitive_variables method, pass True as the final argument (defaults to False)
    sensitive_policy_set_parameter_data = migrate_policy_set_parameters(
        api_original, api_new, policy_sets_map)
    print('policy set parameters successfully migrated')

    # migrate_policy_set_sensitive_parameters(api_new, sensitive_policy_set_parameter_data_map)
    # print('policy set sensitive parameters successfully migrated')

    migrate_registry_modules(api_original, api_new,
                             TFE_ORG_ORIGINAL, TFE_OAUTH_NEW)
    print('registry modules successfully migrated')

    print('\n')
    print('MIGRATION MAPS:')
    print('teams_map:', teams_map)
    print('\n')
    print('ssh_keys_map:', ssh_keys_map)
    print('\n')
    print('ssh_keys_map:', ssh_key_name_map)
    print('\n')
    print('workspaces_map:', workspaces_map)
    print('\n')
    print('workspace_to_ssh_key_map:', workspace_to_ssh_key_map)
    print('\n')
    print('workspace_to_configuration_version_map:',
          workspace_to_configuration_version_map)
    print('\n')
    print('policies_map:', policies_map)
    print('\n')
    print('policy_sets_map:', policy_sets_map)
    print('\n')
    print('sensitive_policy_set_parameter_data:',
          sensitive_policy_set_parameter_data)
    print('\n')
    print('sensitive_variable_data:', sensitive_variable_data)
