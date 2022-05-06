"""
Module for Terraform Enterprise/Cloud Migration Worker: Run Triggers.
"""

from .base_worker import TFCMigratorBaseWorker


class RunTriggersWorker(TFCMigratorBaseWorker):
    """
    A class to represent the worker that will migrate all run triggers
    from one TFC/E org to another TFC/E org.
    """

    _api_module_used = "run_triggers"
    _required_entitlements = []

    def migrate(self, workspaces_map):
        """
        Function to migrate all run triggers from one TFC/E org to another TFC/E org.
        """

        self._logger.info("Migrating run triggers...")

        for source_workspace_id in workspaces_map:
            target_workspace_id = workspaces_map[source_workspace_id]
            workspace_run_trigger_filters = [
                {
                    "keys": ["run-trigger", "type"],
                    "value": "inbound"
                }
            ]

            # Pull all inbound run triggers for the source workspace
            source_workspace_run_triggers = self._api_source.run_triggers.list_all(
                source_workspace_id, filters=workspace_run_trigger_filters)

            if source_workspace_run_triggers:
                # pull all inbound run triggers for the target workspace
                target_workspace_run_triggers = self._api_target.run_triggers.list_all(\
                    target_workspace_id, filters=workspace_run_trigger_filters)

                # Compile a list of all originating workspace_ids for the target workspace
                target_workspace_run_trigger_workspace_ids = \
                    [target_workspace_run_trigger["relationships"]["sourceable"]["data"]["id"]\
                        for target_workspace_run_trigger in target_workspace_run_triggers]

                for source_workspace_run_trigger in source_workspace_run_triggers:
                    # Get originating workspace_id for any inbound trigger for the source workspace
                    source_workspace_trigger_workspace_id = \
                        source_workspace_run_trigger["relationships"]["sourceable"]["data"]["id"]
                    if source_workspace_trigger_workspace_id in workspaces_map:
                        target_workspace_trigger_workspace_id = \
                            workspaces_map[source_workspace_trigger_workspace_id]
                    else:
                        self._logger.info(\
                            "Run trigger from workspace ID: %s cannot be added because trigger workspace does not exist. Skipped.", \
                                    source_workspace_trigger_workspace_id)
                        continue
                    if target_workspace_trigger_workspace_id in \
                        target_workspace_run_trigger_workspace_ids:
                        self._logger.info("Run Trigger: %s, in workspace ID %s exists. Skipped.", \
                            target_workspace_trigger_workspace_id, target_workspace_id)
                        continue

                    # Build the new run trigger payload
                    new_run_trigger_payload = {
                        "data": {
                            "relationships": {
                                "sourceable": {
                                    "data": {
                                        "id": target_workspace_trigger_workspace_id,
                                        "type": "workspaces"
                                    }
                                }
                            }
                        }
                    }

                    # add run triggers to the target workspace
                    self._api_target.run_triggers.create(\
                        target_workspace_id, new_run_trigger_payload)

                    self._logger.info(\
                        "Run trigger workspace ID: %s, to workspace ID: %s, created.", \
                            target_workspace_trigger_workspace_id, target_workspace_id)

        self._logger.info("Run triggers migrated.")


    def delete_all_from_target(self):
        """
        Function to delete all run triggers from the target TFC/E org.
        """

        self._logger.info("Deleting run triggers...")

        workspaces = self._api_target.workspaces.list()["data"]

        if workspaces:
            for workspace in workspaces:
                workspace_id = workspace["id"]

                workspace_run_trigger_filters = [
                    {
                        "keys": ["run-trigger", "type"],
                        "value": "inbound"
                    }
                ]

                run_triggers = self._api_target.run_triggers.list(\
                    workspace_id, filters=workspace_run_trigger_filters)["data"]
                if run_triggers:
                    for run_trigger in run_triggers:
                        self._api_target.run_triggers.destroy(run_trigger["id"])
                        self._logger.info("Run Trigger: %s, deleted.", \
                            run_trigger["relationships"]["sourceable"]["data"]["id"])

        self._logger.info("Run triggers deleted.")
