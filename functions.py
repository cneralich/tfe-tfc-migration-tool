import urllib.request
import hashlib
import base64
import json


def migrate_teams(api_original, api_new):
    # Fetch Teams from Existing Org
    teams = api_original.teams.list()['data']

    team_map = {}
    for team in teams:
        if team['attributes']['name'] != "owners":
            # Build the new team payload
            new_team_payload = {
                "data": {
                    "type": "teams",
                    "attributes": {
                        "name": team['attributes']['name'],
                        "organization-access": {
                            "manage-workspaces": team['attributes']['organization-access']['manage-workspaces'],
                            "manage-policies": team['attributes']['organization-access']['manage-policies'],
                            "manage-vcs-settings": team['attributes']['organization-access']['manage-vcs-settings']
                        }
                    }
                }
            }
            # Create Team in New Org
            new_team = api_new.teams.create(new_team_payload)
            # Build Team ID Map
            team_map[team['id']] = new_team["data"]["id"]
        else:
            continue
    return team_map


def migrate_ssh_keys(api_original, api_new):
    # Fetch SSH Keys from Existing Org
    # Note: This does not fetch the Keys themselves
    ssh_keys = api_original.ssh_keys.list()["data"]

    ssh_keys_map = {}
    ssh_key_name_map = {}
    if ssh_keys:
        for ssh_key in reversed(ssh_keys):
            # Build the new Agent Pool Payload
            new_ssh_key_payload = {
                "data": {
                    "type": "ssh-keys",
                    "attributes": {
                        "name": ssh_key['attributes']['name'],
                        "value": "Replace Me"
                    }
                }
            }

            # Create SSH Key in New Org
            # Note: The actual Keys themselves must be added separately afterward
            new_ssh_key = api_new.ssh_keys.create(new_ssh_key_payload)['data']
            ssh_keys_map[ssh_key['id']] = new_ssh_key['id']
            ssh_key_name_map[new_ssh_key['attributes']
                             ['name']] = new_ssh_key['id']
    return ssh_keys_map, ssh_key_name_map


def migrate_ssh_key_files(api_new, ssh_key_name_map, ssh_key_file_path_map):
    for ssh_key in ssh_key_file_path_map:
        # Pull SSH Key Data
        get_ssh_key = open(ssh_key_file_path_map[ssh_key], 'r')
        ssh_key_data = get_ssh_key.read()

        # Build the new ssh key file payload
        new_ssh_key_file_payload = {
            "data": {
                "type": "ssh-keys",
                "attributes": {
                    "value": ssh_key_data
                }
            }
        }

        # Upload the SSH Key File to the New Organization
        # Note: The ssh_key_file_path_map must be created ahead of time with a format of {'ssh_key_name':'path/to/file'}
        api_new.ssh_keys.update(
            ssh_key_name_map[ssh_key], new_ssh_key_file_payload)
    return


def migrate_agent_pools(api_original, api_new, tfe_org_original, tfe_org_new):
    # Fetch Agent Pools from Existing Org
    agent_pools = api_original.agents.list_pools(tfe_org_original)['data']
    if agent_pools:
        # Build the new agent pool payload
        new_agent_pool_payload = {
            "data": {
                "type": "agent-pools"
            }
        }

        new_org_agent_pools = api_new.agents.list_pools(tfe_org_new)['data']
        if new_org_agent_pools:
            agent_pool_id = api_new.agents.list_pools(tfe_org_new)[
                'data'][0]['id']
        else:
            # Create Agent Pool in New Org
            agent_pool_id = api_new.agents.create_pool(tfe_org_new)[
                'data']['id']
        return agent_pool_id
    else:
        return None


