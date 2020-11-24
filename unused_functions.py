"""
This is an example version of the migrate_workspaces function that includes support for Workspaces connected to GitHub Apps
Managing these connections is not currently supported via the API, but might be in a future version.
"""

# def migrate_workspaces(api_source, api_target, tfe_vcs_connection_map, agent_pool_id):
#     # Fetch Workspaces from Existing Org
#     workspaces = api_source.workspaces.list()["data"]

#     workspaces_map = {}
#     workspace_to_ssh_key_map = {}
#     for workspace in workspaces:
#         branch = "" if workspace["attributes"]["vcs-repo"] is None else workspace["attributes"]["vcs-repo"]["branch"]
#         ingress_submodules = False if workspace["attributes"][
#             "vcs-repo"] is None else workspace["attributes"]["vcs-repo"]["ingress-submodules"]
#         default_branch = True if branch == "" else False

#         if workspace["attributes"]["vcs-repo"] is not None:
#             is_oauth = "oauth-token-id" in workspace["attributes"]["vcs-repo"]
#             if workspace["attributes"]["execution-mode"] == "agent":
#                 if is_oauth:
#                     # Build the new workspace payload
#                     new_workspace_payload = {
#                         "data": {
#                             "attributes": {
#                                 "name": workspace["attributes"]["name"],
#                                 "terraform_version": workspace["attributes"]["terraform-version"],
#                                 "working-directory": workspace["attributes"]["working-directory"],
#                                 "file-triggers-enabled": workspace["attributes"]["file-triggers-enabled"],
#                                 "allow-destroy-plan": workspace["attributes"]["allow-destroy-plan"],
#                                 "auto-apply": workspace["attributes"]["auto-apply"],
#                                 "execution-mode": workspace["attributes"]["execution-mode"],
#                                 "agent-pool-id": agent_pool_id,
#                                 "description": workspace["attributes"]["description"],
#                                 "source-name": workspace["attributes"]["source-name"],
#                                 "source-url": workspace["attributes"]["source-url"],
#                                 "queue-all-runs": workspace["attributes"]["queue-all-runs"],
#                                 "speculative-enabled": workspace["attributes"]["speculative-enabled"],
#                                 "trigger-prefixes": workspace["attributes"]["trigger-prefixes"],
#                                 "vcs-repo": {
#                                     "identifier": workspace["attributes"]["vcs-repo-identifier"],
#                                     "oauth-token-id": tfe_vcs_connection_map[workspace["attributes"]["vcs-repo"]["oauth-token-id"]],
#                                     "branch": branch,
#                                     "default-branch": default_branch,
#                                     "ingress-submodules": ingress_submodules
#                                 }
#                             },
#                             "type": "workspaces"
#                         }
#                     }
#                 else:
#                     # Build the new workspace payload
#                     new_workspace_payload = {
#                         "data": {
#                             "attributes": {
#                                 "name": workspace["attributes"]["name"],
#                                 "terraform_version": workspace["attributes"]["terraform-version"],
#                                 "working-directory": workspace["attributes"]["working-directory"],
#                                 "file-triggers-enabled": workspace["attributes"]["file-triggers-enabled"],
#                                 "allow-destroy-plan": workspace["attributes"]["allow-destroy-plan"],
#                                 "auto-apply": workspace["attributes"]["auto-apply"],
#                                 "execution-mode": workspace["attributes"]["execution-mode"],
#                                 "agent-pool-id": agent_pool_id,
#                                 "description": workspace["attributes"]["description"],
#                                 "source-name": workspace["attributes"]["source-name"],
#                                 "source-url": workspace["attributes"]["source-url"],
#                                 "queue-all-runs": workspace["attributes"]["queue-all-runs"],
#                                 "speculative-enabled": workspace["attributes"]["speculative-enabled"],
#                                 "trigger-prefixes": workspace["attributes"]["trigger-prefixes"],
#                                 "vcs-repo": {
#                                     "identifier": workspace["attributes"]["vcs-repo-identifier"],
#                                     "github-app-installation-id": tfe_vcs_connection_map[workspace["attributes"]["vcs-repo"]["github-app-installation-id"]],
#                                     "branch": branch,
#                                     "default-branch": default_branch,
#                                     "ingress-submodules": ingress_submodules
#                                 }
#                             },
#                             "type": "workspaces"
#                         }
#                     }

