"""
Module for Terraform Enterprise/Cloud Migration Worker: Team Access.
"""

from .base_worker import TFCMigratorBaseWorker


class TeamAccessWorker(TFCMigratorBaseWorker):

    def __init__(self, api_source, api_target, vcs_connection_map, log_level):
        super().__init__(api_source, api_target, vcs_connection_map, log_level)

    def migrate_all(self, workspaces_map, teams_map):

        self._logger.info("Migrating team access...")

        for source_workspace_id in workspaces_map:
            # Set proper workspace team filters to pull team access for each
            # workspace
            source_workspace_team_filters = [
                {
                    "keys": ["workspace", "id"],
                    "value": source_workspace_id
                }
            ]

            # Pull teams from the old workspace
            source_workspace_teams = self._api_source.team_access.list(\
                filters=source_workspace_team_filters)["data"]

            target_workspace_id = workspaces_map[source_workspace_id]
            target_workspace_team_filters = [
                {
                    "keys": ["workspace", "id"],
                    "value": target_workspace_id
                }
            ]

            target_workspace_teams = self._api_target.team_access.list(\
                filters=target_workspace_team_filters)["data"]
            target_team_ids = [team["relationships"]["team"]["data"]["id"] \
                for team in target_workspace_teams]

            for source_workspace_team in source_workspace_teams:
                new_target_team_id = teams_map\
                    [source_workspace_team["relationships"]["team"]["data"]["id"]]

                if new_target_team_id in target_team_ids:
                    self._logger.info(\
                        "Team access for workspace: %s, exists (%s). Skipped." % \
                            (new_target_team_id, target_workspace_id))
                    continue

                new_workspace_team_payload = {
                    "data": {
                        "attributes": {
                            "access": source_workspace_team["attributes"]["access"]
                        },
                        "relationships": {
                            "workspace": {
                                "data": {
                                    "type": "workspaces",
                                    "id": target_workspace_id
                                }
                            },
                            "team": {
                                "data": {
                                    "type": "teams",
                                    "id": new_target_team_id
                                }
                            }
                        },
                        "type": "team-workspaces"
                    }
                }

                if source_workspace_team["attributes"]["access"] == "custom":
                    attributes_to_copy = [
                        "runs", "variables", "state-versions", "sentinel-mocks",
                        "workspace-locking"
                    ]

                    for attr in attributes_to_copy:
                        new_workspace_team_payload["data"]["attributes"][attr] = \
                            source_workspace_team["attributes"][attr]

                try:
                    # Create the team workspace access map for the target workspace
                    self._api_target.team_access.add_team_access(new_workspace_team_payload)
                except Exception as err:
                    # TODO
                    print(err)

        self._logger.info("Team access migrated.")


    def delete_all_from_target(self):
        self._logger.info("Deleting team workspace access...")

        target_workspaces = self._api_target.workspaces.list()["data"]

        if target_workspaces:
            for target_workspace in target_workspaces:
                target_workspace_id = target_workspace["id"]
                target_workspace_team_filters = [
                    {
                        "keys": ["workspace", "id"],
                        "value": target_workspace_id
                    }
                ]

                target_workspace_teams = \
                    self._api_target.team_access.list(filters=target_workspace_team_filters)["data"]

                if target_workspace_teams:
                    for target_workspace_team in target_workspace_teams:
                        target_workspace_team_data = self._api_target.teams.show( \
                            target_workspace_team["relationships"]["team"]["data"]["id"])["data"]
                        target_workspace_team_name = \
                            target_workspace_team_data["attributes"]["name"]

                        self._logger.info("Team access: %s, for workspace: %s..." \
                            % (target_workspace_team_name, target_workspace["attributes"]["name"]))
                        self._api_target.team_access.remove_team_access(target_workspace_team["id"])

        self._logger.info("Team workspace access deleted.")
