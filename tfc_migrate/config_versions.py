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
        """
        Function to migrate all config versions from one TFC/E org to another TFC/E org.
        """

        self._logger.info("Migrating config versions...")

        workspace_to_config_version_upload_url_map = {}
        workspace_to_config_version_file_path_map = []

        for source_workspace_id in workspaces_map:
            source_workspace_name = self._api_source.workspaces.show(workspace_id=source_workspace_id)\
                ["data"]["attributes"]["name"]
            target_workspace_id = workspaces_map[source_workspace_id]

            # Fetch config versions for the existing workspace
            config_versions = self._api_source.config_versions.list(source_workspace_id)["data"]

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
                        target_workspace_id, new_config_version_payload)["data"]

                    self._logger.info("Config version for workspace: %s, created.", source_workspace_name)

                    workspace_to_config_version_upload_url_map[source_workspace_name] = \
                        new_config_version["attributes"]["upload-url"]
                    
                    workspace_to_config_version_file_path_map.append(\
                        {"workspace_name":source_workspace_name, "workspace_id":target_workspace_id, "path_to_config_version_file":""})

        self._logger.info("Config versions migrated.")

        return workspace_to_config_version_upload_url_map, workspace_to_config_version_file_path_map


    def migrate_config_files(self):
        self._logger.info("Migrating config files...")

        if "workspace_to_config_version_upload_url_map" in self._sensitive_data_map and \
            "workspace_to_config_version_file_path_map" in self._sensitive_data_map:
            
            workspace_to_config_version_upload_url_map = self._sensitive_data_map["workspace_to_config_version_upload_url_map"]
            workspace_to_config_version_file_path_map = self._sensitive_data_map["workspace_to_config_version_file_path_map"]

            for workspace in workspace_to_config_version_file_path_map:
                """
                NOTE: The workspace_to_config_version_file_path_map is provided as an output by the migrate_all method
                above, and the missing "path_to_config_version_file" values should be updated prior to invoking this function.
                For reference, the correct format for each item in the list should be:
                {"workspace_name":"workspace_name", "workspace_id":"workspace_id", "path_to_config_version_file":"path/to/file"}
                {"ssh_key_name":"name_of_ssh_key", "path_to_ssh_key_file":"path/to/file"}
                """

                workspace_name = workspace["workspace_name"]

                # Upload the config file to the target workspace
                self._api_target.config_versions.upload(\
                    workspace["path_to_config_version_file"], \
                        workspace_to_config_version_upload_url_map[workspace_name])

                self._logger.info("Config files for workspace: %s, uploaded.", workspace_name)

        self._logger.info("Config files migrated.")