#                 # Build the new Workspace
#                 new_workspace = api_target.workspaces.create(
#                     new_workspace_payload)
#                 new_workspace_id = new_workspace["data"]["id"]

#                 workspaces_map[workspace["id"]] = new_workspace_id

#                 try:
#                     ssh_key = workspace["relationships"]["ssh-key"]["data"]["id"]
#                     workspace_to_ssh_key_map[workspace["id"]] = ssh_key
#                 except:
#                     continue
#             else:
#                 if is_oauth:
#                     # Build the new workspace payload
#                     new_workspace_payload = {
#                         "data": {
#                             "attributes": {
#                                 "name": workspace["attributes"]["name"],
#                                 "terraform_version": workspace["attributes"]["terraform-version"],
#                                 "working-directory": workspace["attributes"]["working-directory"],
#                                 "file-triggers-enabled": workspace["attributes"]["file-triggers-enabled"],
#                                 "allow-destroy-plan": workspace["attributes"]["allow-destroy-plan"],
#                                 "auto-apply": workspace["attributes"]["auto-apply"],
#                                 "execution-mode": workspace["attributes"]["execution-mode"],
#                                 "description": workspace["attributes"]["description"],
#                                 "source-name": workspace["attributes"]["source-name"],
#                                 "source-url": workspace["attributes"]["source-url"],
#                                 "queue-all-runs": workspace["attributes"]["queue-all-runs"],
#                                 "speculative-enabled": workspace["attributes"]["speculative-enabled"],
#                                 "trigger-prefixes": workspace["attributes"]["trigger-prefixes"],
#                                 "vcs-repo": {
#                                     "identifier": workspace["attributes"]["vcs-repo-identifier"],
#                                     "oauth-token-id": tfe_vcs_connection_map[workspace["attributes"]["vcs-repo"]["oauth-token-id"]],
#                                     "branch": branch,
#                                     "default-branch": default_branch,
#                                     "ingress-submodules": ingress_submodules
#                                 }
#                             },
#                             "type": "workspaces"
#                         }
#                     }
#                 else:
#                     # Build the new workspace payload
#                     new_workspace_payload = {
#                         "data": {
#                             "attributes": {
#                                 "name": workspace["attributes"]["name"],
#                                 "terraform_version": workspace["attributes"]["terraform-version"],
#                                 "working-directory": workspace["attributes"]["working-directory"],
#                                 "file-triggers-enabled": workspace["attributes"]["file-triggers-enabled"],
#                                 "allow-destroy-plan": workspace["attributes"]["allow-destroy-plan"],
#                                 "auto-apply": workspace["attributes"]["auto-apply"],
#                                 "execution-mode": workspace["attributes"]["execution-mode"],
#                                 "description": workspace["attributes"]["description"],
#                                 "source-name": workspace["attributes"]["source-name"],
#                                 "source-url": workspace["attributes"]["source-url"],
#                                 "queue-all-runs": workspace["attributes"]["queue-all-runs"],
#                                 "speculative-enabled": workspace["attributes"]["speculative-enabled"],
#                                 "trigger-prefixes": workspace["attributes"]["trigger-prefixes"],
#                                 "vcs-repo": {
#                                     "identifier": workspace["attributes"]["vcs-repo-identifier"],
#                                     "github-app-installation-id": tfe_vcs_connection_map[workspace["attributes"]["vcs-repo"]["github-app-installation-id"]],
#                                     "branch": branch,
#                                     "default-branch": default_branch,
#                                     "ingress-submodules": ingress_submodules
#                                 }
#                             },
#                             "type": "workspaces"
#                         }
#                     }
#                 # Build the new Workspace
#                 new_workspace = api_target.workspaces.create(
#                     new_workspace_payload)
#                 new_workspace_id = new_workspace["data"]["id"]

