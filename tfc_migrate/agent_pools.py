"""
Module for Terraform Enterprise/Cloud Migration Worker: Agent Pools.
"""

from .base_worker import TFCMigratorBaseWorker


class AgentPoolsWorker(TFCMigratorBaseWorker):
    """
    A class to represent the worker that will migrate all agent pools from one
    TFC/E org to another TFC/E org.
    """

    _api_module_used = "agents"
    _required_entitlements = ["agents"]

    def migrate(self):
        """
        Function to migrate all agent pools from one TFC/E org to another TFC/E org.
        """

        self._logger.info("Migrating agent pools...")

        # Only perform this migration if it's TFC to TFC, otherwise it won't work.
        agent_pools_map = {}
        # Fetch agent pools from existing org
        source_agent_pools = self._api_source.agents.list_pools()["data"]
        target_agent_pools = self._api_target.agents.list_pools()["data"]

        target_agent_pool_data = {}
        for target_agent_pool in target_agent_pools:
            target_agent_pool_data[target_agent_pool["attributes"]["name"]] = \
                target_agent_pool["id"]

        for source_agent_pool in source_agent_pools:
            source_agent_pool_name = source_agent_pool["attributes"]["name"]
            source_agent_pool_id = source_agent_pool["id"]

            if source_agent_pool_name in target_agent_pool_data:
                agent_pools_map[source_agent_pool_id] = \
                    target_agent_pool_data[source_agent_pool_name]
                self._logger.info(\
                    "Agent pool: %s, exists. Skipped.", source_agent_pool_name)
                continue

            # Build the new agent pool payload
            new_agent_pool_payload = {
                "data": {
                    "type": "agent-pools",
                    "attributes": {
                        "name": source_agent_pool_name
                    }
                }
            }

            # Create Agent Pool in the target org
            new_agent_pool = self._api_target.agents.create_pool(new_agent_pool_payload)
            new_agent_pool_id = new_agent_pool["data"]["id"]
            agent_pools_map[source_agent_pool_id] = new_agent_pool_id

        self._logger.info("Agent pools migrated.")
        return agent_pools_map

    def delete_all_from_target(self):
        """
        Function to delete all agent pools from the target TFC/E org.
        """

        self._logger.info("Deleting agent pools...")

        agent_pools = self._api_target.agents.list_pools()["data"]

        if agent_pools:
            for agent_pool in agent_pools:
                if agent_pool["attributes"]["name"] != "Default":
                    self._logger.info("Agent pool: %s, deleted.", agent_pool["attributes"]["name"])
                    self._api_target.agents.destroy_pool(agent_pool["id"])

        self._logger.info("Agent pools deleted.")
