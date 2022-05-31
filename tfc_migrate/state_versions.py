"""
Module for Terraform Enterprise/Cloud Migration Worker: State Versions.
"""

import base64
import hashlib
import json
import ssl
from urllib import request
from terrasnek import exceptions

from .base_worker import TFCMigratorBaseWorker


class StateVersionsWorker(TFCMigratorBaseWorker):
    """
    A class to represent the worker that will migrate all state versions from
    one TFC/E org to another TFC/E org.
    """

    _api_module_used = "state_versions"
    _required_entitlements = []

    def migrate(self, workspaces_map, tfe_verify_source):
        """
        Function to migrate all state versions from one TFC/E org to another TFC/E org.
        """

        self._logger.info("Migrating all state versions...")

        context = ssl.create_default_context()

        if tfe_verify_source is False:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        for workspace_id in workspaces_map:
            source_workspace_name = self._api_source.workspaces.show(workspace_id=workspace_id)\
                ["data"]["attributes"]["name"]

            source_state_filters = [
                {
                    "keys": ["workspace", "name"],
                    "value":  source_workspace_name
                },
                {
                    "keys": ["organization", "name"],
                    "value": self._api_source.get_org()
                }
            ]

            source_state_versions = \
                self._api_source.state_versions.list_all(filters=source_state_filters)

            target_state_filters = [
                {
                    "keys": ["workspace", "name"],
                    "value":  source_workspace_name
                },
                {
                    "keys": ["organization", "name"],
                    "value": self._api_target.get_org()
                }
            ]

            target_state_versions = \
                self._api_target.state_versions.list_all(filters=target_state_filters)
            target_state_version_serials = \
                [state_version["attributes"]["serial"] for state_version in target_state_versions]

            # NOTE: this is reversed to maintain the order present in the source
            for source_state_version in reversed(source_state_versions):
                source_state_url = source_state_version["attributes"]["hosted-state-download-url"]
                source_pull_state = request.urlopen(source_state_url, data=None, context=context)
                source_state_data = source_pull_state.read()
                source_state_json = json.loads(source_state_data)
                source_state_serial = source_state_json["serial"]
                source_state_lineage = source_state_json["lineage"]

                if target_state_version_serials and source_state_serial <= target_state_version_serials[0]:
                    self._logger.info( \
                        "State Version: %s, for workspace %s, exists or is older than the current version. Skipped.", \
                            source_state_serial, source_workspace_name)
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
                            "lineage": source_state_lineage,
                            "state": source_state_b64
                        }
                    }
                }

                # Migrate state to the target workspace
                # TODO: Add try statement and logging in case a workspace is already locked and this fails
                self._api_target.workspaces.lock(workspaces_map[workspace_id], \
                    {"reason": "migration script"})
                self._api_target.state_versions.create( \
                    workspaces_map[workspace_id], create_state_version_payload)
                self._api_target.workspaces.unlock(workspaces_map[workspace_id])

                self._logger.info("State Version: %s, for workspace %s created.", \
                    source_state_serial, source_workspace_name)

        self._logger.info("All state versions migrated.")


    def migrate_current(self, workspaces_map, tfe_verify_source):
        """
        Function to migrate current state versions from one TFC/E org to another TFC/E org.
        """

        self._logger.info("Migrating current state versions...")

        context = ssl.create_default_context()

        if tfe_verify_source is False:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        for workspace_id in workspaces_map:
            source_workspace_name = self._api_source.workspaces.show(workspace_id=workspace_id)\
                ["data"]["attributes"]["name"]

            # Set proper state filters to pull state versions for each workspace
            current_source_version = None

            target_state_filters = [
                {
                    "keys": ["workspace", "name"],
                    "value":  source_workspace_name
                },
                {
                    "keys": ["organization", "name"],
                    "value": self._api_target.get_org()
                }
            ]

            target_state_versions = \
                self._api_target.state_versions.list_all(filters=target_state_filters)["data"]
            target_state_version_serials = \
                [state_version["attributes"]["serial"] for state_version in target_state_versions]

            try:
                current_source_version = self._api_source.state_versions.get_current(workspace_id)["data"]
                current_source_version_number = current_source_version["attributes"]["serial"]
            except exceptions.TFCHTTPNotFound:
                self._logger.info(\
                    "Current state version for workspace: %s, does not exist. Skipped.", \
                        source_workspace_name)
                continue

            if target_state_version_serials and current_source_version_number <= target_state_version_serials[0]:
                self._logger.info( \
                    "State Version: %s, for workspace %s, exists or is older than the current version. Skipped.", \
                        current_source_version_number, source_workspace_name)
                continue

            source_state_url = current_source_version["attributes"]["hosted-state-download-url"]
            source_pull_state = request.urlopen(source_state_url, data=None, context=context)
            source_state_data = source_pull_state.read()
            source_state_json = json.loads(source_state_data)
            source_state_serial = source_state_json["serial"]
            source_state_lineage = source_state_json["lineage"]

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
                        "lineage": source_state_lineage,
                        "state": source_state_b64
                    }
                }
            }

            # Migrate state to the target workspace
            self._api_target.workspaces.lock(\
                workspaces_map[workspace_id], {"reason": "migration script"})
            self._api_target.state_versions.create(\
                workspaces_map[workspace_id], create_state_version_payload)
            self._api_target.workspaces.unlock(workspaces_map[workspace_id])

            self._logger.info("Current state version for workspace: %s, created.",
                source_workspace_name)

        self._logger.info("Current state versions migrated.")