#                 workspaces_map[workspace["id"]] = new_workspace_id

#                 try:
#                     ssh_key = workspace["relationships"]["ssh-key"]["data"]["id"]
#                     workspace_to_ssh_key_map[workspace["id"]] = ssh_key
#                 except:
#                     continue
#         else:
#             if workspace["attributes"]["execution-mode"] == "agent":
#                 # Build the new workspace payload
#                 new_workspace_payload = {
#                     "data": {
#                         "attributes": {
#                             "name": workspace["attributes"]["name"],
#                             "terraform_version": workspace["attributes"]["terraform-version"],
#                             "working-directory": workspace["attributes"]["working-directory"],
#                             "file-triggers-enabled": workspace["attributes"]["file-triggers-enabled"],
#                             "allow-destroy-plan": workspace["attributes"]["allow-destroy-plan"],
#                             "auto-apply": workspace["attributes"]["auto-apply"],
#                             "execution-mode": workspace["attributes"]["execution-mode"],
#                             "agent-pool-id": agent_pool_id,
#                             "description": workspace["attributes"]["description"],
#                             "source-name": workspace["attributes"]["source-name"],
#                             "source-url": workspace["attributes"]["source-url"],
#                             "queue-all-runs": workspace["attributes"]["queue-all-runs"],
#                             "speculative-enabled": workspace["attributes"]["speculative-enabled"],
#                             "trigger-prefixes": workspace["attributes"]["trigger-prefixes"]
#                         },
#                         "type": "workspaces"
#                     }
#                 }

#                 # Build the new Workspace
#                 new_workspace = api_target.workspaces.create(
#                     new_workspace_payload)
#                 new_workspace_id = new_workspace["data"]["id"]

#                 workspaces_map[workspace["id"]] = new_workspace_id

#                 try:
#                     ssh_key = workspace["relationships"]["ssh-key"]["data"]["id"]
#                     workspace_to_ssh_key_map[workspace["id"]] = ssh_key
#                 except:
#                     continue
#             else:
#                 # Build the new workspace payload
#                 new_workspace_payload = {
#                     "data": {
#                         "attributes": {
#                             "name": workspace["attributes"]["name"],
#                             "terraform_version": workspace["attributes"]["terraform-version"],
#                             "working-directory": workspace["attributes"]["working-directory"],
#                             "file-triggers-enabled": workspace["attributes"]["file-triggers-enabled"],
#                             "allow-destroy-plan": workspace["attributes"]["allow-destroy-plan"],
#                             "auto-apply": workspace["attributes"]["auto-apply"],
#                             "execution-mode": workspace["attributes"]["execution-mode"],
#                             "description": workspace["attributes"]["description"],
#                             "source-name": workspace["attributes"]["source-name"],
#                             "source-url": workspace["attributes"]["source-url"],
#                             "queue-all-runs": workspace["attributes"]["queue-all-runs"],
#                             "speculative-enabled": workspace["attributes"]["speculative-enabled"],
#                             "trigger-prefixes": workspace["attributes"]["trigger-prefixes"]
#                         },
#                         "type": "workspaces"
#                     }
#                 }

#                 # Build the new Workspace
#                 new_workspace = api_target.workspaces.create(
#                     new_workspace_payload)
#                 new_workspace_id = new_workspace["data"]["id"]

#                 workspaces_map[workspace["id"]] = new_workspace_id

#                 try:
#                     ssh_key = workspace["relationships"]["ssh-key"]["data"]["id"]
#                     workspace_to_ssh_key_map[workspace["id"]] = ssh_key
#                 except:
#                     continue
#     return workspaces_map, workspace_to_ssh_key_map

