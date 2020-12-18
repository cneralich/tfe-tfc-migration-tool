"""
Module for Terraform Enterprise/Cloud Migration Worker: Registry Module Versions.
"""

import os

from .base_worker import TFCMigratorBaseWorker


class RegistryModuleVersionsWorker(TFCMigratorBaseWorker):
    """
    A class to represent the worker that will migrate all registry module
    versions from one TFC/E org to another TFC/E org.
    """

    def migrate_all(self):
        """
        Function to migrate all registry module versions from one TFC/E org to another TFC/E org.
        """

        self._logger.info("Migrating registry module versions...")

        source_modules = self._api_source.registry_modules.list()["modules"]
        target_modules = self._api_target.registry_modules.list()["modules"]
        target_module_names = \
            [target_module["name"] for target_module in target_modules]

        for source_module in source_modules:
            if source_module["source"] == "":
                source_module_name = source_module["name"]
                source_module_provider = source_module["provider"]
                source_module_version = source_module["version"]

                if source_module_name in target_module_names:
                    self._logger.info("Registry module: %s, exists. Skipped.", source_module_name)
                    continue

                # Build the new module payload
                new_module_payload = {
                    "data": {
                        "type": "registry-modules",
                        "attributes": {
                            "name": source_module_name,
                            "provider": source_module_provider
                        }
                    }
                }

                # Create the module in the target organization
                self._api_target.registry_modules.create(new_module_payload)
                self._logger.info("Registry module: %s, created.", source_module_name)

                # Build the new module version payload
                new_module_version_payload = {
                    "data": {
                        "type": "registry-module-versions",
                        "attributes": {
                            "version": source_module_version
                        }
                    }
                }

                # Create the module version in the target organization
                new_module_version = self._api_target.registry_modules.create_version(\
                    source_module_name, source_module_provider, new_module_version_payload)["data"]
                self._logger.info("Module version: %s, for module: %s, created.", \
                    source_module_version, source_module_name)

                # Pull module version file and upload to target organization
                source_module_file_path = "/tmp/%s.tar.gz" % (source_module_name)
                self._api_source.registry_modules.download_latest_source( \
                    source_module_name, source_module_provider, source_module_file_path)
                
                self._api_target.registry_modules.upload_version(\
                   source_module_file_path, new_module_version["links"]["upload"])
                self._logger.info("Module version file for version: %s, for module: %s, uploaded.", \
                    source_module_version, source_module_name)
                os.remove(source_module_file_path)

        self._logger.info("Registry module versions migrated.")


    def delete_all_from_target(self):
        self._logger.info("Deleting registry modules...")

        modules = self._api_target.registry_modules.list()["modules"]

        if modules:
            for module in modules:
                if module["source"] == "":
                    self._api_target.registry_modules.destroy(module["name"])
                    self._logger.info("Registry module: %s, deleted.", module["name"])

        self._logger.info("Registry modules deleted.")
