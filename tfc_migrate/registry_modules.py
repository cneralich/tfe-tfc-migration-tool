

# TODO: Add support for modules uploaded via the API
def migrate(api_source, api_target, tfe_vcs_connection_map):

    print("Migrating registry modules...")

    source_modules = api_source.registry_modules.list()["modules"]
    target_modules = api_target.registry_modules.list()["modules"]
    target_module_names = \
        [target_module["name"] for target_module in target_modules]

    for source_module in source_modules:
        if source_module["source"] != "":
            source_module_name = source_module["name"]

            if source_module_name in target_module_names:
                print("\t", source_module_name, "module already exists, skipping...")
                continue

            source_module_data = \
                api_source.registry_modules.show(\
                    source_module_name, source_module["provider"])["data"]

            oauth_token_id = ""
            for tfe_vcs_connection in tfe_vcs_connection_map:
                if tfe_vcs_connection["source"] == source_module_data["attributes"]["vcs-repo"]["oauth-token-id"]:
                    oauth_token_id = tfe_vcs_connection["target"]

            # Build the new module payload
            new_module_payload = {
                "data": {
                    "attributes": {
                        "vcs-repo": {
                            "identifier": source_module_data["attributes"]["vcs-repo"]["identifier"],
                            # NOTE that if the VCS the module was originally connected to has been
                            # deleted, it will not return an OAuth Token ID and this will error.
                            "oauth-token-id": oauth_token_id,
                            "display_identifier": source_module_data\
                                ["attributes"]["vcs-repo"]["display-identifier"]
                        }
                    },
                    "type": "registry-modules"
                }
            }

            # Create the module in the target organization
            api_target.registry_modules.publish_from_vcs(new_module_payload)

    print("Registry modules successfully migrated.")


def delete_all(api_target):
    print("Deleting registry modules...")

    modules = api_target.registry_modules.list()["modules"]

    if modules:
        for module in modules:
            if module["source"] != "":
                print(f"\t deleting registry module %s..." % module["name"])
                api_target.registry_modules.destroy(module["name"])

    print("Registry modules deleted.")
