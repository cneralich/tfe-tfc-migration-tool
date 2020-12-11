"""
Module for Terraform Enterprise/Cloud Migration Worker: SSH Keys.
"""

from .base_worker import TFCMigratorBaseWorker


class SSHKeysWorker(TFCMigratorBaseWorker):

    def __init__(self, api_source, api_target, vcs_connection_map, log_level):
        super().__init__(api_source, api_target, vcs_connection_map, log_level)

    def migrate_all(self):
        self._logger.info("Migrating SSH keys...")

        # Fetch SSH Keys from existing org
        # NOTE: This does not fetch the Keys themselves
        source_ssh_keys = self._api_source.ssh_keys.list()["data"]
        target_ssh_keys = self._api_target.ssh_keys.list()["data"]

        target_ssh_keys_data = {}
        for target_ssh_key in target_ssh_keys:
            target_ssh_keys_data[target_ssh_key["attributes"]["name"]] = target_ssh_key["id"]

        ssh_keys_map = {}
        ssh_key_name_map = {}

        # NOTE: this is reversed to maintain the order present in the source
        for source_ssh_key in reversed(source_ssh_keys):
            source_ssh_key_id = source_ssh_key["id"]
            source_ssh_key_name = source_ssh_key["attributes"]["name"]

            if source_ssh_key_name in target_ssh_keys_data:
                ssh_keys_map[source_ssh_key_id] = target_ssh_keys_data[source_ssh_key_name]
                ssh_key_name_map[source_ssh_key_name] = target_ssh_keys_data[source_ssh_key_name]
                self._logger.info(" SSH Key: %s, exists. Skipped." % source_ssh_key_name)
                continue

            # Build the new agent pool payload
            new_ssh_key_payload = {
                "data": {
                    "type": "ssh-keys",
                    "attributes": {
                        "name": source_ssh_key_name,
                        "value": "Replace Me"
                    }
                }
            }

            # Create SSH key in the target org
            # NOTE: The actual key material itself must be added separately afterward
            new_ssh_key = self._api_target.ssh_keys.create(new_ssh_key_payload)["data"]
            self._logger.info("SSH Key: %s, created." % source_ssh_key_name)

            new_ssh_key_id = new_ssh_key["id"]
            ssh_keys_map[source_ssh_key_id] = new_ssh_key_id
            ssh_key_name_map[source_ssh_key_name] = new_ssh_key_id

        self._logger.info("SSH keys migrated.")

        return ssh_keys_map, ssh_key_name_map


    def migrate_key_files(self, ssh_key_name_map, ssh_key_file_path_map):
        """
        NOTE: The ssh_key_file_path_map must be created ahead of time with a format of
        {"ssh_key_name":"path/to/file"}
        """

        self._logger.info("Migrating SSH key files...")

        for ssh_key in ssh_key_file_path_map:
            # Pull SSH key data
            get_ssh_key = open(ssh_key_file_path_map[ssh_key], "r")
            ssh_key_data = get_ssh_key.read()

            # Build the new ssh key file payload
            new_ssh_key_file_payload = {
                "data": {
                    "type": "ssh-keys",
                    "attributes": {
                        "value": ssh_key_data
                    }
                }
            }

            # TODO: logging, and make sure this works / document it

            # Upload the SSH key file to the target organization
            self._api_target.ssh_keys.update(ssh_key_name_map[ssh_key], new_ssh_key_file_payload)

        self._logger.info("SSH key files migrated.")


    def delete_all_from_target(self):
        self._logger.info("Deleting SSH keys...")

        ssh_keys = self._api_target.ssh_keys.list()["data"]
        if ssh_keys:
            for ssh_key in ssh_keys:
                self._logger.info("SSH key: %s, deleted..." % ssh_key["attributes"]["name"])
                self._api_target.ssh_keys.destroy(ssh_key["id"])

        self._logger.info("SSH keys deleted.")