def migrate_workspaces(api_original, api_new, tfe_oauth_new, agent_pool_id):
    # Fetch Workspaces from Existing Org
    workspaces = api_original.workspaces.list()['data']

    workspaces_map = {}
    workspace_to_ssh_key_map = {}
    for workspace in workspaces:
        branch = "" if workspace['attributes']['vcs-repo'] is None else workspace['attributes']['vcs-repo']['branch']
        ingress_submodules = False if workspace['attributes'][
            'vcs-repo'] is None else workspace['attributes']['vcs-repo']['ingress-submodules']
        default_branch = True if branch == "" else False

        if workspace['attributes']['vcs-repo'] is not None:
            if workspace['attributes']['execution-mode'] == 'agent':
                # Build the new workspace payload
                new_workspace_payload = {
                    "data": {
                        "attributes": {
                            "name": workspace['attributes']['name'],
                            "terraform_version": workspace['attributes']['terraform-version'],
                            "working-directory": workspace['attributes']['working-directory'],
                            "file-triggers-enabled": workspace['attributes']['file-triggers-enabled'],
                            "allow-destroy-plan": workspace['attributes']['allow-destroy-plan'],
                            "auto-apply": workspace['attributes']['auto-apply'],
                            "execution-mode": workspace['attributes']['execution-mode'],
                            "agent-pool-id": agent_pool_id,
                            "description": workspace['attributes']['description'],
                            "source-name": workspace['attributes']['source-name'],
                            "source-url": workspace['attributes']['source-url'],
                            "queue-all-runs": workspace['attributes']['queue-all-runs'],
                            "speculative-enabled": workspace['attributes']['speculative-enabled'],
                            "trigger-prefixes": workspace['attributes']['trigger-prefixes'],
                            "vcs-repo": {
                                "identifier": workspace['attributes']['vcs-repo-identifier'],
                                "oauth-token-id": tfe_oauth_new,
                                "branch": branch,
                                "default-branch": default_branch,
                                "ingress-submodules": ingress_submodules
                            }
                        },
                        "type": "workspaces"
                    }
                }

                # Build the new Workspace
                new_workspace = api_new.workspaces.create(
                    new_workspace_payload)
                new_workspace_id = new_workspace["data"]["id"]

                workspaces_map[workspace['id']] = new_workspace_id

                try:
                    ssh_key = workspace['relationships']['ssh-key']['data']['id']
                    workspace_to_ssh_key_map[workspace['id']] = ssh_key
                except:
                    continue
            else:
                # Build the new workspace payload
                new_workspace_payload = {
                    "data": {
                        "attributes": {
                            "name": workspace['attributes']['name'],
                            "terraform_version": workspace['attributes']['terraform-version'],
                            "working-directory": workspace['attributes']['working-directory'],
                            "file-triggers-enabled": workspace['attributes']['file-triggers-enabled'],
                            "allow-destroy-plan": workspace['attributes']['allow-destroy-plan'],
                            "auto-apply": workspace['attributes']['auto-apply'],
                            "execution-mode": workspace['attributes']['execution-mode'],
                            "description": workspace['attributes']['description'],
                            "source-name": workspace['attributes']['source-name'],
                            "source-url": workspace['attributes']['source-url'],
                            "queue-all-runs": workspace['attributes']['queue-all-runs'],
                            "speculative-enabled": workspace['attributes']['speculative-enabled'],
                            "trigger-prefixes": workspace['attributes']['trigger-prefixes'],
                            "vcs-repo": {
                                "identifier": workspace['attributes']['vcs-repo-identifier'],
                                "oauth-token-id": tfe_oauth_new,
                                "branch": branch,
                                "default-branch": default_branch,
                                "ingress-submodules": ingress_submodules
                            }
                        },
                        "type": "workspaces"
                    }
                }

                # Build the new Workspace
                new_workspace = api_new.workspaces.create(
                    new_workspace_payload)
                new_workspace_id = new_workspace["data"]["id"]

                workspaces_map[workspace['id']] = new_workspace_id

                try:
                    ssh_key = workspace['relationships']['ssh-key']['data']['id']
                    workspace_to_ssh_key_map[workspace['id']] = ssh_key
                except:
                    continue
        else:
            if workspace['attributes']['execution-mode'] == 'agent':
                # Build the new workspace payload
                new_workspace_payload = {
                    "data": {
                        "attributes": {
                            "name": workspace['attributes']['name'],
                            "terraform_version": workspace['attributes']['terraform-version'],
                            "working-directory": workspace['attributes']['working-directory'],
                            "file-triggers-enabled": workspace['attributes']['file-triggers-enabled'],
                            "allow-destroy-plan": workspace['attributes']['allow-destroy-plan'],
                            "auto-apply": workspace['attributes']['auto-apply'],
                            "execution-mode": workspace['attributes']['execution-mode'],
                            "agent-pool-id": agent_pool_id,
                            "description": workspace['attributes']['description'],
                            "source-name": workspace['attributes']['source-name'],
                            "source-url": workspace['attributes']['source-url'],
                            "queue-all-runs": workspace['attributes']['queue-all-runs'],
                            "speculative-enabled": workspace['attributes']['speculative-enabled'],
                            "trigger-prefixes": workspace['attributes']['trigger-prefixes']
                        },
                        "type": "workspaces"
                    }
                }

                # Build the new Workspace
                new_workspace = api_new.workspaces.create(
                    new_workspace_payload)
                new_workspace_id = new_workspace['data']['id']

                workspaces_map[workspace['id']] = new_workspace_id

                try:
                    ssh_key = workspace['relationships']['ssh-key']['data']['id']
                    workspace_to_ssh_key_map[workspace['id']] = ssh_key
                except:
                    continue
            else:
                # Build the new workspace payload
                new_workspace_payload = {
                    "data": {
                        "attributes": {
                            "name": workspace['attributes']['name'],
                            "terraform_version": workspace['attributes']['terraform-version'],
                            "working-directory": workspace['attributes']['working-directory'],
                            "file-triggers-enabled": workspace['attributes']['file-triggers-enabled'],
                            "allow-destroy-plan": workspace['attributes']['allow-destroy-plan'],
                            "auto-apply": workspace['attributes']['auto-apply'],
                            "execution-mode": workspace['attributes']['execution-mode'],
                            "description": workspace['attributes']['description'],
                            "source-name": workspace['attributes']['source-name'],
                            "source-url": workspace['attributes']['source-url'],
                            "queue-all-runs": workspace['attributes']['queue-all-runs'],
                            "speculative-enabled": workspace['attributes']['speculative-enabled'],
                            "trigger-prefixes": workspace['attributes']['trigger-prefixes']
                        },
                        "type": "workspaces"
                    }
                }

                # Build the new Workspace
                new_workspace = api_new.workspaces.create(
                    new_workspace_payload)
                new_workspace_id = new_workspace['data']['id']

                workspaces_map[workspace['id']] = new_workspace_id

                try:
                    ssh_key = workspace['relationships']['ssh-key']['data']['id']
                    workspace_to_ssh_key_map[workspace['id']] = ssh_key
                except:
                    continue
    return workspaces_map, workspace_to_ssh_key_map


