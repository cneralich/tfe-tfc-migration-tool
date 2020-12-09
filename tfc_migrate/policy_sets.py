

def migrate(\
    api_source, api_target, tfe_vcs_connection_map, workspaces_map, policies_map):

    # Pull policy sets from the source organization
    # TODO: handle paging
    source_policy_sets = api_source.policy_sets.list(
        page_size=50, include="policies,workspaces")["data"]
    target_policy_sets = api_target.policy_sets.list(
        page_size=50, include="policies,workspaces")["data"]

    target_policy_sets_data = {}
    for target_policy_set in target_policy_sets:
        target_policy_sets_data[target_policy_set["attributes"]["name"]] = target_policy_set["id"]

    print("Migrating policy sets...")

    policy_sets_map = {}
    for source_policy_set in source_policy_sets:
        source_policy_set_name = source_policy_set["attributes"]["name"]

        if source_policy_set_name in target_policy_sets_data:
            policies_map[source_policy_set["id"]] = target_policy_sets_data[source_policy_set_name]
            print("\t", source_policy_set_name, "policy set already exists, skipping...")
            continue

        new_policy_set_payload = {
            "data": {
                "type": "policy-sets",
                "attributes": {
                    "name": source_policy_set_name,
                    "description": source_policy_set["attributes"]["description"],
                    "global": source_policy_set["attributes"]["global"]
                },
                "relationships": {
                }
            }
        }

        # TODO: handle non VCS backed policies
        if "policies-path" in source_policy_set["attributes"]:
            new_policy_set_payload["data"]["attributes"]["policies-path"] = \
                source_policy_set["attributes"]["policies-path"]

        if source_policy_set["attributes"]["versioned"]:
            oauth_token_id = ""
            for tfe_vcs_connection in tfe_vcs_connection_map:
                if tfe_vcs_connection["source"] == source_policy_set["attributes"]["vcs-repo"]["oauth-token-id"]:
                    oauth_token_id = tfe_vcs_connection["target"]

            new_policy_set_payload["data"]["attributes"]["vcs-repo"] = {
                "branch": source_policy_set["attributes"]["vcs-repo"]["branch"],
                "identifier": source_policy_set["attributes"]["vcs-repo"]["identifier"],
                "ingress-submodules": source_policy_set
                ["attributes"]["vcs-repo"]["ingress-submodules"],
                "oauth-token-id": oauth_token_id
            }
        else:
            policy_ids = source_policy_set["relationships"]["policies"]["data"]

            for policy_id in policy_ids:
                policy_id["id"] = policies_map[policy_id["id"]]

            new_policy_set_payload["data"]["relationships"]["policies"] = {
                "data": policy_ids
            }

        if not source_policy_set["attributes"]["global"]:
            workspace_ids = source_policy_set["relationships"]["workspaces"]["data"]

            for workspace_id in workspace_ids:
                workspace_id["id"] = workspaces_map[workspace_id["id"]]

            # Build the new policy set payload
            new_policy_set_payload["data"]["relationships"]["workspaces"] = {
                "data": workspace_ids
            }

        # Create the policy set in the target organization
        new_policy_set = api_target.policy_sets.create(new_policy_set_payload)
        print(f"\t policy set %s created..." % source_policy_set_name)

        policy_sets_map[source_policy_set["id"]] = new_policy_set["data"]["id"]

    print("Policy sets successfully migrated.")

    return policy_sets_map


def delete_all(api_target):
    print("Deleting policy sets...")

    # TODO: handle paging
    policy_sets = api_target.policy_sets.list(page_size=50, include="policies,workspaces")["data"]

    for policy_set in policy_sets:
        print(f"\t deleting policy set %s..." % policy_set["attributes"]["name"])
        api_target.policy_sets.destroy(policy_set["id"])

    print("Policy sets deleted.")
