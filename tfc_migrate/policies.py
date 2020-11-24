from urllib import request

def migrate(api_source, api_target):

    print("Migrating policies...")

    # Pull policies from the old organization
    source_policies = api_source.policies.list()["data"]
    target_policies = api_target.policies.list()["data"]

    target_policies_data = {}
    for target_policy in target_policies:
        target_policies_data[target_policy["attributes"]["name"]] = target_policy["id"]

    policies_map = {}

    for source_policy in source_policies:
        source_policy_name = source_policy["attributes"]["name"]
        source_policy_id = source_policy["id"]

        if source_policy_name in target_policies_data:
            policies_map[source_policy_id] = target_policies_data[source_policy_name]
            print("\t", source_policy_name, "policy already exists, skipping...")
            continue

        headers = {
            "Authorization": "Bearer %s" % (api_source.get_token()),
            "Content-Type": "application/vnd.api+json"
        }

        policy_download_url = "%s/api/v2/policies/%s/download" % \
            (api_source.get_url(), source_policy_id)

        # Retrieve the policy content
        policy_request = request.Request(policy_download_url, headers=headers)
        pull_policy = request.urlopen(policy_request)
        policy_data = pull_policy.read()
        policy_b64 = policy_data.decode("utf-8")

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
        new_policy = api_target.policies.create(new_policy_payload)
        new_policy_id = new_policy["data"]["id"]
        policies_map[source_policy_id] = new_policy_id

        print(f"\t policy %s created..." % source_policy_name)

        # Upload the policy content to the target policy in the target organization
        api_target.policies.upload(new_policy_id, policy_b64)

    print("Policies successfully migrated.")

    return policies_map


def delete_all(api_target):
    print("Deleting policies...")

    policies = api_target.policies.list()["data"]

    if policies:
        for policy in policies:
            print(f"\t deleting policy %s..." % policy["attributes"]["name"])
            api_target.policies.destroy(policy["id"])

    print("Policies deleted.")