"""
This is an example version of the migrate_policy_sets function that includes support for
Workspaces connected to GitHub Apps Managing these connections is not currently supported
via the API, but might be in a future version.
"""
# def migrate_policy_sets(api_source, api_target, tfe_vcs_connection_map, workspaces_map, policies_map):
#     # Pull Policy Sets from the old organization
#     policy_sets = api_source.policy_sets.list(
#         page_size=50, include="policies,workspaces")["data"]

#     policy_sets_map = {}
#     for policy_set in policy_sets:
#         if policy_set["attributes"]["versioned"]:
#             is_oauth = "oauth-token-id" in policy_set["attributes"]["vcs-repo"]
#             if policy_set["attributes"]["global"]:
#                 if is_oauth:
#                     # Build the new policy set payload
#                     new_policy_set_payload = {
#                         "data": {
#                             "type": "policy-sets",
#                             "attributes": {
#                                 "name": policy_set["attributes"]["name"],
#                                 "description": policy_set["attributes"]["name"],
#                                 "global": policy_set["attributes"]["global"],
#                                 "policies-path": policy_set["attributes"]["policies-path"],
#                                 "vcs-repo": {
#                                     "branch": policy_set["attributes"]["vcs-repo"]["branch"],
#                                     "identifier": policy_set["attributes"]["vcs-repo"]["identifier"],
#                                     "ingress-submodules": policy_set["attributes"]["vcs-repo"]["ingress-submodules"],
#                                     "oauth-token-id": tfe_vcs_connection_map[policy_set["attributes"]["vcs-repo"]["oauth-token-id"]]
#                                 }
#                             },
#                             "relationships": {
#                             }
#                         }
#                     }
#                 else:
#                     # Build the new policy set payload
#                     new_policy_set_payload = {
#                         "data": {
#                             "type": "policy-sets",
#                             "attributes": {
#                                 "name": policy_set["attributes"]["name"],
#                                 "description": policy_set["attributes"]["name"],
#                                 "global": policy_set["attributes"]["global"],
#                                 "policies-path": policy_set["attributes"]["policies-path"],
#                                 "vcs-repo": {
#                                     "branch": policy_set["attributes"]["vcs-repo"]["branch"],
#                                     "identifier": policy_set["attributes"]["vcs-repo"]["identifier"],
#                                     "ingress-submodules": policy_set["attributes"]["vcs-repo"]["ingress-submodules"],
#                                     "github-app-installation-id": tfe_vcs_connection_map[policy_set["attributes"]["vcs-repo"]["github-app-installation-id"]]
#                                 }
#                             },
#                             "relationships": {
#                             }
#                         }
#                     }

#                 # Create the policy set in the target organization
#                 new_policy_set = api_target.policy_sets.create(
#                     new_policy_set_payload)
#                 policy_sets_map[policy_set["id"]
#                                 ] = new_policy_set["data"]["id"]
#             else:
#                 workspace_ids = policy_set["relationships"]["workspaces"]["data"]
#                 for workspace_id in workspace_ids:
#                     workspace_id["id"] = workspaces_map[workspace_id["id"]]

