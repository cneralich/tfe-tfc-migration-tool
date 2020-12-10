from .base_worker import TFCMigratorBaseWorker

class TeamsWorker(TFCMigratorBaseWorker):

    def __init__(self, api_source, api_target, vcs_connection_map, log_level):
        super().__init__(api_source, api_target, vcs_connection_map, log_level)

    def migrate_all(self):
        self._logger.info("Migrating teams...")

        # Fetch Teams from Existing Org
        source_teams = self._api_source.teams.list()["data"]
        target_teams = self._api_target.teams.list()["data"]

        target_teams_data = {}
        for target_team in target_teams:
            target_teams_data[target_team["attributes"]["name"]] = target_team["id"]

        new_org_owners_team_id = None

        for source_team in source_teams:
            if source_team["attributes"]["name"] == "owners":
                new_org_owners_team_id = source_team["id"]
                break

        teams_map = {}
        for source_team in source_teams:
            source_team_name = source_team["attributes"]["name"]

            if source_team_name in target_teams_data:
                teams_map[source_team["id"]] = target_teams_data[source_team_name]
                self._logger.info(f"Team: %s, exists. Skipped." % source_team_name)
                continue

            if source_team_name == "owners":
                # No need to create a team, it's the owners team
                teams_map[source_team["id"]] = new_org_owners_team_id
            else:
                # Build the new team payload
                new_team_payload = {
                    "data": {
                        "type": "teams",
                        "attributes": {
                            "name": source_team_name,
                            "organization-access": {
                                "manage-workspaces": \
                                    source_team["attributes"]["organization-access"]["manage-workspaces"],
                                "manage-policies": \
                                    source_team["attributes"]["organization-access"]["manage-policies"],
                                "manage-vcs-settings": \
                                    source_team["attributes"]["organization-access"]["manage-vcs-settings"]
                            }
                        }
                    }
                }

                # Create team in the target org
                new_team = self._api_target.teams.create(new_team_payload)
                self._logger.info(f"Team %s, created." % source_team_name)

                # Build Team ID Map
                teams_map[source_team["id"]] = new_team["data"]["id"]

        self._logger.info("Teams migrated.")

        return teams_map


    def delete_all_from_target(self):
        self._logger.info("Deleting teams...")

        teams = self._api_target.teams.list()["data"]
        if teams:
            for team in teams:
                team_name = team["attributes"]["name"]
                if team_name != "owners":
                    self._api_target.teams.destroy(team["id"])
                    self._logger.info(f"Team: %s deleted." % team_name)

        self._logger.info("Teams deleted.")