def migrate_all_state(api_original, api_new, tfe_org_original, workspaces_map):
    for workspace_id in workspaces_map:
        workspace_name = api_original.workspaces.show(workspace_id=workspace_id)[
            'data']['attributes']['name']

        # Set proper state filters to pull state versions for each workspace
        state_filters = [
            {
                "keys": ["workspace", "name"],
                "value":  workspace_name
            },
            {
                "keys": ["organization", "name"],
                "value": tfe_org_original
            }
        ]

        state_versions = api_original.state_versions.list(
            filters=state_filters)['data']
        if state_versions:
            for state_version in reversed(state_versions):
                state_url = state_version['attributes']['hosted-state-download-url']
                pull_state = urllib.request.urlopen(state_url)
                state_data = pull_state.read()
                state_serial = json.loads(state_data)['serial']

                state_hash = hashlib.md5()
                state_hash.update(state_data)
                state_md5 = state_hash.hexdigest()
                state_b64 = base64.b64encode(state_data).decode("utf-8")

                # Build the new state payload
                create_state_version_payload = {
                    "data": {
                        "type": "state-versions",
                        "attributes": {
                            "serial": state_serial,
                            "md5": state_md5,
                            "state": state_b64
                        }
                    }
                }

                # Migrate state to the new Workspace
                api_new.workspaces.lock(workspaces_map[workspace_id], {
                                        "reason": "migration script"})
                api_new.state_versions.create(
                    workspaces_map[workspace_id], create_state_version_payload)
                api_new.workspaces.unlock(workspaces_map[workspace_id])
        else:
            continue
    return