#                 if is_oauth:
#                     # Build the new policy set payload
#                     new_policy_set_payload = {
#                         "data": {
#                             "type": "policy-sets",
#                             "attributes": {
#                                 "name": policy_set["attributes"]["name"],
#                                 "description": policy_set["attributes"]["name"],
#                                 "global": policy_set["attributes"]["global"],
#                                 "policies-path": policy_set["attributes"]["policies-path"],
#                                 "vcs-repo": {
#                                     "branch": policy_set["attributes"]["vcs-repo"]["branch"],
#                                     "identifier": policy_set["attributes"]["vcs-repo"]["identifier"],
#                                     "ingress-submodules": policy_set["attributes"]["vcs-repo"]["ingress-submodules"],
#                                     "oauth-token-id": tfe_vcs_connection_map[policy_set["attributes"]["vcs-repo"]["oauth-token-id"]]
#                                 }
#                             },
#                             "relationships": {
#                                 "workspaces": {
#                                     "data":
#                                     workspace_ids
#                                 }
#                             }
#                         }
#                     }
#                 else:
#                     # Build the new policy set payload
#                     new_policy_set_payload = {
#                         "data": {
#                             "type": "policy-sets",
#                             "attributes": {
#                                 "name": policy_set["attributes"]["name"],
#                                 "description": policy_set["attributes"]["name"],
#                                 "global": policy_set["attributes"]["global"],
#                                 "policies-path": policy_set["attributes"]["policies-path"],
#                                 "vcs-repo": {
#                                     "branch": policy_set["attributes"]["vcs-repo"]["branch"],
#                                     "identifier": policy_set["attributes"]["vcs-repo"]["identifier"],
#                                     "ingress-submodules": policy_set["attributes"]["vcs-repo"]["ingress-submodules"],
#                                     "github-app-installation-id": tfe_vcs_connection_map[policy_set["attributes"]["vcs-repo"]["github-app-installation-id"]]
#                                 }
#                             },
#                             "relationships": {
#                                 "workspaces": {
#                                     "data":
#                                     workspace_ids
#                                 }
#                             }
#                         }
#                     }

#                 # Create the policy set in the target organization
#                 new_policy_set = api_target.policy_sets.create(
#                     new_policy_set_payload)
#                 policy_sets_map[policy_set["id"]
#                                 ] = new_policy_set["data"]["id"]
#         else:
#             if policy_set["attributes"]["global"]:
#                 policy_ids = policy_set["relationships"]["policies"]["data"]
#                 for policy_id in policy_ids:
#                     policy_id["id"] = policies_map[policy_id["id"]]

#                 # Build the new policy set payload
#                 new_policy_set_payload = {
#                     "data": {
#                         "type": "policy-sets",
#                         "attributes": {
#                             "name": policy_set["attributes"]["name"],
#                             "description": policy_set["attributes"]["name"],
#                             "global": policy_set["attributes"]["global"],
#                         },
#                         "relationships": {
#                             "policies": {
#                                 "data":
#                                 policy_ids
#                             }
#                         }
#                     }
#                 }

#                 # Create the policy set in the target organization
#                 new_policy_set = api_target.policy_sets.create(
#                     new_policy_set_payload)
#                 policy_sets_map[policy_set["id"]
#                                 ] = new_policy_set["data"]["id"]
#             else:
#                 policy_ids = policy_set["relationships"]["policies"]["data"]
#                 for policy_id in policy_ids:
#                     policy_id["id"] = policies_map[policy_id["id"]]

#                 workspace_ids = policy_set["relationships"]["workspaces"]["data"]
#                 for workspace_id in workspace_ids:
#                     workspace_id["id"] = workspaces_map[workspace_id["id"]]

#                 # Build the new policy set payload
#                 new_policy_set_payload = {
#                     "data": {
#                         "type": "policy-sets",
#                         "attributes": {
#                             "name": policy_set["attributes"]["name"],
#                             "description": policy_set["attributes"]["name"],
#                             "global": policy_set["attributes"]["global"],
#                         },
#                         "relationships": {
#                             "policies": {
#                                 "data":
#                                 policy_ids
#                             },
#                             "workspaces": {
#                                 "data":
#                                 workspace_ids
#                             }
#                         }
#                     }
#                 }

#                 # Create the policy set in the target organization
#                 new_policy_set = api_target.policy_sets.create(
#                     new_policy_set_payload)
#                 policy_sets_map[policy_set["id"]
#                                 ] = new_policy_set["data"]["id"]
#     return policy_sets_map


