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
    team_map = migrate_teams(api_original, api_new)
    print('teams migrated')

    ssh_keys_map = migrate_ssh_keys(api_original, api_new)
    print('ssh keys migrated')

    agent_pool_id = migrate_agent_pools(
        api_original, api_new, TFE_ORG_ORIGINAL, TFE_ORG_NEW)
    print('agent pools migrated')

    workspaces_map, workspace_to_ssh_key_map = migrate_workspaces(
        api_original, api_new, TFE_OAUTH_NEW, agent_pool_id)
    print('workspaces migrated')

    #migrate_all_state(api_original, api_new, TFE_ORG_ORIGINAL, workspaces_map)
    migrate_current_state(api_original, api_new,
                          TFE_ORG_ORIGINAL, workspaces_map)
    print('state migrated')

    migrate_workspace_variables(
        api_original, api_new, TFE_ORG_ORIGINAL, workspaces_map)
    print('workspace variables migrated')

    migrate_ssh_keys_to_workspaces(
        api_original, api_new, workspaces_map, workspace_to_ssh_key_map, ssh_keys_map)
    print('workspace ssh keys migrated')

    migrate_workspace_run_triggers(api_original, api_new, workspaces_map)
    print('workspace run triggers migrated')

    migrate_workspace_notifications(api_original, api_new, workspaces_map)
    print('workspace notifications migrated')

    migrate_workspace_team_access(
        api_original, api_new, workspaces_map, team_map)
    print('workspace team access migrated')

    workspace_to_configuration_version_map = migrate_configuration_versions(
        api_original, api_new, workspaces_map)
    print('workspace configuration versions migrated')

    #migrate_configuration_files(api_new, workspace_to_configuration_version_map, workspace_to_file_path_map)
    # print('workspace configuration files uploades)

    policies_map = migrate_policies(
        api_original, api_new, TFE_TOKEN_ORIGINAL, TFE_URL_ORIGINAL)
    print('policies migrated')

    policy_sets_map = migrate_policy_sets(
        api_original, api_new, TFE_OAUTH_NEW, workspaces_map, policies_map)
    print('policy sets migrated')

    migrate_policy_set_parameters(api_original, api_new, policy_sets_map)
    print('policy set parameters migrated')

    migrate_registry_modules(api_original, api_new,
                             TFE_ORG_ORIGINAL, TFE_OAUTH_NEW)
    print('registry modules migrated')

    print('\n')
    print('MIGRATION MAPS:')
    print('team_map:', team_map)
    print('\n')
    print('ssh_keys_map:', ssh_keys_map)
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
