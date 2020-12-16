"""
Module for Terraform Enterprise/Cloud Migration Worker: Registry Module Versions.
"""

from .base_worker import TFCMigratorBaseWorker


class RegistryModuleVersionsWorker(TFCMigratorBaseWorker):
    """
    A class to represent the worker that will migrate all registry module
    versions from one TFC/E org to another TFC/E org.
    """

    def migrate_all(self):
        self._logger.info("Migrating registry module versions...")

        source_modules = self._api_source.registry_modules.list()["modules"]
        target_modules = self._api_target.registry_modules.list()["modules"]
        target_module_names = \
            [target_module["name"] for target_module in target_modules]

        module_to_module_version_upload_map = {}
        module_to_file_path_map = []

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

                module_to_module_version_upload_map[source_module_name] = \
                    new_module_version["links"]["upload"]
                module_to_file_path_map.append({"module_name":source_module_name,"path_to_module_file":""})

        self._logger.info("Registry module versions migrated.")

        return module_to_module_version_upload_map, module_to_file_path_map


    def migrate_module_version_files(self):
        self._logger.info("Migrating module version files...")

        if "module_to_module_version_upload_map" in self._sensitive_data_map \
            and "module_to_file_path_map" in self._sensitive_data_map:

            module_to_module_version_upload_map = self._sensitive_data_map["module_to_module_version_upload_map"]
            module_to_file_path_map = self._sensitive_data_map["module_to_file_path_map"]

            for module in module_to_file_path_map:
                """
                NOTE: The module_to_file_path_map is provided as an output by the migrate_all method
                above, and the missing "path_to_ssh_key_file" values should be updated prior to invoking this function.
                For reference, the correct format for each item in the list should be:
                {"module_name":"name_of_module", "path_to_module_file":"path/to/file"}
                """
                
                module_name = module["module_name"]

                # Upload the module version file
                self._api_target.registry_modules.upload_version(\
                    module_to_file_path_map["path_to_module_file"], \
                        module_to_module_version_upload_map[module_name])

                self._logger.info("Module version file for module: %s, uploaded.", module_name)

            self._logger.info("Module version files migrated.")


    def delete_all_from_target(self):
        self._logger.info("Deleting registry modules...")

        modules = self._api_target.registry_modules.list()["modules"]

        if modules:
            for module in modules:
                if module["source"] == "":
                    self._api_target.registry_modules.destroy(module["name"])
                    self._logger.info("Registry module: %s, deleted.", module["name"])

        self._logger.info("Registry modules deleted.")