"""
This is an example version of the migrate_workspaces function that includes support for Workspaces connected to GitHub Apps
Managing these connections is not currently supported via the API, but might be in a future version.
"""

# def migrate_workspaces(api_source, api_target, tfe_vcs_connection_map, agent_pool_id):
#     # Fetch Workspaces from Existing Org
#     workspaces = api_source.workspaces.list()["data"]

#     workspaces_map = {}
#     workspace_to_ssh_key_map = {}
#     for workspace in workspaces:
#         branch = "" if workspace["attributes"]["vcs-repo"] is None else workspace["attributes"]["vcs-repo"]["branch"]
#         ingress_submodules = False if workspace["attributes"][
#             "vcs-repo"] is None else workspace["attributes"]["vcs-repo"]["ingress-submodules"]
#         default_branch = True if branch == "" else False

#         if workspace["attributes"]["vcs-repo"] is not None:
#             is_oauth = "oauth-token-id" in workspace["attributes"]["vcs-repo"]
#             if workspace["attributes"]["execution-mode"] == "agent":
#                 if is_oauth:
#                     # Build the new workspace payload
#                     new_workspace_payload = {
#                         "data": {
#                             "attributes": {
#                                 "name": workspace["attributes"]["name"],
#                                 "terraform_version": workspace["attributes"]["terraform-version"],
#                                 "working-directory": workspace["attributes"]["working-directory"],
#                                 "file-triggers-enabled": workspace["attributes"]["file-triggers-enabled"],
#                                 "allow-destroy-plan": workspace["attributes"]["allow-destroy-plan"],
#                                 "auto-apply": workspace["attributes"]["auto-apply"],
#                                 "execution-mode": workspace["attributes"]["execution-mode"],
#                                 "agent-pool-id": agent_pool_id,
#                                 "description": workspace["attributes"]["description"],
#                                 "source-name": workspace["attributes"]["source-name"],
#                                 "source-url": workspace["attributes"]["source-url"],
#                                 "queue-all-runs": workspace["attributes"]["queue-all-runs"],
#                                 "speculative-enabled": workspace["attributes"]["speculative-enabled"],
#                                 "trigger-prefixes": workspace["attributes"]["trigger-prefixes"],
#                                 "vcs-repo": {
#                                     "identifier": workspace["attributes"]["vcs-repo-identifier"],
#                                     "oauth-token-id": tfe_vcs_connection_map[workspace["attributes"]["vcs-repo"]["oauth-token-id"]],
#                                     "branch": branch,
#                                     "default-branch": default_branch,
#                                     "ingress-submodules": ingress_submodules
#                                 }
#                             },
#                             "type": "workspaces"
#                         }
#                     }
#                 else:
#                     # Build the new workspace payload
#                     new_workspace_payload = {
#                         "data": {
#                             "attributes": {
#                                 "name": workspace["attributes"]["name"],
#                                 "terraform_version": workspace["attributes"]["terraform-version"],
#                                 "working-directory": workspace["attributes"]["working-directory"],
#                                 "file-triggers-enabled": workspace["attributes"]["file-triggers-enabled"],
#                                 "allow-destroy-plan": workspace["attributes"]["allow-destroy-plan"],
#                                 "auto-apply": workspace["attributes"]["auto-apply"],
#                                 "execution-mode": workspace["attributes"]["execution-mode"],
#                                 "agent-pool-id": agent_pool_id,
#                                 "description": workspace["attributes"]["description"],
#                                 "source-name": workspace["attributes"]["source-name"],
#                                 "source-url": workspace["attributes"]["source-url"],
#                                 "queue-all-runs": workspace["attributes"]["queue-all-runs"],
#                                 "speculative-enabled": workspace["attributes"]["speculative-enabled"],
#                                 "trigger-prefixes": workspace["attributes"]["trigger-prefixes"],
#                                 "vcs-repo": {
#                                     "identifier": workspace["attributes"]["vcs-repo-identifier"],
#                                     "github-app-installation-id": tfe_vcs_connection_map[workspace["attributes"]["vcs-repo"]["github-app-installation-id"]],
#                                     "branch": branch,
#                                     "default-branch": default_branch,
#                                     "ingress-submodules": ingress_submodules
#                                 }
#                             },
#                             "type": "workspaces"
#                         }
#                     }

