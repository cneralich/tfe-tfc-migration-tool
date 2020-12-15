"""
Module for Terraform Enterprise/Cloud Migration Worker: Policy Set Params.
"""

from .base_worker import TFCMigratorBaseWorker


class PolicySetParamsWorker(TFCMigratorBaseWorker):
    """
    A class to represent the worker that will migrate all policy set params
    from one TFC/E org to another TFC/E org.
    """

    def migrate_all(self, policy_sets_map, return_sensitive_variable_data=True):

        self._logger.info("Migrating policy set params...")

        sensitive_policy_set_parameter_data = []

        for policy_set_id in policy_sets_map:
            new_policy_set_id = policy_sets_map[policy_set_id]

            # Pull policy sets from the old organization
            policy_set_parameters = self._api_source.policy_set_params.list(policy_set_id)["data"]

            if policy_set_parameters:
                # NOTE: this is reversed to maintain the order present in the source
                for policy_set_parameter in reversed(policy_set_parameters):
                    policy_set_parameter_key = policy_set_parameter["attributes"]["key"]
                    policy_set_parameter_value = policy_set_parameter["attributes"]["value"]
                    policy_set_parameter_category = policy_set_parameter["attributes"]["category"]
                    policy_set_parameter_sensitive = policy_set_parameter["attributes"]["sensitive"]

                    # Build the new policy set parameter payload
                    new_policy_parameter_payload = {
                        "data": {
                            "type": "vars",
                            "attributes": {
                                "key": policy_set_parameter_key,
                                "value": policy_set_parameter_value,
                                "category": policy_set_parameter_category,
                                "sensitive": policy_set_parameter_sensitive
                            }
                        }
                    }

                    # Create the policy set parameter in the target organization
                    new_parameter = self._api_target.policy_set_params.create(
                        new_policy_set_id, new_policy_parameter_payload)["data"]

                    self._logger.info("Policy set param: %s, created.", policy_set_parameter_key)

                    new_parameter_id = new_parameter["id"]

                    if policy_set_parameter_sensitive and return_sensitive_variable_data:
                        policy_set_name = self._api_target.policy_sets.show(policy_set_id)\
                            ["data"]["attributes"]["name"]

                        # Build the sensitive policy set parameter map
                        parameter_data = {
                            "policy_set_name": policy_set_name,
                            "policy_set_id": new_policy_set_id,
                            "parameter_id": new_parameter_id,
                            "parameter_key": policy_set_parameter_key,
                            "parameter_value": policy_set_parameter_value,
                            "parameter_category": policy_set_parameter_category
                        }

                        sensitive_policy_set_parameter_data.append(parameter_data)

        self._logger.info("Policy set params migrated.")

        return sensitive_policy_set_parameter_data


    def migrate_sensitive(self):
        """
        NOTE: The sensitive_policy_set_parameter_data_map map must be manually created ahead of time.
        The easiest way to do this is to update the value for each variable in the list returned by
        the migrate_policy_set_parameters method
        """

        sensitive_policy_set_parameter_data_map = self._sensitive_data_map["sensitive_policy_set_parameter_data_map"]
        
        for sensitive_policy_set_parameter in sensitive_policy_set_parameter_data_map:
            # Build the new parameter payload
            update_policy_set_parameter_payload = {
                "data": {
                    "id": sensitive_policy_set_parameter["parameter_id"],
                    "attributes": {
                        "key": sensitive_policy_set_parameter["parameter_key"],
                        "value": sensitive_policy_set_parameter["parameter_value"],
                        "category": "policy-set",
                        "sensitive": "true"
                    },
                    "type": "vars"
                }
            }

            # Update the sensitive parameter value in the policy set
            self._api_target.policy_set_params.update(
                sensitive_policy_set_parameter["policy_set_id"], \
                    sensitive_policy_set_parameter["parameter_id"], \
                        update_policy_set_parameter_payload)


    def delete_all_from_target(self):
        self._logger.info("Deleting policy set params...")

        # TODO: handle paging
        policy_sets = self._api_target.policy_sets.list( \
            page_size=50, include="policies,workspaces")["data"]

        if policy_sets:
            for policy_set in policy_sets:
                params = self._api_target.policy_set_params.list(policy_set["id"])["data"]

                for param in params:
                    self._logger.info("Policy set param: %s, deleted..", param["attributes"]["key"])
                    self._api_target.policy_set_params.destroy(policy_set["id"], param["id"])

        self._logger.info("Policy set params deleted.")