def migrate_current_state(api_original, api_new, tfe_org_original, workspaces_map):
    for workspace_id in workspaces_map:
        workspace_name = api_original.workspaces.show(workspace_id=workspace_id)[
            'data']['attributes']['name']

        # Set proper state filters to pull state versions for each workspace
        state_filters = [
            {
                "keys": ["workspace", "name"],
                "value":  workspace_name
            },
            {
                "keys": ["organization", "name"],
                "value": tfe_org_original
            }
        ]

        state_versions = api_original.state_versions.list(
            filters=state_filters)['data']
        if state_versions:
            current_version = api_original.state_versions.get_current(workspace_id)[
                'data']
            state_url = current_version['attributes']['hosted-state-download-url']
            pull_state = urllib.request.urlopen(state_url)
            state_data = pull_state.read()
            state_serial = json.loads(state_data)['serial']

            state_hash = hashlib.md5()
            state_hash.update(state_data)
            state_md5 = state_hash.hexdigest()
            state_b64 = base64.b64encode(state_data).decode("utf-8")

            # Build the new state payload
            create_state_version_payload = {
                "data": {
                    "type": "state-versions",
                    "attributes": {
                        "serial": state_serial,
                        "md5": state_md5,
                        "state": state_b64
                    }
                }
            }

            # Migrate state to the new Workspace
            api_new.workspaces.lock(workspaces_map[workspace_id], {
                                    "reason": "migration script"})
            api_new.state_versions.create(
                workspaces_map[workspace_id], create_state_version_payload)
            api_new.workspaces.unlock(workspaces_map[workspace_id])
        else:
            continue
    return


def migrate_workspace_variables(api_original, api_new, tfe_org_original, workspaces_map, return_sensitive_variable_data=False):
    sensitive_variable_data = []
    for workspace_id in workspaces_map:
        # Pull Variables from the Old Workspace
        workspace_variables = api_original.workspace_vars.list(workspace_id)[
            'data']

        for variable in reversed(workspace_variables):
            variable_key = variable['attributes']['key']
            variable_value = variable['attributes']['value']
            variable_category = variable['attributes']['category']
            variable_hcl = variable['attributes']['hcl']
            variable_description = variable['attributes']['description']
            variable_sensitive = variable['attributes']['sensitive']

            # Build the new variable payload
            new_variable_payload = {
                "data": {
                    "type": "vars",
                    "attributes": {
                        "key": variable_key,
                        "value": variable_value,
                        "description": variable_description,
                        "category": variable_category,
                        "hcl": variable_hcl,
                        "sensitive": variable_sensitive
                    }
                }
            }

            # Migrate variables to the new Workspace
            new_variable = api_new.workspace_vars.create(
                workspaces_map[workspace_id], new_variable_payload)['data']
            new_variable_id = new_variable['id']

            if variable_sensitive and return_sensitive_variable_data:
                workspace_name = api_new.workspaces.show(workspace_id=workspace_id)[
                    'data']['attributes']['name']

                # Build the sensitive variable map
                variable_data = {
                    'workspace_name': workspace_name,
                    'workspace_id': workspace_id,
                    'variable_id': new_variable_id,
                    'variable_key': variable_key,
                    'variable_value': variable_value,
                    'variable_description': variable_description,
                    'category': variable_category,
                    'hcl': variable_hcl
                }

                sensitive_variable_data.append(variable_data)
    return sensitive_variable_data


