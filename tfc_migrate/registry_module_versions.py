

def migrate(api_source, api_target):
    print("Migrating registry module versions...")

    source_modules = api_source.registry_modules.list()["modules"]
    target_modules = api_target.registry_modules.list()["modules"]
    target_module_names = \
        [target_module["name"] for target_module in target_modules]

    module_to_module_version_upload_map = {}

    for source_module in source_modules:
        if source_module["source"] == "":
            source_module_name = source_module["name"]
            source_module_provider = source_module["provider"]
            source_module_version = source_module["version"]

            if source_module_name in target_module_names:
                print("\t", source_module_name, "module already exists, skipping...")
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
            api_target.registry_modules.create(new_module_payload)
            print(f"\t module %s created..." % source_module_name)

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
            new_module_version = api_target.registry_module.create_version(\
                source_module_name, source_module_provider, new_module_version_payload)["data"]
            print(f"\t module version %s created for module %s..." % (source_module_version, source_module_name))

            module_to_module_version_upload_map[source_module_name] = new_module_version["links"]["upload"]

    print("Registry module versions successfully migrated.")
    return module_to_module_version_upload_map


def migrate_module_version_files(\
        api_target, module_to_module_version_upload_map, module_to_file_path_map):
    print("Migrating module version files...")

    for module_name in module_to_file_path_map:
        # NOTE: The module_to_file_path_map must be created ahead of time
        # with a format of {"module_name":"path/to/file"}

        # Upload the module version file
        api_target.registry_modules.upload_version(\
            module_to_file_path_map[module_name], \
                module_to_module_version_upload_map[module_name])

        print(f"\t module version file for module %s uploaded..." % module_name)

    print("Module version files migrated.")


def delete_all(api_target):
    print("Deleting registry modules...")

    modules = api_target.registry_modules.list()["modules"]

    if modules:
        for module in modules:
            if module["source"] == "":
                print(f"\t deleting registry module %s..." % module["name"])
                api_target.registry_modules.destroy(module["name"])

    print("Registry modules deleted.")