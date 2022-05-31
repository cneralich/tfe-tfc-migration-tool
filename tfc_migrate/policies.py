"""
Module for Terraform Enterprise/Cloud Migration Worker: Policies.
"""

from .base_worker import TFCMigratorBaseWorker


class PoliciesWorker(TFCMigratorBaseWorker):
    """
    A class to represent the worker that will migrate all policies from one
    TFC/E org to another TFC/E org.
    """

    _api_module_used = "policies"
    _required_entitlements = ["sentinel"]

    def migrate(self):
        """
        Function to migrate all policies from one TFC/E org to another TFC/E org.
        """

        self._logger.info("Migrating policies...")

        # Pull policies from the old organization
        source_policies = self._api_source.policies.list_all()["data"]
        target_policies = self._api_target.policies.list_all()["data"]

        target_policies_data = {}
        for target_policy in target_policies:
            target_policies_data[target_policy["attributes"]["name"]] = target_policy["id"]

        policies_map = {}

        for source_policy in source_policies:
            source_policy_name = source_policy["attributes"]["name"]
            source_policy_id = source_policy["id"]

            if source_policy_name in target_policies_data:
                policies_map[source_policy_id] = target_policies_data[source_policy_name]
                self._logger.info("Policy: %s, exists. Skipped.", source_policy_name)
                continue

            source_policy_text = self._api_source.policies.get_policy_text(source_policy["id"])

            # Build the new policy payload
            new_policy_payload = {
                "data": {
                    "attributes": {
                        "name": source_policy_name,
                        "description": source_policy["attributes"]["description"],
                        "enforce": [
                            {
                                "path": source_policy["attributes"]["enforce"][0]["path"],
                                "mode": source_policy["attributes"]["enforce"][0]["mode"]
                            }
                        ],
                    },
                    "type": "policies"
                }
            }

            new_policy_id = None

            # Create the policy in the target organization
            new_policy = self._api_target.policies.create(new_policy_payload)
            new_policy_id = new_policy["data"]["id"]
            policies_map[source_policy_id] = new_policy_id

            self._logger.info("Policy: %s, created.", source_policy_name)

            # Upload the policy content to the target policy in the target organization
            self._api_target.policies.upload(new_policy_id, source_policy_text)

        self._logger.info("Policies migrated.")

        return policies_map


    def delete_all_from_target(self):
        """
        Function to delete all policies from the target TFC/E org.
        """

        self._logger.info("Deleting policies...")

        policies = self._api_target.policies.list_all()["data"]

        for policy in policies:
            self._api_target.policies.destroy(policy["id"])
            self._logger.info("Policy: %s, deleted.", policy["attributes"]["name"])

        self._logger.info("Policies deleted.")
