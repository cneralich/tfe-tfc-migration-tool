
from .base_worker import TFCMigratorBaseWorker

class NotificationConfigsWorker(TFCMigratorBaseWorker):

    def __init__(self, api_source, api_target, vcs_connection_map, log_level):
        super().__init__(api_source, api_target, vcs_connection_map, log_level)

    def migrate_all(self, workspaces_map):
        self._logger.info("Migrating notification configs...")

        for workspace_id in workspaces_map:
            # Pull notifications from the old workspace
            source_notifications = self._api_source.notification_configs.list(workspace_id)["data"]

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
                self._api_target.notification_configs.create( \
                    workspaces_map[workspace_id], new_notification_payload)

                self._logger.info(f"Notification Config: %s, created." % notification_name)

        self._logger.info("Notification configs migrated.")


    def delete_all_from_target(self):
        self._logger.info("Deleting notification configs...")

        workspaces = self._api_target.workspaces.list()["data"]

        for workspace in workspaces:
            notifications = self._api_target.notification_configs.list(workspace["id"])["data"]

            for notification in notifications:
                self._api_target.notification_configs.destroy(notification["id"])
                self._logger.info(f"Notification Config: %s, deleted." % notification["attributes"]["name"])

        self._logger.info("Notification configs deleted.")