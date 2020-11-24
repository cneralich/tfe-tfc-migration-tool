from terrasnek import exceptions

def migrate(api_source, api_target, teams_map):
    print("Migrating org memberships...")

    # Set proper membership filters
    active_member_filter = [
        {
            "keys": ["status"],
            "value": "active"
        }
    ]

    source_org_members = api_source.org_memberships.list_for_org( \
        filters=active_member_filter, page=0, page_size=100)["data"]
    target_org_members = api_target.org_memberships.list_for_org( \
        page=0, page_size=100)["data"]

    target_org_members_data = {}
    for target_org_member in target_org_members:
        target_org_members_data[target_org_member["attributes"]["email"]] = target_org_member["id"]

    org_membership_map = {}

    for source_org_member in source_org_members:
        source_org_member_email = source_org_member["attributes"]["email"]
        source_org_member_id = source_org_member["relationships"]["user"]["data"]["id"]

        if source_org_member_email in target_org_members_data:
            org_membership_map[source_org_member_id] = target_org_members_data[source_org_member_email]
            # TODO: should the team membership be checked for an existing org member and updated to match
            # the source_org value if different?
            print("\t", source_org_member_email, " member already exists, skipping...")
            continue

        for team in source_org_member["relationships"]["teams"]["data"]:
            team["id"] = teams_map[team["id"]]

        # Build the new user invite payload
        new_user_invite_payload = {
            "data": {
                "attributes": {
                    "email": source_org_member_email
                },
                "relationships": {
                    "teams": {
                        "data": source_org_member["relationships"]["teams"]["data"]
                    },
                },
                "type": "organization-memberships"
            }
        }

        # try statement required in case a user account tied to the email address does not yet exist
        try:
            target_org_member = api_target.org_memberships.invite( \
                new_user_invite_payload)["data"]
        except:
            org_membership_map[source_org_member["relationships"]["user"]["data"]["id"]] = \
                None

            print("\t", "A user account tied to", source_org_member_email, "does not exist, skipping...")
            continue

        new_user_id = target_org_member["relationships"]["user"]["data"]["id"]
        org_membership_map[source_org_member["relationships"]["user"]["data"]["id"]] = \
            new_user_id

    print("Org memberships migrated.")

    return org_membership_map

def delete_all(api_target):
    print("Deleting organization members...")

    org_members = api_target.org_memberships.list_for_org( \
        page=0, page_size=100)["data"]

    if org_members:
        for org_member in org_members:
            try:
                api_target.org_memberships.remove(org_member["id"])
                print(f"\t removed org member %s..." % org_member["attributes"]["email"])
            except exceptions.TFCHTTPUnclassified as unclassified:
                # Rather than add some complicated logic, if we get the error message saying
                # we can't delete ourselves from a group we own, just skip it. Otherwise
                # raise the exception. You will still see an error in the logs.
                if "remove yourself" not in str(unclassified):
                    raise unclassified

    print("Organization members deleted.")