"""
Module for Terraform Enterprise/Cloud Migration Worker: Registry Modules.
"""

from .base_worker import TFCMigratorBaseWorker


class RegistryModulesWorker(TFCMigratorBaseWorker):
    """
    A class to represent the worker that will migrate all registry modules from
    one TFC/E org to another TFC/E org.
    """

    _api_module_used = "registry_modules"
    _required_entitlements = []

    def migrate_all(self):
        """
        Function to migrate all registry modules from one TFC/E org to another TFC/E org.
        """

        self._logger.info("Migrating registry modules...")

        source_modules = self._api_source.registry_modules.list()["data"]
        target_modules = self._api_target.registry_modules.list()["data"]
        target_module_names = \
            [target_module["name"] for target_module in target_modules]

        for source_module in source_modules:
            if source_module["source"] != "":
                source_module_name = source_module["name"]

                if source_module_name in target_module_names:
                    self._logger.info("Registry Module: %s, exists. Skipped.", source_module_name)
                    continue

                source_module_data = \
                    self._api_source.registry_modules.show(\
                        source_module_name, source_module["provider"])["data"]

                oauth_token_id = ""
                for vcs_connection in self._vcs_connection_map:
                    if vcs_connection["source"] == \
                        source_module_data["attributes"]["vcs-repo"]["oauth-token-id"]:
                        oauth_token_id = vcs_connection["target"]

                # Build the new module payload
                new_module_payload = {
                    "data": {
                        "attributes": {
                            "vcs-repo": {
                                "identifier": \
                                    source_module_data["attributes"]["vcs-repo"]["identifier"],
                                # NOTE that if the VCS the module was connected to has been
                                # deleted, it will not return Token ID and this will error.
                                "oauth-token-id": oauth_token_id,
                                "display_identifier": source_module_data\
                                    ["attributes"]["vcs-repo"]["display-identifier"]
                            }
                        },
                        "type": "registry-modules"
                    }
                }

                # Create the module in the target organization
                self._api_target.registry_modules.publish_from_vcs(new_module_payload)

                # TODO: logging

            # TODO: Add support for modules uploaded via the API

        self._logger.info("Registry modules migrated.")


    def delete_all_from_target(self):
        """
        Function to delete all registry modules from the target TFC/E org.
        """

        self._logger.info("Deleting registry modules...")

        modules = self._api_target.registry_modules.list()["data"]

        if modules:
            for module in modules:
                if module["source"] != "":
                    self._api_target.registry_modules.destroy(module["name"])
                    self._logger.info("Registry module: %s, deleted.", module["name"])

        self._logger.info("Registry modules deleted.")