#                 # Build the new Workspace
#                 new_workspace = api_target.workspaces.create(
#                     new_workspace_payload)
#                 new_workspace_id = new_workspace["data"]["id"]

#                 workspaces_map[workspace["id"]] = new_workspace_id

#                 try:
#                     ssh_key = workspace["relationships"]["ssh-key"]["data"]["id"]
#                     workspace_to_ssh_key_map[workspace["id"]] = ssh_key
#                 except:
#                     continue
#             else:
#                 if is_oauth:
#                     # Build the new workspace payload
#                     new_workspace_payload = {
#                         "data": {
#                             "attributes": {
#                                 "name": workspace["attributes"]["name"],
#                                 "terraform_version": workspace["attributes"]["terraform-version"],
#                                 "working-directory": workspace["attributes"]["working-directory"],
#                                 "file-triggers-enabled": workspace["attributes"]["file-triggers-enabled"],
#                                 "allow-destroy-plan": workspace["attributes"]["allow-destroy-plan"],
#                                 "auto-apply": workspace["attributes"]["auto-apply"],
#                                 "execution-mode": workspace["attributes"]["execution-mode"],
#                                 "description": workspace["attributes"]["description"],
#                                 "source-name": workspace["attributes"]["source-name"],
#                                 "source-url": workspace["attributes"]["source-url"],
#                                 "queue-all-runs": workspace["attributes"]["queue-all-runs"],
#                                 "speculative-enabled": workspace["attributes"]["speculative-enabled"],
#                                 "trigger-prefixes": workspace["attributes"]["trigger-prefixes"],
#                                 "vcs-repo": {
#                                     "identifier": workspace["attributes"]["vcs-repo-identifier"],
#                                     "oauth-token-id": tfe_vcs_connection_map[workspace["attributes"]["vcs-repo"]["oauth-token-id"]],
#                                     "branch": branch,
#                                     "default-branch": default_branch,
#                                     "ingress-submodules": ingress_submodules
#                                 }
#                             },
#                             "type": "workspaces"
#                         }
#                     }
#                 else:
#                     # Build the new workspace payload
#                     new_workspace_payload = {
#                         "data": {
#                             "attributes": {
#                                 "name": workspace["attributes"]["name"],
#                                 "terraform_version": workspace["attributes"]["terraform-version"],
#                                 "working-directory": workspace["attributes"]["working-directory"],
#                                 "file-triggers-enabled": workspace["attributes"]["file-triggers-enabled"],
#                                 "allow-destroy-plan": workspace["attributes"]["allow-destroy-plan"],
#                                 "auto-apply": workspace["attributes"]["auto-apply"],
#                                 "execution-mode": workspace["attributes"]["execution-mode"],
#                                 "description": workspace["attributes"]["description"],
#                                 "source-name": workspace["attributes"]["source-name"],
#                                 "source-url": workspace["attributes"]["source-url"],
#                                 "queue-all-runs": workspace["attributes"]["queue-all-runs"],
#                                 "speculative-enabled": workspace["attributes"]["speculative-enabled"],
#                                 "trigger-prefixes": workspace["attributes"]["trigger-prefixes"],
#                                 "vcs-repo": {
#                                     "identifier": workspace["attributes"]["vcs-repo-identifier"],
#                                     "github-app-installation-id": tfe_vcs_connection_map[workspace["attributes"]["vcs-repo"]["github-app-installation-id"]],
#                                     "branch": branch,
#                                     "default-branch": default_branch,
#                                     "ingress-submodules": ingress_submodules
#                                 }
#                             },
#                             "type": "workspaces"
#                         }
#                     }
#                 # Build the new Workspace
#                 new_workspace = api_target.workspaces.create(
#                     new_workspace_payload)
#                 new_workspace_id = new_workspace["data"]["id"]

