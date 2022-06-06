"""
Module for Terraform Enterprise/Cloud Migration Worker: Workspaces.
"""

from .base_worker import TFCMigratorBaseWorker
from terrasnek import exceptions

class WorkspacesWorker(TFCMigratorBaseWorker):
    """
    A class to represent the worker that will migrate all workspaces from one
    TFC/E org to another TFC/E org.
    """

    _api_module_used = "workspaces"
    _required_entitlements = []

    def migrate(self, agent_pools_map, migrate_select=False):
        """
        Function to migrate all workspaces from one TFC/E org to another TFC/E org.
        """

        self._logger.info("Migrating workspaces...")

        source_workspaces = []
        # Fetch workspaces from existing org
        if migrate_select:
            # If we are migrating specific workspaces, retrieve those specific workspaces
            for source_workspace in self._select_items_list["workspaces"]:
                try:
                    source_workspace = self._api_source.workspaces.show(workspace_name=source_workspace)["data"]
                    source_workspaces.append(source_workspace)
                except exceptions.TFCHTTPNotFound as not_found:
                    self._logger.info(f"Source workspace <{source_workspace}> does not exist in the source org.")
                    pass
        else:
            # Otherwise, get all of the workspaces
            source_workspaces = self._api_source.workspaces.list_all()["data"]

        target_workspaces = self._api_target.workspaces.list_all()["data"]

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

                self._logger.info("Workspace: %s, exists. Skipped.", source_workspace_name)
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
                        "speculative-enabled": \
                            source_workspace["attributes"]["speculative-enabled"],
                        "trigger-prefixes": source_workspace["attributes"]["trigger-prefixes"],
                    },
                    "type": "workspaces"
                }
            }

            # Set agent pool ID unless target is TFE
            if source_workspace["attributes"]["execution-mode"] == "agent":
                if agent_pools_map and 'app.terraform.io' in self._api_target.get_url():
                    new_workspace_payload["data"]["attributes"]["agent-pool-id"] = \
                        agent_pools_map[\
                            source_workspace["relationships"]["agent-pool"]["data"]["id"]]
                else:
                    new_workspace_payload["data"]["attributes"]["execution-mode"] = "remote"

            # TODO: if there is no oauth_token_id in the source, we cannot migrate it for now
            if source_workspace["attributes"]["vcs-repo"] is not None and \
                "oauth-token-id" in source_workspace["attributes"]["vcs-repo"]:
                oauth_token_id = ""
                for vcs_connection in self._vcs_connection_map:
                    if vcs_connection["source"] == \
                        source_workspace["attributes"]["vcs-repo"]["oauth-token-id"]:
                        oauth_token_id = vcs_connection["target"]

                new_workspace_payload["data"]["attributes"]["vcs-repo"] = {
                    "identifier": source_workspace["attributes"]["vcs-repo-identifier"],
                    "oauth-token-id": oauth_token_id,
                    "branch": branch,
                    "default-branch": default_branch,
                    "ingress-submodules": ingress_submodules
                }

            # Build the new workspace
            new_workspace = self._api_target.workspaces.create(new_workspace_payload)
            self._logger.info("Workspace: %s, created.", source_workspace_name)

            new_workspace_id = new_workspace["data"]["id"]
            workspaces_map[source_workspace["id"]] = new_workspace_id

            if "ssh-key" in source_workspace["relationships"]:
                ssh_key = source_workspace["relationships"]["ssh-key"]["data"]["id"]
                workspace_to_ssh_key_map[source_workspace["id"]] = ssh_key

        self._logger.info("Workspaces migrated.")
        return workspaces_map, workspace_to_ssh_key_map

    def delete_all_from_target(self):
        """
        Function to delete all workspaces from the target TFC/E org.
        """

        self._logger.info("Deleting workspaces...")

        workspaces = self._api_target.workspaces.list_all()["data"]

        if workspaces:
            for workspace in workspaces:
                self._api_target.workspaces.destroy(workspace["id"])
                self._logger.info("Workspace: %s, deleted.", workspace["attributes"]["name"])

        self._logger.info("Workspaces deleted.")
