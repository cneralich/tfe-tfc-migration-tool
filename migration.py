import os
import argparse
import json
import logging
from terrasnek.api import TFC
from tfc_migrate.migrator import TFCMigrator

DEFAULT_VCS_FILE = "vcs.json"
DEFAULT_SENSITIVE_DATA_FILE = "sensitive_data.txt"

# Source Org
TFE_TOKEN_SOURCE = os.getenv("TFE_TOKEN_SOURCE", None)
TFE_URL_SOURCE = os.getenv("TFE_URL_SOURCE", None)
TFE_ORG_SOURCE = os.getenv("TFE_ORG_SOURCE", None)

# Target Org
TFE_TOKEN_TARGET = os.getenv("TFE_TOKEN_TARGET", None)
TFE_URL_TARGET = os.getenv("TFE_URL_TARGET", None)
TFE_ORG_TARGET = os.getenv("TFE_ORG_TARGET", None)

# NOTE: this is parsed in the main function
TFE_VCS_CONNECTION_MAP = None
SENSITIVE_DATA_MAP = None


def main(migrator, delete_all, no_confirmation, migrate_all_state, migrate_sensitive_data):

    if delete_all:
        migrator.delete_all_from_target(no_confirmation)
    elif migrate_sensitive_data:
        migrator.migrate_sensitive()
    else:
        migrator.migrate_all(migrate_all_state)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Migrate from one TFE/C org to another TFE/C org')
    parser.add_argument('--vcs-file-path', dest="vcs_file_path", default=DEFAULT_VCS_FILE, \
        help="Path to the VCS JSON file. Defaults to `vcs.json`.")
    parser.add_argument('--migrate-all-state', dest="migrate_all_state", action="store_true", \
        help="Migrate all state history workspaces. Default behavior is only current state.")
    parser.add_argument('--sensitive-data-file-path', dest="sensitive_data_file_path", \
        default=DEFAULT_SENSITIVE_DATA_FILE, \
            help="Path the the sensitive values file. Defaults to `sensitive_data.txt`.")
    parser.add_argument('--migrate-sensitive-data', dest="migrate_sensitive_data", action="store_true", \
        help="Migrate sensitive data to the target organization.")
    parser.add_argument('--delete-all', dest="delete_all", action="store_true", \
        help="Delete all resources from the target API.")
    parser.add_argument('--no-confirmation', dest="no_confirmation", action="store_true", \
        help="If set, don't ask for confirmation before deleting all target resources.")
    parser.add_argument('--debug', dest="debug", action="store_true", \
        help="If set, run the logger in debug mode.")
    args = parser.parse_args()

    api_source = TFC(TFE_TOKEN_SOURCE, url=TFE_URL_SOURCE)
    api_source.set_org(TFE_ORG_SOURCE)

    # TODO: take the verification as an env var
    api_target = TFC(TFE_TOKEN_TARGET, url=TFE_URL_TARGET, verify=False)
    api_target.set_org(TFE_ORG_TARGET)

    with open(args.vcs_file_path, "r") as f:
        TFE_VCS_CONNECTION_MAP = json.loads(f.read())

    with open(args.sensitive_data_file_path) as f:
        SENSITIVE_DATA_MAP = json.loads(f.read())

    log_level = logging.INFO

    if args.debug:
        log_level = logging.DEBUG

    logging.basicConfig(level=log_level)

    migrator = TFCMigrator(api_source, api_target, TFE_VCS_CONNECTION_MAP, SENSITIVE_DATA_MAP, log_level)

    main(migrator, args.delete_all, args.no_confirmation, args.migrate_all_state, args.migrate_sensitive_data)
