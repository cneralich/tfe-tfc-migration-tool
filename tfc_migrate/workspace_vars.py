

def migrate(\
        api_source, api_target, workspaces_map, \
            return_sensitive_variable_data=True):

    print("Migrating workspace variables...")

    sensitive_variable_data = []
    for source_workspace_id in workspaces_map:
        target_workspace_id = workspaces_map[source_workspace_id]
        target_workspace_name = api_target.workspaces.show(workspace_id=target_workspace_id)["data"]["attributes"]["name"]


        # Pull variables from the old workspace
        source_workspace_vars = api_source.workspace_vars.list(source_workspace_id)["data"]
        # Get the variables that may already exist in the target workspace from a previous run
        existing_target_workspace_vars = api_target.workspace_vars.list(target_workspace_id)["data"]

        target_workspace_var_data = {}
        for target_workspace_var in existing_target_workspace_vars:
            target_workspace_var_data[target_workspace_var["attributes"]["key"]] = target_workspace_var["id"]

        # NOTE: this is reversed to maintain the order present in the source
        for source_variable in reversed(source_workspace_vars):
            target_variable_key = source_variable["attributes"]["key"]
            target_variable_value = source_variable["attributes"]["value"]
            target_variable_category = source_variable["attributes"]["category"]
            target_variable_hcl = source_variable["attributes"]["hcl"]
            target_variable_description = source_variable["attributes"]["description"]
            target_variable_sensitive = source_variable["attributes"]["sensitive"]
            
            if target_variable_sensitive:
                sensitive_variable_map = {
                    "workspace_name": target_workspace_name,
                    "workspace_id": target_workspace_id,
                    "variable_key": target_variable_key,
                    "variable_value": target_variable_value,
                    "variable_description": target_variable_description,
                    "variable_category": target_variable_category,
                    "variable_hcl": target_variable_hcl
                }

            # Make sure we haven't already created this variable in a past run
            if target_variable_key in target_workspace_var_data:
                print("\t variable %s already exists in workspace %s, skipping..." \
                        % (target_variable_key, target_workspace_name))
                if target_variable_sensitive and return_sensitive_variable_data:
                    sensitive_variable_map["variable_id"] = target_workspace_var_data[target_variable_key]
                    # Build the sensitive variable map
                    sensitive_variable_data.append(sensitive_variable_map)
                continue

            # Build the new variable payload
            new_variable_payload = {
                "data": {
                    "type": "vars",
                    "attributes": {
                        "key": target_variable_key,
                        "value": target_variable_value,
                        "description": target_variable_description,
                        "category": target_variable_category,
                        "hcl": target_variable_hcl,
                        "sensitive": target_variable_sensitive
                    }
                }
            }

            # Migrate variables to the target Workspace
            target_variable = api_target.workspace_vars.create(
                target_workspace_id, new_variable_payload)["data"]
            target_variable_id = target_variable["id"]

            if target_variable_sensitive and return_sensitive_variable_data:
                sensitive_variable_map["variable_id"] = target_variable_id
                # Build the sensitive variable map
                sensitive_variable_data.append(sensitive_variable_map)

    return sensitive_variable_data


def migrate_sensitive(api_target, sensitive_variable_data_map):
    """
    NOTE: The sensitive_variable_data_map map must be created ahead of time. The easiest way to
    do this is to update the value for each variable in the list returned by the
    migrate_workspace_variables method
    """

    for sensitive_variable in sensitive_variable_data_map:
        # Build the new variable payload
        update_variable_payload = {
            "data": {
                "id": sensitive_variable["variable_id"],
                "attributes": {
                    "key": sensitive_variable["variable_key"],
                    "value": sensitive_variable["variable_value"],
                    "description": sensitive_variable["variable_description"],
                    "category": sensitive_variable["variable_category"],
                    "hcl": sensitive_variable["variable_hcl"],
                    "sensitive": "true"
                },
                "type": "vars"
            }
        }

        # Update the sensitive variable value in the target workspace
        api_target.workspace_vars.update(
            sensitive_variable["workspace_id"], \
                sensitive_variable["variable_id"], update_variable_payload)

    print("Workspace variables successfully migrated.")


def delete_all(api_target):
    print("Deleting workspace variables...")

    target_workspaces = api_target.workspaces.list()["data"]

    if target_workspaces:
        for target_workspace in target_workspaces:
            target_workspace_id = target_workspace["id"]
            target_workspace_variables = api_target.workspace_vars.list(target_workspace_id)["data"]
            if target_workspace_variables:
                for target_workspace_variable in target_workspace_variables:
                    print(f"\t deleting workspace variable %s from workspace %s..." \
                        % (target_workspace_variable["attributes"]["key"], target_workspace["attributes"]["name"]))
                    api_target.workspace_vars.destroy(target_workspace_id, target_workspace_variable["id"])

    print("Workspace variables deleted.")