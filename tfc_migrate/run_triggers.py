

def migrate(api_source, api_target, workspaces_map):

    print("Migrating run triggers...")

    for source_workspace_id in workspaces_map:
        target_workspace_id = workspaces_map[source_workspace_id]
        workspace_run_trigger_filters = [
            {
                "keys": ["run-trigger", "type"],
                "value": "inbound"
            }
        ]

        # pull all inbound run triggers for the source workspace
        source_workspace_run_triggers = api_source.run_triggers.list(
            source_workspace_id, filters=workspace_run_trigger_filters,  page_size=100)["data"]

        if source_workspace_run_triggers:
            # pull all inbound run triggers for the target workspace
            target_workspace_run_triggers = api_target.run_triggers.list(\
                target_workspace_id, filters=workspace_run_trigger_filters)["data"]

            # compile a list of all originating workspace_ids for the target workspace
            target_workspace_run_trigger_workspace_ids = [target_workspace_run_trigger["relationships"]["sourceable"]["data"]["id"]\
                for target_workspace_run_trigger in target_workspace_run_triggers]

            for source_workspace_run_trigger in source_workspace_run_triggers:
                # pull the originating workspace_id for any inbound run trigger for the source workspace
                source_workspace_trigger_workspace_id = source_workspace_run_trigger["relationships"]["sourceable"]["data"]["id"]
                target_workspace_trigger_workspace_id = workspaces_map[source_workspace_trigger_workspace_id]

                if target_workspace_trigger_workspace_id in target_workspace_run_trigger_workspace_ids:
                    print("\t run trigger from workspace ID %s already exists in target workspace ID %s, skipping..." \
                        % (target_workspace_trigger_workspace_id, target_workspace_id))
                    continue

                # build the new run trigger payload
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
                api_target.run_triggers.create(
                    target_workspace_id, new_run_trigger_payload)

                print(f"\t run trigger created from originating workspace ID %s to target workspace ID %s..." \
                    % (target_workspace_trigger_workspace_id, target_workspace_id))

    print("Run triggers successfully migrated.")


def delete_all(api_target):
    print("Deleting run triggers...")

    workspaces = api_target.workspaces.list()["data"]

    if workspaces:
        for workspace in workspaces:
            workspace_id =  workspace["id"]

            workspace_run_trigger_filters = [
                {
                    "keys": ["run-trigger", "type"],
                    "value": "inbound"
                }
            ]

            run_triggers = api_target.run_triggers.list(\
                workspace_id, filters=workspace_run_trigger_filters)["data"]
            if run_triggers:
                for run_trigger in run_triggers:
                    print(f"\t deleting run trigger originating from workspace ID %s from target workspace ID %s..." \
                        % (run_trigger["relationships"]["sourceable"]["data"]["id"], workspace_id))
                    api_target.run_triggers.destroy(run_trigger["id"])

    print("Run triggers deleted.")