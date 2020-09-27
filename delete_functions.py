def delete_teams(api_new):
    teams = api_new.teams.list()['data']
    if teams:
        for team in teams:
            if team['attributes']['name'] != "owners":
                api_new.teams.destroy(team['id'])
    return


def delete_ssh_keys(api_new):
    ssh_keys = api_new.ssh_keys.list()["data"]
    if ssh_keys:
        for ssh_key in ssh_keys:
            api_new.ssh_keys.destroy(ssh_key['id'])
    return


def delete_workspaces(api_new):
    workspaces = api_new.workspaces.list()['data']
    if workspaces:
        for workspace in workspaces:
            api_new.workspaces.destroy(workspace['id'])
    return


def delete_variables(api_new):
    workspaces = api_new.workspaces.list()['data']
    for workspace in workspaces:
        variables = api_new.workspace_vars.list(workspace['id'])['data']
        for variable in variables:
            api_new.workspace_vars.destroy(workspace['id'], variable['id'] )
    return


def delete_workspace_notifications(api_new):
    workspaces = api_new.workspaces.list()['data']
    for workspace in workspaces:
        notifications = api_new.notification_configs.list(workspace['id'])['data']
        if notifications:
            for notification in notifications:
                api_new.notification_configs.destroy(notification['id'])
    return


def delete_policies(api_new):
    policies = api_new.policies.list()['data']
    if policies:
        for policy in policies:
            api_new.policies.destroy(policy['id'])
    return


def delete_policy_sets(api_new):
    policy_sets = api_new.policy_sets.list(
        page_size=50, include="policies,workspaces")['data']
    if policy_sets:
        for policy_set in policy_sets:
            api_new.policy_sets.destroy(policy_set['id'])
    return


def delete_policy_set_parameters(api_new):
    policy_sets = api_new.policy_sets.list(
        page_size=50, include="policies,workspaces")['data']
    if policy_sets:
        for policy_set in policy_sets:
            parameters = api_new.policy_set_params.list(policy_set['id'])['data']
            for parameter in parameters:
                api_new.policy_set_params.destroy(policy_set['id'], parameter['id'])
    return


def delete_modules(api_new):
    modules = api_new.registry_modules.list()['modules']
    if modules:
        for module in modules:
            api_new.registry_modules.destroy(module['name'])
    return


def delete_all(api_new):
    delete_workspaces(api_new)
    print('workspaces successfully deleted')

    delete_ssh_keys(api_new)
    print('ssh keys successfully deleted')

    delete_teams(api_new)
    print('teams successfully deleted')

    delete_policies(api_new)
    print('policies successfully deleted')

    delete_policy_sets(api_new)
    print('policy sets successfully deleted')

    delete_modules(api_new)
    print('modules successfully deleted')

    return