#                 workspaces_map[workspace["id"]] = new_workspace_id

#                 try:
#                     ssh_key = workspace["relationships"]["ssh-key"]["data"]["id"]
#                     workspace_to_ssh_key_map[workspace["id"]] = ssh_key
#                 except:
#                     continue
#         else:
#             if workspace["attributes"]["execution-mode"] == "agent":
#                 # Build the new workspace payload
#                 new_workspace_payload = {
#                     "data": {
#                         "attributes": {
#                             "name": workspace["attributes"]["name"],
#                             "terraform_version": workspace["attributes"]["terraform-version"],
#                             "working-directory": workspace["attributes"]["working-directory"],
#                             "file-triggers-enabled": workspace["attributes"]["file-triggers-enabled"],
#                             "allow-destroy-plan": workspace["attributes"]["allow-destroy-plan"],
#                             "auto-apply": workspace["attributes"]["auto-apply"],
#                             "execution-mode": workspace["attributes"]["execution-mode"],
#                             "agent-pool-id": agent_pool_id,
#                             "description": workspace["attributes"]["description"],
#                             "source-name": workspace["attributes"]["source-name"],
#                             "source-url": workspace["attributes"]["source-url"],
#                             "queue-all-runs": workspace["attributes"]["queue-all-runs"],
#                             "speculative-enabled": workspace["attributes"]["speculative-enabled"],
#                             "trigger-prefixes": workspace["attributes"]["trigger-prefixes"]
#                         },
#                         "type": "workspaces"
#                     }
#                 }

#                 # Build the new Workspace
#                 new_workspace = api_target.workspaces.create(
#                     new_workspace_payload)
#                 new_workspace_id = new_workspace["data"]["id"]

#                 workspaces_map[workspace["id"]] = new_workspace_id

#                 try:
#                     ssh_key = workspace["relationships"]["ssh-key"]["data"]["id"]
#                     workspace_to_ssh_key_map[workspace["id"]] = ssh_key
#                 except:
#                     continue
#             else:
#                 # Build the new workspace payload
#                 new_workspace_payload = {
#                     "data": {
#                         "attributes": {
#                             "name": workspace["attributes"]["name"],
#                             "terraform_version": workspace["attributes"]["terraform-version"],
#                             "working-directory": workspace["attributes"]["working-directory"],
#                             "file-triggers-enabled": workspace["attributes"]["file-triggers-enabled"],
#                             "allow-destroy-plan": workspace["attributes"]["allow-destroy-plan"],
#                             "auto-apply": workspace["attributes"]["auto-apply"],
#                             "execution-mode": workspace["attributes"]["execution-mode"],
#                             "description": workspace["attributes"]["description"],
#                             "source-name": workspace["attributes"]["source-name"],
#                             "source-url": workspace["attributes"]["source-url"],
#                             "queue-all-runs": workspace["attributes"]["queue-all-runs"],
#                             "speculative-enabled": workspace["attributes"]["speculative-enabled"],
#                             "trigger-prefixes": workspace["attributes"]["trigger-prefixes"]
#                         },
#                         "type": "workspaces"
#                     }
#                 }

#                 # Build the new Workspace
#                 new_workspace = api_target.workspaces.create(
#                     new_workspace_payload)
#                 new_workspace_id = new_workspace["data"]["id"]

#                 workspaces_map[workspace["id"]] = new_workspace_id

#                 try:
#                     ssh_key = workspace["relationships"]["ssh-key"]["data"]["id"]
#                     workspace_to_ssh_key_map[workspace["id"]] = ssh_key
#                 except:
#                     continue
#     return workspaces_map, workspace_to_ssh_key_map