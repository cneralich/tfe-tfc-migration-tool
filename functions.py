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

def migrate_workspaces(api_original, api_new, tfe_oauth_new):
    workspaces = api_original.workspaces.list()['data']

    workspaces_map = {}
    for workspace in workspaces:
        branch = "" if workspace['attributes']['vcs-repo'] is None else workspace['attributes']['vcs-repo']['branch']
        ingress_submodules = False if workspace['attributes']['vcs-repo'] is None else workspace['attributes']['vcs-repo']['ingress-submodules']
        default_branch = True if branch == "" else False

        if workspace['attributes']['vcs-repo'] is not None: 
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
            new_workspace = api_new.workspaces.create(new_workspace_payload)
            new_workspace_id = new_workspace["data"]["id"]

            workspaces_map[workspace['id']] = new_workspace_id
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
            new_workspace = api_new.workspaces.create(new_workspace_payload)
            new_workspace_id = new_workspace["data"]["id"]
            
            workspaces_map[workspace['id']] = new_workspace_id
    return workspaces_map

def migrate_all_state(api_original, api_new, tfe_org_original, workspaces_map):
    for workspace_id in workspaces_map:
        workspace_name = api_original.workspaces.show(workspace_id=workspace_id)['data']['attributes']['name']

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

        state_versions = api_original.state_versions.list(filters=state_filters)['data']
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

                api_new.workspaces.lock(workspaces_map[workspace_id], {"reason": "migration script"})
                api_new.state_versions.create(workspaces_map[workspace_id], create_state_version_payload)
                api_new.workspaces.unlock(workspaces_map[workspace_id])
        else:
            continue
    return

def migrate_current_state(api_original, api_new, tfe_org_original, workspaces_map):
    for workspace_id in workspaces_map:
        workspace_name = api_original.workspaces.show(workspace_id=workspace_id)['data']['attributes']['name']

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

        state_versions = api_original.state_versions.list(filters=state_filters)['data']
        if state_versions:
            current_version = api_original.state_versions.get_current(workspace_id)['data']
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

            api_new.workspaces.lock(workspaces_map[workspace_id], {"reason": "migration script"})
            api_new.state_versions.create(workspaces_map[workspace_id], create_state_version_payload)
            api_new.workspaces.unlock(workspaces_map[workspace_id])
        else:
            continue
    return

def migrate_workspace_variables(api_original, api_new, tfe_org_original, workspaces_map):
    for workspace_id in workspaces_map:
        # Pull Variables from the Old Workspace
        workspace_variables = api_original.workspace_vars.list(workspace_id)['data']

        for variable in reversed(workspace_variables):
            # Build the new variable payload
            new_variable_payload = {
                "data": {
                    "type":"vars",
                    "attributes": {
                        "key": variable['attributes']['key'],
                        "value": variable['attributes']['value'],
                        "description": variable['attributes']['description'],
                        "category": variable['attributes']['category'],
                        "hcl": variable['attributes']['hcl'],
                        "sensitive": variable['attributes']['sensitive']
                    }
                }
            }

            api_new.workspace_vars.create(workspaces_map[workspace_id], new_variable_payload)
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

        workspace_teams = api_original.team_access.list(filters=workspace_team_filters)["data"]
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

def migrate_policies(api_original, api_new, tfe_token_original, tfe_url_original):
   policies = api_original.policies.list()['data']

   policies_map = {}

   if policies:
      for policy in policies:
        policy_id = policy['id']

        headers = {'Authorization': 'Bearer %s' % (tfe_token_original), 'Content-Type': 'application/vnd.api+json'} 
        policy_download_url = '%s/api/v2/policies/%s/download' % (tfe_url_original, policy_id)

        # Retrieve the Policy Content
        policy_request = urllib.request.Request(policy_download_url, headers=headers)
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
                "type":"policies"
            }
        }

        # Create the new policy
        new_policy = api_new.policies.create(new_policy_payload)
        new_policy_id = new_policy['data']['id']

        policies_map[policy_id] = new_policy_id

        # Upload the policy content to the new policy
        api_new.policies.upload(new_policy_id, policy_b64)
      return policies_map
   else:
      return

def migrate_policy_sets(api_original, api_new, tfe_oauth_new, workspaces_map, policies_map):
   policy_sets = api_original.policy_sets.list(\
      page_size=50, include="policies,workspaces")["data"]
   
   policy_sets_map = {}
   for policy_set in policy_sets:
      if policy_set['attributes']['versioned']:
         if policy_set['attributes']['global']:
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
            new_policy_set = api_new.policy_sets.create(new_policy_set_payload)
            policy_sets_map[policy_set['id']] = new_policy_set['data']['id']
         else:
            workspace_ids = policy_set['relationships']['workspaces']['data']
            for workspace_id in workspace_ids:
               workspace_id['id'] = workspaces_map[workspace_id['id']]

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
            
            new_policy_set = api_new.policy_sets.create(new_policy_set_payload)
            policy_sets_map[policy_set['id']] = new_policy_set['data']['id']
      else:
         if policy_set['attributes']['global']:
            policy_ids = policy_set['relationships']['policies']['data']
            for policy_id in policy_ids:
               policy_id['id'] = policies_map[policy_id['id']]

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
            
            new_policy_set = api_new.policy_sets.create(new_policy_set_payload)
            policy_sets_map[policy_set['id']] = new_policy_set['data']['id']
         else:
            policy_ids = policy_set['relationships']['policies']['data']
            for policy_id in policy_ids:
               policy_id['id'] = policies_map[policy_id['id']]
            
            workspace_ids = policy_set['relationships']['workspaces']['data']
            for workspace_id in workspace_ids:
               workspace_id['id'] = workspaces_map[workspace_id['id']]
            
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

            new_policy_set = api_new.policy_sets.create(new_policy_set_payload)
            policy_sets_map[policy_set['id']] = new_policy_set['data']['id']
   return policy_sets_map

def migrate_policy_set_parameters(api_original, api_new, policy_sets_map):
   for policy_set_id in policy_sets_map:
      policy_set_parameters = api_original.policy_set_params.list(policy_set_id)
      if policy_set_parameters['data']:
         for policy_set_parameter in reversed(policy_set_parameters['data']):
            new_policy_parameter_payload = {
               "data": {
                  "type":"vars",
                  "attributes": {
                     "key": policy_set_parameter['attributes']['key'],
                     "value": policy_set_parameter['attributes']['value'],
                     "category": policy_set_parameter['attributes']['category'],
                     "sensitive": policy_set_parameter['attributes']['sensitive']
                  }
               }
            }

            api_new.policy_set_params.create(policy_sets_map[policy_set_id], new_policy_parameter_payload)
      else:
         continue

def delete_new_org(api_new):
    workspaces = api_new.workspaces.list()['data']
    for workspace in workspaces:
        api_new.workspaces.destroy(workspace['id'])

    teams = api_new.teams.list()['data']
    for team in teams:
        if team['attributes']['name'] != "owners":
            api_new.teams.destroy(team['id'])

    policies = api_new.policies.list()['data']
    for policy in policies:
        api_new.policies.destroy(policy['id'])

    policy_sets = api_new.policy_sets.list(\
      page_size=50, include="policies,workspaces")["data"]
    for policy_set in policy_sets:
        api_new.policy_sets.destroy(policy_set['id'])