def migrate_workspace_sensitive_variables(api_new, sensitive_variable_data_map):
    for sensitive_variable in sensitive_variable_data_map:
        # Build the new variable payload
        update_variable_payload = {
            "data": {
                "id": sensitive_variable['variable_id'],
                "attributes": {
                    "key": sensitive_variable['variable_key'],
                    "value": sensitive_variable['variable_value'],
                    "description": sensitive_variable['variable_description'],
                    "category": sensitive_variable['category'],
                    "hcl": sensitive_variable['hcl'],
                    "sensitive": 'true'
                },
                "type": "vars"
            }
        }

        # Update the Sensitive Variable value in the New Workspace
        # Note: The sensitive_variable_data_map must be created ahead of time. The easiest way to do this is to update the
        #       value for each variable in the list returned by the migrate_workspace_variables method

        api_new.workspace_vars.update(
            sensitive_variable['workspace_id'], sensitive_variable['variable_id'], update_variable_payload)
    return


def migrate_ssh_keys_to_workspaces(api_original, api_new, workspaces_map, workspace_to_ssh_key_map, ssh_keys_map):
    if workspace_to_ssh_key_map:
        for k, v in workspace_to_ssh_key_map.items():
            # Build the new ssh key payload
            new_workspace_ssh_key_payload = {
                "data": {
                    "attributes": {
                        "id": ssh_keys_map[v]
                    },
                    "type": "workspaces"
                }
            }

            # Add SSH Keys to the new Workspace
            api_new.workspaces.assign_ssh_key(
                workspaces_map[k], new_workspace_ssh_key_payload)
    return


def migrate_workspace_run_triggers(api_original, api_new, workspaces_map):
    for workspace in workspaces_map:
        workspace_filters = [
            {
                "keys": ["run-trigger", "type"],
                "value": "inbound"
            }
        ]

        # Pull Run Triggers from the Old Workspace
        run_triggers = api_original.run_triggers.list(
            workspace, filters=workspace_filters,  page_size=100)['data']

        if run_triggers:
            for run_trigger in run_triggers:
                source_workspace_id = run_trigger['relationships']['sourceable']['data']['id']

                # Build the new run trigger payload
                new_run_trigger_payload = {
                    "data": {
                        "relationships": {
                            "sourceable": {
                                "data": {
                                    "id": workspaces_map[source_workspace_id],
                                    "type": "workspaces"
                                }
                            }
                        }
                    }
                }

                # Add Run Triggers to the new Workspace
                api_new.run_triggers.create(
                    workspaces_map[workspace], new_run_trigger_payload)
    return


def migrate_workspace_notifications(api_original, api_new, workspaces_map):
    for workspace in workspaces_map:
        # Pull Notifications from the Old Workspace
        notifications = api_original.notification_configs.list(workspace)[
            'data']

        if notifications:
            for notification in notifications:
                if notification['attributes']['destination-type'] == 'email':
                    # Build the new notification payload
                    new_notification_payload = {
                        "data": {
                            "type": "notification-configurations",
                            "attributes": {
                                "destination-type": notification['attributes']['destination-type'],
                                "enabled": notification['attributes']['enabled'],
                                "name": notification['attributes']['name'],
                                "triggers": notification['attributes']['triggers']
                            },
                            "relationships": {
                                "users": {
                                    "data":  notification['relationships']['users']['data']
                                }
                            }
                        }
                    }

                    # Add Notifications to the new Workspace
                    api_new.notification_configs.create(
                        workspaces_map[workspace], new_notification_payload)
                else:
                    # Build the new notification payload
                    new_notification_payload = {
                        "data": {
                            "type": "notification-configurations",
                            "attributes": {
                                "destination-type": notification['attributes']['destination-type'],
                                "enabled": notification['attributes']['enabled'],
                                "name": notification['attributes']['name'],
                                "token": notification['attributes']['token'],
                                "url": notification['attributes']['url'],
                                "triggers": notification['attributes']['triggers']
                            }
                        }
                    }

                    # Add Notifications to the new Workspace
                    api_new.notification_configs.create(
                        workspaces_map[workspace], new_notification_payload)
    return


