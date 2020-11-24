

def migrate(api_source, api_target):
    print("Migrating agent pools...")

    # Fetch agent pools from existing org
    source_agent_pools = api_source.agents.list_pools()["data"]
    target_agent_pools = api_target.agents.list_pools()["data"]
    agent_pools_map = {}

    if source_agent_pools and "app.terraform.io" in api_target.get_url():
        target_agent_pool_data = {}
        for target_agent_pool in target_agent_pools:
            target_agent_pool_data[target_agent_pool["attributes"]["name"]] = target_agent_pool["id"]

        for source_agent_pool in source_agent_pools:
            source_agent_pool_name = source_agent_pool["attributes"]["name"]
            source_agent_pool_id = source_agent_pool["id"]

            if source_agent_pool_name in target_agent_pool_data:
                agent_pools_map[source_agent_pool_id] = target_agent_pool_data[source_agent_pool_name]
                print("\t", source_agent_pool_name, "agent pool already exists, skipping...")
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
            new_agent_pool = api_target.agents.create_pool(new_agent_pool_payload)
            new_agent_pool_id = new_agent_pool["data"]["id"]
            agent_pools_map[source_agent_pool_id] = new_agent_pool_id

    print("Agent pools successfully migrated.")
    return agent_pools_map

def delete_all(api_target):
    print("Deleting agent pools...")

    agent_pools = api_target.agents.list_pools()["data"]

    if agent_pools:
        for agent_pool in agent_pools:
            if agent_pool["attributes"]["name"] != "Default":
                print(f"\t deleting agent pool %s..." % agent_pool["attributes"]["name"])
                api_target.agents.destroy(agent_pool["id"])

    print("Agent pools deleted.")
