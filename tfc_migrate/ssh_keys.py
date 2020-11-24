

def migrate_keys(api_source, api_target):
    print("Migrating SSH keys...")

    # Fetch SSH Keys from existing org
    # NOTE: This does not fetch the Keys themselves
    source_ssh_keys = api_source.ssh_keys.list()["data"]
    target_ssh_keys = api_target.ssh_keys.list()["data"]

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
            print("\t", source_ssh_key_name, "SSH key already exists, skipping...")
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
        new_ssh_key = api_target.ssh_keys.create(new_ssh_key_payload)["data"]
        print("\t", source_ssh_key_name, "SSH key created...")

        new_ssh_key_id = new_ssh_key["id"]
        ssh_keys_map[source_ssh_key_id] = new_ssh_key_id
        ssh_key_name_map[source_ssh_key_name] = new_ssh_key_id

    print("SSH keys successfully migrated.")

    return ssh_keys_map, ssh_key_name_map


def migrate_key_files(api_target, ssh_key_name_map, ssh_key_file_path_map):
    """
    NOTE: The ssh_key_file_path_map must be created ahead of time with a format of
    {"ssh_key_name":"path/to/file"}
    """

    print("Migrating SSH key files...")

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
        api_target.ssh_keys.update(ssh_key_name_map[ssh_key], new_ssh_key_file_payload)

    print("SSH key files successfully migrated.")


def delete_all_keys(api_target):
    print("Deleting SSH keys...")

    ssh_keys = api_target.ssh_keys.list()["data"]
    if ssh_keys:
        for ssh_key in ssh_keys:
            print(f"\t deleting SSH key %s..." % ssh_key["attributes"]["name"])
            api_target.ssh_keys.destroy(ssh_key["id"])

    print("SSH keys deleted.")