def migrate_workspace_team_access(api_original, api_new, workspaces_map, team_map):
    for workspace_id in workspaces_map:
        # Set proper workspace team filters to pull team access for each workspace
        workspace_team_filters = [
            {
                "keys": ["workspace", "id"],
                "value": workspace_id
            }
        ]

        # Pull Teams from the Old Workspace
        workspace_teams = api_original.team_access.list(
            filters=workspace_team_filters)["data"]
        for workspace_team in workspace_teams:
            if workspace_team['attributes']['access'] == 'custom':
                # Build the new team access payload
                new_workspace_team_payload = {
                    "data": {
                        "attributes": {
                            "access": workspace_team['attributes']['access'],
                            "runs": workspace_team['attributes']['runs'],
                            "variables": workspace_team['attributes']['variables'],
                            "state-versions": workspace_team['attributes']['state-versions'],
                            "plan-outputs": "none",
                            "sentinel-mocks": workspace_team['attributes']['sentinel-mocks'],
                            "workspace-locking": workspace_team['attributes']['workspace-locking']
                        },
                        "relationships": {
                            "workspace": {
                                "data": {
                                    "type": "workspaces",
                                    "id": workspaces_map[workspace_id]
                                }
                            },
                            "team": {
                                "data": {
                                    "type": "teams",
                                    "id": team_map[workspace_team['relationships']['team']['data']['id']]
                                }
                            }
                        },
                        "type": "team-workspaces"
                    }
                }

                # Create the Team Workspace Access map for the new Workspace
                api_new.team_access.add_team_access(new_workspace_team_payload)
            else:
                # Build the new team access payload
                new_workspace_team_payload = {
                    "data": {
                        "attributes": {
                            "access": workspace_team['attributes']['access'],
                        },
                        "relationships": {
                            "workspace": {
                                "data": {
                                    "type": "workspaces",
                                    "id": workspaces_map[workspace_id]
                                }
                            },
                            "team": {
                                "data": {
                                    "type": "teams",
                                    "id": team_map[workspace_team['relationships']['team']['data']['id']]
                                }
                            }
                        },
                        "type": "team-workspaces"
                    }
                }

                # Create the Team Workspace Access map for the new Workspace
                api_new.team_access.add_team_access(new_workspace_team_payload)
    return


def migrate_configuration_versions(api_original, api_new, workspaces_map):
    workspace_to_configuration_version_map = {}

    for workspace_id in workspaces_map:
        workspace_name = api_original.workspaces.show(workspace_id=workspace_id)[
            'data']['attributes']['name']
        # Fetch Configuration Versions for the Existing Workspace
        configuration_versions = api_original.config_versions.list(workspace_id)[
            'data']
        if configuration_versions:
            latest_configuration_version = configuration_versions[0]
            if latest_configuration_version['attributes']['source'] == 'tfe-api':
                # Build the new configuration version payload
                new_configuration_version_payload = {
                    "data": {
                        "type": "configuration-versions",
                        "attributes": {
                            "auto-queue-runs": latest_configuration_version['attributes']['auto-queue-runs']
                        }
                    }
                }

                # Create a configuration version in the New Organization
                new_configuration_version = api_new.config_versions.create(
                    workspaces_map[workspace_id], new_configuration_version_payload)['data']
                workspace_to_configuration_version_map[workspace_name] = new_configuration_version['id']
    return workspace_to_configuration_version_map


def migrate_configuration_files(api_new, workspace_to_configuration_version_map, workspace_to_file_path_map):
    for workspace_name in workspace_to_file_path_map:
        # Upload the Configuration File to the New Workspace
        # Note: The workspace_to_file_path_map must be created ahead of time with a format of {'workspace_name':'path/to/file'}
        api_new.config_versions.upload(
            workspace_to_file_path_map[workspace_name], workspace_to_configuration_version_map[workspace_name])
    return


