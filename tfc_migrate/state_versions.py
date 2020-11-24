import base64
import hashlib
import json
from urllib import request
from terrasnek import exceptions

def migrate_all(api_source, api_target, workspaces_map):
    print("Migrating all state versions...")

    for workspace_id in workspaces_map:
        source_workspace_name = api_source.workspaces.show(workspace_id=workspace_id)\
            ["data"]["attributes"]["name"]

        # TODO: paging
        source_state_filters = [
            {
                "keys": ["workspace", "name"],
                "value":  source_workspace_name
            },
            {
                "keys": ["organization", "name"],
                "value": api_source.get_org()
            }
        ]

        source_state_versions = api_source.state_versions.list(filters=source_state_filters)["data"]

        # TODO: paging
        target_state_filters = [
            {
                "keys": ["workspace", "name"],
                "value":  source_workspace_name
            },
            {
                "keys": ["organization", "name"],
                "value": api_target.get_org()
            }
        ]

        target_state_versions = \
            api_target.state_versions.list(filters=target_state_filters)["data"]
        target_state_version_serials = \
            [state_version["attributes"]["serial"] for state_version in target_state_versions]

        # NOTE: this is reversed to maintain the order present in the source
        for source_state_version in reversed(source_state_versions):
            source_state_url = source_state_version["attributes"]["hosted-state-download-url"]
            source_pull_state = request.urlopen(source_state_url)
            source_state_data = source_pull_state.read()
            source_state_serial = json.loads(source_state_data)["serial"]

            if source_state_serial in target_state_version_serials:
                print("\t state version %s for workspace %s exists, skipping..." % \
                    (source_state_serial, source_workspace_name))
                continue

            source_state_hash = hashlib.md5()
            source_state_hash.update(source_state_data)
            source_state_md5 = source_state_hash.hexdigest()
            source_state_b64 = base64.b64encode(source_state_data).decode("utf-8")

            # Build the new state payload
            create_state_version_payload = {
                "data": {
                    "type": "state-versions",
                    "attributes": {
                        "serial": source_state_serial,
                        "md5": source_state_md5,
                        "state": source_state_b64
                    }
                }
            }

            print("\t state version %s for workspace %s created..." % \
                (source_state_serial, source_workspace_name))

            # Migrate state to the target workspace
            api_target.workspaces.lock(workspaces_map[workspace_id], \
                {"reason": "migration script"})
            api_target.state_versions.create( \
                workspaces_map[workspace_id], create_state_version_payload)
            api_target.workspaces.unlock(workspaces_map[workspace_id])

    print("All state versions successfully migrated.")


def migrate_current(api_source, api_target, workspaces_map):
    print("Migrating current state versions...")

    for workspace_id in workspaces_map:
        source_workspace_name = api_source.workspaces.show(workspace_id=workspace_id)\
            ["data"]["attributes"]["name"]

        # Set proper state filters to pull state versions for each workspace
        current_version = None
        try:
            current_version = api_source.state_versions.get_current(workspace_id)["data"]
        except exceptions.TFCHTTPNotFound:
            print("\t", source_workspace_name, "doesn't have a current state version in source org, skipping...")
            continue

        state_url = current_version["attributes"]["hosted-state-download-url"]
        pull_state = request.urlopen(state_url)
        state_data = pull_state.read()
        state_serial = json.loads(state_data)["serial"]

        state_hash = hashlib.md5()
        state_hash.update(state_data)
        state_md5 = state_hash.hexdigest()
        state_b64 = base64.b64encode(state_data).decode("utf-8")

        # Build the new state payload
        create_state_version_payload = {
            "data": {
                "type": "state-versions",
                "attributes": {
                    "serial": state_serial,
                    "md5": state_md5,
                    "state": state_b64
                }
            }
        }

        print("\t current state version for workspace %s created..." % source_workspace_name)

        # Migrate state to the target workspace
        api_target.workspaces.lock(\
            workspaces_map[workspace_id], {"reason": "migration script"})
        api_target.state_versions.create(\
            workspaces_map[workspace_id], create_state_version_payload)
        api_target.workspaces.unlock(workspaces_map[workspace_id])

    print("Current state versions successfully migrated.")
