"""
Module for Terraform Enterprise/Cloud Migration Worker: Policy Sets.
"""

from .base_worker import TFCMigratorBaseWorker


class PolicySetsWorker(TFCMigratorBaseWorker):
    """
    A class to represent the worker that will migrate all policy sets from one
    TFC/E org to another TFC/E org.
    """

    _api_module_used = "policy_sets"
    _required_entitlements = ["sentinel"]

    def migrate_all(self, workspaces_map, policies_map):
        """
        Function to migrate all policy sets from one TFC/E org to another TFC/E org.
        """

        # Pull policy sets from the source organization
        source_policy_sets = self._api_source.policy_sets.list_all(include="policies,workspaces")
        target_policy_sets = self._api_target.policy_sets.list_all(include="policies,workspaces")

        target_policy_sets_data = {}
        for target_policy_set in target_policy_sets:
            target_policy_sets_data[target_policy_set["attributes"]["name"]] = \
                target_policy_set["id"]

        self._logger.info("Migrating policy sets...")

        policy_sets_map = {}
        for source_policy_set in source_policy_sets:
            source_policy_set_name = source_policy_set["attributes"]["name"]

            if source_policy_set_name in target_policy_sets_data:
                policy_sets_map[source_policy_set["id"]] = \
                    target_policy_sets_data[source_policy_set_name]
                self._logger.info("Policy set: %s, exists. Skipped.", source_policy_set_name)
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

            if "policies-path" in source_policy_set["attributes"]:
                new_policy_set_payload["data"]["attributes"]["policies-path"] = \
                    source_policy_set["attributes"]["policies-path"]

            if source_policy_set["attributes"]["versioned"]:
                oauth_token_id = ""
                for vcs_connection in self._vcs_connection_map:
                    if vcs_connection["source"] == \
                        source_policy_set["attributes"]["vcs-repo"]["oauth-token-id"]:
                        oauth_token_id = vcs_connection["target"]

                new_policy_set_payload["data"]["attributes"]["vcs-repo"] = {
                    "branch": source_policy_set["attributes"]["vcs-repo"]["branch"],
                    "identifier": source_policy_set["attributes"]["vcs-repo"]["identifier"],
                    "ingress-submodules": source_policy_set\
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
            new_policy_set = self._api_target.policy_sets.create(new_policy_set_payload)
            self._logger.info("Policy set: %s, created.", source_policy_set_name)

            policy_sets_map[source_policy_set["id"]] = new_policy_set["data"]["id"]

        self._logger.info("Policy sets migrated.")

        return policy_sets_map


    def delete_all_from_target(self):
        """
        Function to delete all policy sets from the target TFC/E org.
        """

        self._logger.info("Deleting policy sets...")

        policy_sets = self._api_target.policy_sets.list_all(include="policies,workspaces")

        for policy_set in policy_sets:
            self._api_target.policy_sets.destroy(policy_set["id"])
            self._logger.info("Policy set: %s, deleted.", policy_set["attributes"]["name"])

        self._logger.info("Policy sets deleted.")