def migrate_policies(api_original, api_new, tfe_token_original, tfe_url_original):
    # Pull Policies from the Old Organization
    policies = api_original.policies.list()['data']

    policies_map = {}

    if policies:
        for policy in policies:
            policy_id = policy['id']

            headers = {'Authorization': 'Bearer %s' % (
                tfe_token_original), 'Content-Type': 'application/vnd.api+json'}
            policy_download_url = '%s/api/v2/policies/%s/download' % (
                tfe_url_original, policy_id)

            # Retrieve the Policy Content
            policy_request = urllib.request.Request(
                policy_download_url, headers=headers)
            pull_policy = urllib.request.urlopen(policy_request)
            policy_data = pull_policy.read()
            policy_b64 = policy_data.decode("utf-8")

            # Build the new policy payload
            new_policy_payload = {
                "data": {
                    "attributes": {
                        "name": policy['attributes']['name'],
                        "description": policy['attributes']['description'],
                        "enforce": [
                            {
                                "path": policy['attributes']['enforce'][0]['path'],
                                "mode": policy['attributes']['enforce'][0]['mode']
                            }
                        ],
                    },
                    "type": "policies"
                }
            }

            # Create the policy in the New Organization
            new_policy = api_new.policies.create(new_policy_payload)
            new_policy_id = new_policy['data']['id']

            policies_map[policy_id] = new_policy_id

            # Upload the policy content to the new policy in the New Organization
            api_new.policies.upload(new_policy_id, policy_b64)
        return policies_map
    else:
        return


def migrate_policy_sets(api_original, api_new, tfe_oauth_new, workspaces_map, policies_map):
    # Pull Policy Sets from the Old Organization
    policy_sets = api_original.policy_sets.list(
        page_size=50, include='policies,workspaces')['data']

    policy_sets_map = {}
    for policy_set in policy_sets:
        if policy_set['attributes']['versioned']:
            if policy_set['attributes']['global']:
                # Build the new policy set payload
                new_policy_set_payload = {
                    "data": {
                        "type": "policy-sets",
                        "attributes": {
                            "name": policy_set['attributes']['name'],
                            "description": policy_set['attributes']['name'],
                            "global": policy_set['attributes']['global'],
                            "policies-path": policy_set['attributes']['policies-path'],
                            "vcs-repo": {
                                "branch": policy_set['attributes']['vcs-repo']['branch'],
                                "identifier": policy_set['attributes']['vcs-repo']['identifier'],
                                "ingress-submodules": policy_set['attributes']['vcs-repo']['ingress-submodules'],
                                "oauth-token-id": tfe_oauth_new
                            }
                        },
                        "relationships": {
                        }
                    }
                }

                # Create the policy set in the New Organization
                new_policy_set = api_new.policy_sets.create(
                    new_policy_set_payload)
                policy_sets_map[policy_set['id']
                                ] = new_policy_set['data']['id']
            else:
                workspace_ids = policy_set['relationships']['workspaces']['data']
                for workspace_id in workspace_ids:
                    workspace_id['id'] = workspaces_map[workspace_id['id']]

                # Build the new policy set payload
                new_policy_set_payload = {
                    "data": {
                        "type": "policy-sets",
                        "attributes": {
                            "name": policy_set['attributes']['name'],
                            "description": policy_set['attributes']['name'],
                            "global": policy_set['attributes']['global'],
                            "policies-path": policy_set['attributes']['policies-path'],
                            "vcs-repo": {
                                "branch": policy_set['attributes']['vcs-repo']['branch'],
                                "identifier": policy_set['attributes']['vcs-repo']['identifier'],
                                "ingress-submodules": policy_set['attributes']['vcs-repo']['ingress-submodules'],
                                "oauth-token-id": tfe_oauth_new
                            }
                        },
                        "relationships": {
                            "workspaces": {
                                "data":
                                workspace_ids
                            }
                        }
                    }
                }

                # Create the policy set in the New Organization
                new_policy_set = api_new.policy_sets.create(
                    new_policy_set_payload)
                policy_sets_map[policy_set['id']
                                ] = new_policy_set['data']['id']
        else:
            if policy_set['attributes']['global']:
                policy_ids = policy_set['relationships']['policies']['data']
                for policy_id in policy_ids:
                    policy_id['id'] = policies_map[policy_id['id']]

                # Build the new policy set payload
                new_policy_set_payload = {
                    "data": {
                        "type": "policy-sets",
                        "attributes": {
                            "name": policy_set['attributes']['name'],
                            "description": policy_set['attributes']['name'],
                            "global": policy_set['attributes']['global'],
                        },
                        "relationships": {
                            "policies": {
                                "data":
                                policy_ids
                            }
                        }
                    }
                }

                # Create the policy set in the New Organization
                new_policy_set = api_new.policy_sets.create(
                    new_policy_set_payload)
                policy_sets_map[policy_set['id']
                                ] = new_policy_set['data']['id']
            else:
                policy_ids = policy_set['relationships']['policies']['data']
                for policy_id in policy_ids:
                    policy_id['id'] = policies_map[policy_id['id']]

                workspace_ids = policy_set['relationships']['workspaces']['data']
                for workspace_id in workspace_ids:
                    workspace_id['id'] = workspaces_map[workspace_id['id']]

                # Build the new policy set payload
                new_policy_set_payload = {
                    "data": {
                        "type": "policy-sets",
                        "attributes": {
                            "name": policy_set['attributes']['name'],
                            "description": policy_set['attributes']['name'],
                            "global": policy_set['attributes']['global'],
                        },
                        "relationships": {
                            "policies": {
                                "data":
                                policy_ids
                            },
                            "workspaces": {
                                "data":
                                workspace_ids
                            }
                        }
                    }
                }

                # Create the policy set in the New Organization
                new_policy_set = api_new.policy_sets.create(
                    new_policy_set_payload)
                policy_sets_map[policy_set['id']
                                ] = new_policy_set['data']['id']
    return policy_sets_map


