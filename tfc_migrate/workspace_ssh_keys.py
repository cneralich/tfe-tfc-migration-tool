"""
Module for Terraform Enterprise/Cloud Migration Worker: Workspace SSH Keys.
"""

from .base_worker import TFCMigratorBaseWorker


class WorkspaceSSHKeysWorker(TFCMigratorBaseWorker):

    def __init__(self, api_source, api_target, vcs_connection_map, log_level):
        super().__init__(api_source, api_target, vcs_connection_map, log_level)

    def migrate_all(self, workspaces_map, workspace_to_ssh_key_map, ssh_keys_map):
        self._logger.info("Migrating SSH keys for workspaces...")

        # NOTE: No check for existing keys, since this assign function won't throw
        # an exception if the key exists.
        for source_workspace_id, ssh_key_id in workspace_to_ssh_key_map.items():
            workspace_id = ssh_keys_map[ssh_key_id]

            # Build the new ssh key payload
            new_workspace_ssh_key_payload = {
                "data": {
                    "attributes": {
                        "id": workspace_id
                    },
                    "type": "workspaces"
                }
            }

            self._logger.info("SSH key: %s, for workspace: %s, created." % \
                (ssh_key_id, workspace_id))

            # Add SSH Keys to the target workspace
            self._api_target.workspaces.assign_ssh_key( \
                workspaces_map[source_workspace_id], new_workspace_ssh_key_payload)

        self._logger.info("SSH keys for workspaces migrated.")


    def delete_all_from_target(self):
        self._logger.info("Deleting workspace SSH keys...")

        workspaces = self._api_target.workspaces.list()["data"]

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
                    self._logger.info("SSH key for workspace: %s, deleted.." % \
                        workspace["attributes"]["name"])
                    self._api_target.workspaces.unassign_ssh_key( \
                        workspace["id"], unassign_workspace_ssh_key_payload)

        self._logger.info("Workspace SSH keys deleted.")
