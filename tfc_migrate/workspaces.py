

def migrate(api_source, api_target, tfe_vcs_connection_map, agent_pools_map):
    print("Migrating workspaces...")

    # Fetch workspaces from existing org
    source_workspaces = api_source.workspaces.list()["data"]
    target_workspaces = api_target.workspaces.list()["data"]

    target_workspaces_data = {}
    for target_workspace in target_workspaces:
        target_workspaces_data[target_workspace["attributes"]["name"]] = target_workspace["id"]

    workspaces_map = {}
    workspace_to_ssh_key_map = {}

    for source_workspace in source_workspaces:
        source_workspace_name = source_workspace["attributes"]["name"]
        source_workspace_id = source_workspace["id"]

        if source_workspace_name in target_workspaces_data:
            workspaces_map[source_workspace_id] = target_workspaces_data[source_workspace_name]

            if "ssh-key" in source_workspace["relationships"]:
                ssh_key = source_workspace["relationships"]["ssh-key"]["data"]["id"]
                workspace_to_ssh_key_map[source_workspace["id"]] = ssh_key

            print("\t", source_workspace_name, "workspace already exists, skipping...")
            continue

        branch = "" if source_workspace["attributes"]["vcs-repo"] is None \
            else source_workspace["attributes"]["vcs-repo"]["branch"]

        ingress_submodules = False if source_workspace["attributes"]["vcs-repo"] is None \
            else source_workspace["attributes"]["vcs-repo"]["ingress-submodules"]

        default_branch = True if branch == "" else False

        new_workspace_payload = {
            "data": {
                "attributes": {
                    "name": source_workspace_name,
                    "terraform_version": source_workspace["attributes"]["terraform-version"],
                    "working-directory": source_workspace["attributes"]["working-directory"],
                    "file-triggers-enabled": \
                        source_workspace["attributes"]["file-triggers-enabled"],
                    "allow-destroy-plan": source_workspace["attributes"]["allow-destroy-plan"],
                    "auto-apply": source_workspace["attributes"]["auto-apply"],
                    "execution-mode": source_workspace["attributes"]["execution-mode"],
                    "description": source_workspace["attributes"]["description"],
                    "source-name": source_workspace["attributes"]["source-name"],
                    "source-url": source_workspace["attributes"]["source-url"],
                    "queue-all-runs": source_workspace["attributes"]["queue-all-runs"],
                    "speculative-enabled": source_workspace["attributes"]["speculative-enabled"],
                    "trigger-prefixes": source_workspace["attributes"]["trigger-prefixes"],
                },
                "type": "workspaces"
            }
        }

        # Set agent pool ID unless target is TFE
        if source_workspace["attributes"]["execution-mode"] == "agent":
            if 'app.terraform.io' in api_target.get_url():
                new_workspace_payload["data"]["attributes"]["agent-pool-id"] = agent_pools_map[source_workspace["relationships"]["agent-pool"]["data"]["id"]]
            else:
                new_workspace_payload["data"]["attributes"]["execution-mode"] = "remote"

        if source_workspace["attributes"]["vcs-repo"] is not None:
            oauth_token_id = ""
            for tfe_vcs_connection in tfe_vcs_connection_map:
                if tfe_vcs_connection["source"] == source_workspace["attributes"]["vcs-repo"]["oauth-token-id"]:
                    oauth_token_id = tfe_vcs_connection["target"]

            new_workspace_payload["data"]["attributes"]["vcs-repo"] = {
                "identifier": source_workspace["attributes"]["vcs-repo-identifier"],
                "oauth-token-id": oauth_token_id,
                "branch": branch,
                "default-branch": default_branch,
                "ingress-submodules": ingress_submodules
            }

        # Build the new workspace
        new_workspace = api_target.workspaces.create(new_workspace_payload)
        print(f"\t workspace %s created..." % source_workspace_name)

        new_workspace_id = new_workspace["data"]["id"]
        workspaces_map[source_workspace["id"]] = new_workspace_id

        if "ssh-key" in source_workspace["relationships"]:
            ssh_key = source_workspace["relationships"]["ssh-key"]["data"]["id"]
            workspace_to_ssh_key_map[source_workspace["id"]] = ssh_key

    print("Workspaces successfully migrated.")
    return workspaces_map, workspace_to_ssh_key_map


def delete_all(api_target):
    print("Deleting workspaces...")

    workspaces = api_target.workspaces.list()["data"]

    if workspaces:
        for workspace in workspaces:
            print(f"\t deleting workspace %s..." % workspace["attributes"]["name"])
            api_target.workspaces.destroy(workspace["id"])

    print("Workspaces deleted.")