def migrate_policy_set_parameters(api_original, api_new, policy_sets_map):
    for policy_set_id in policy_sets_map:
        # Pull Policy Sets from the Old Organization
        policy_set_parameters = api_original.policy_set_params.list(
            policy_set_id)
        if policy_set_parameters['data']:
            for policy_set_parameter in reversed(policy_set_parameters['data']):
                # Build the new policy set parameter payload
                new_policy_parameter_payload = {
                    "data": {
                        "type": "vars",
                        "attributes": {
                            "key": policy_set_parameter['attributes']['key'],
                            "value": policy_set_parameter['attributes']['value'],
                            "category": policy_set_parameter['attributes']['category'],
                            "sensitive": policy_set_parameter['attributes']['sensitive']
                        }
                    }
                }

                # Create the policy set parameter in the New Organization
                api_new.policy_set_params.create(
                    policy_sets_map[policy_set_id], new_policy_parameter_payload)
        else:
            continue
    return


# TO DO: Account for Modules uploaded via VCS and API
# TO DO: Account for ALL versions of Module
# TO DO: Note OAuth token challenges (ex. if they don't all share the same token)
def migrate_registry_modules(api_original, api_new, tfe_org_original, tfe_oauth_new):
    modules = api_original.registry_modules.list()['modules']
    for module in modules:
        # Pull VCS Modules from the Old Organization
        module_data = api_original.registry_modules.show(
            tfe_org_original, module['name'], module['provider'])['data']

        # Build the new Module payload
        new_module_payload = {
            "data": {
                "attributes": {
                    "vcs-repo": {
                        "identifier": module_data['attributes']['vcs-repo']['identifier'],
                        "oauth-token-id": tfe_oauth_new,
                        "display_identifier": module_data['attributes']['vcs-repo']['display-identifier']
                    }
                },
                "type": "registry-modules"
            }
        }

        # Create the Module in the New Organization
        api_new.registry_modules.publish_from_vcs(new_module_payload)
    return
