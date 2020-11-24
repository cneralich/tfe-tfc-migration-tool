

def migrate(api_source, api_target, workspaces_map):
    print("Migrating notification configs...")

    for workspace_id in workspaces_map:
        # Pull notifications from the old workspace
        source_notifications = api_source.notification_configs.list(workspace_id)["data"]

        """
        NOTE: Notification configuration endpoints will not throw an error if you
        try to create one with a duplicate name. This is because a workspace can
        have up to 20 of them.
        """

        for source_notification in source_notifications:
            notification_name = source_notification["attributes"]["name"]
            destination_type = source_notification["attributes"]["destination-type"]

            new_notification_payload = {
                "data": {
                    "type": "notification-configurations",
                    "attributes": {
                        "destination-type": destination_type,
                        "enabled": source_notification["attributes"]["enabled"],
                        "name": notification_name,
                        "triggers": source_notification["attributes"]["triggers"]
                    }
                }
            }

            if destination_type == "email":
                new_notification_payload["data"]["relationships"] = {
                    "users": {
                        "data":  source_notification["relationships"]["users"]["data"]
                    }
                }

            else:
                new_notification_payload["data"]["attributes"]["token"] = source_notification["attributes"]["token"]
                new_notification_payload["data"]["attributes"]["url"] = source_notification["attributes"]["url"]

            # TODO: add handling for failed webhook response
            # Add notifications to the target workspace
            api_target.notification_configs.create( \
                workspaces_map[workspace_id], new_notification_payload)

            print(f"\t notification config %s created..." % notification_name)

    print("Notification configs successfully migrated.")


def delete_all(api_target):
    print("Deleting notification configs...")

    workspaces = api_target.workspaces.list()["data"]

    for workspace in workspaces:
        notifications = api_target.notification_configs.list(workspace["id"])["data"]

        for notification in notifications:
            print(f"\t deleting notification config %s created..." % notification["attributes"]["name"])
            api_target.notification_configs.destroy(notification["id"])

    print("Notification configs deleted.")