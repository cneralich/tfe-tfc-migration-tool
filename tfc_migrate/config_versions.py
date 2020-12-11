"""
Module for Terraform Enterprise/Cloud Migration Worker: Config Versions.
"""

from .base_worker import TFCMigratorBaseWorker


class ConfigVersionsWorker(TFCMigratorBaseWorker):
    """
    A class to represent the worker that will migrate all config versions
    from one TFC/E org to another TFC/E org.
    """

    def migrate_all(self, workspaces_map):
        self._logger.info("Migrating config versions...")

        workspace_to_config_version_upload_map = {}

        for workspace_id in workspaces_map:
            workspace_name = self._api_source.workspaces.show(workspace_id=workspace_id)\
                ["data"]["attributes"]["name"]

            # Fetch config versions for the existing workspace
            config_versions = self._api_source.config_versions.list(workspace_id)["data"]

            if config_versions:
                latest_config_version = config_versions[0]

                if latest_config_version["attributes"]["source"] == "tfe-api":
                    # Build the new config version payload
                    new_config_version_payload = {
                        "data": {
                            "type": "configuration-versions",
                            "attributes": {
                                "auto-queue-runs": latest_config_version\
                                    ["attributes"]["auto-queue-runs"]
                            }
                        }
                    }

                    # Create a config version in the target organization
                    new_config_version = self._api_target.config_versions.create(\
                        workspaces_map[workspace_id], new_config_version_payload)["data"]

                    self._logger.info("Config version for workspace: %s, created." % workspace_name)

                    workspace_to_config_version_upload_map[workspace_name] = \
                        new_config_version["attributes"]["upload-url"]

        self._logger.info("Config versions migrated.")

        return workspace_to_config_version_upload_map


    def migrate_config_files(self, workspace_to_config_version_upload_map, workspace_to_file_path_map):
        self._logger.info("Migrating config files...")

        for workspace_name in workspace_to_file_path_map:
            # NOTE: The workspace_to_file_path_map must be created ahead of time
            # with a format of {"workspace_name":"path/to/file"}

            # Upload the config file to the target workspace
            self._api_target.config_versions.upload(\
                workspace_to_file_path_map[workspace_name], \
                    workspace_to_config_version_upload_map[workspace_name])

            self._logger.info("Config files for workspace: %s, uploaded." % workspace_name)

        self._logger.info("Config files migrated.")
