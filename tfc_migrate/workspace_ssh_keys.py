

def migrate(\
        api_source, api_target, workspaces_map, workspace_to_ssh_key_map, \
            ssh_keys_map):

    print("Migrating SSH keys for workspaces...")

    # NOTE: No check for existing keys, since this assign function won't throw
    # an exception if the key already exists.
    for key, value in workspace_to_ssh_key_map.items():
        # Build the new ssh key payload
        new_workspace_ssh_key_payload = {
            "data": {
                "attributes": {
                    "id": ssh_keys_map[value]
                },
                "type": "workspaces"
            }
        }

        print(f"\t ssh key %s created for workspace..." % value)

        # Add SSH Keys to the target workspace
        api_target.workspaces.assign_ssh_key(
            workspaces_map[key], new_workspace_ssh_key_payload)

    print("SSH keys for workspaces successfully migrated.")


def delete_all(api_target):
    print("Deleting workspace SSH keys...")

    workspaces = api_target.workspaces.list()["data"]

    if workspaces:
        unassign_workspace_ssh_key_payload = {
            "data": {
                "attributes": {
                    "id": None
                },
                "type": "workspaces"
            }
        }

        for workspace in workspaces:
            if "ssh-key" in workspace["relationships"]:
                print(f"\t deleting ssh key from workspace %s..." % workspace["attributes"]["name"])
                api_target.workspaces.unassign_ssh_key( \
                    workspace["id"], unassign_workspace_ssh_key_payload)
    
    print("Workspace SSH keys deleted.")
                