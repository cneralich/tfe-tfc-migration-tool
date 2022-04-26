import os
import argparse
import json
import logging
from terrasnek.api import TFC
from tfc_migrate.migrator import TFCMigrator

DEFAULT_VCS_FILE = "vcs.json"
DEFAULT_SENSITIVE_DATA_FILE = "sensitive_data.txt"
DEFAULT_SELECT_ITEMS_LIST_FILE = "select_items_list.json"

# Source Org
TFE_TOKEN_SOURCE = os.getenv("TFE_TOKEN_SOURCE", None)
TFE_URL_SOURCE = os.getenv("TFE_URL_SOURCE", None)
TFE_ORG_SOURCE = os.getenv("TFE_ORG_SOURCE", None)
TFE_VERIFY_SOURCE = os.getenv("TFE_VERIFY_SOURCE", default="True").lower() == "true"

# Target Org
TFE_TOKEN_TARGET = os.getenv("TFE_TOKEN_TARGET", None)
TFE_URL_TARGET = os.getenv("TFE_URL_TARGET", None)
TFE_ORG_TARGET = os.getenv("TFE_ORG_TARGET", None)
TFE_VERIFY_TARGET = os.getenv("TFE_VERIFY_TARGET", default="True").lower() == "true"

# NOTE: this is parsed in the main function
TFE_VCS_CONNECTION_MAP = None
SENSITIVE_DATA_MAP = None
SELECT_ITEMS_LIST = None


def main(migrator, delete_all, no_confirmation, migrate_all_state, migrate_sensitive_data, migrate_select_workspaces, tfe_verify_source):

    if delete_all:
        migrator.delete_all_from_target(no_confirmation)
    elif migrate_sensitive_data:
        migrator.migrate_sensitive()
    else:
        migrator.migrate_all(migrate_all_state, migrate_select_workspaces, tfe_verify_source)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Migrate from one TFE/C org to another TFE/C org')
    parser.add_argument('--vcs-file-path', dest="vcs_file_path", default=DEFAULT_VCS_FILE, \
        help="Path to the VCS JSON file. Defaults to `vcs.json`.")
    parser.add_argument('--select-items-list-file-path', dest="select_items_list_file_path", \
        default=DEFAULT_SELECT_ITEMS_LIST_FILE, \
            help="Path to the select itmems migration file. Defaults to `select_items.json`.")
    parser.add_argument('--migrate-select-items', dest="migrate_select_items", action="store_true", \
        help="Migrate select items to the target organization. Default behavior is to migrate all items.")
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

    api_source = TFC(TFE_TOKEN_SOURCE, url=TFE_URL_SOURCE, verify=TFE_VERIFY_SOURCE)
    api_source.set_org(TFE_ORG_SOURCE)

    api_target = TFC(TFE_TOKEN_TARGET, url=TFE_URL_TARGET, verify=TFE_VERIFY_TARGET)
    api_target.set_org(TFE_ORG_TARGET)

    if not os.path.exists(args.vcs_file_path):
        open(DEFAULT_VCS_FILE, "w").close()
    else:
        with open(args.vcs_file_path, "r") as f:
            TFE_VCS_CONNECTION_MAP = json.loads(f.read())

    if not os.path.exists(args.sensitive_data_file_path):
        open(DEFAULT_SENSITIVE_DATA_FILE, "w").close()
    else:
        with open(args.sensitive_data_file_path, "r") as f:
            SENSITIVE_DATA_MAP = json.loads(f.read())

    if not os.path.exists(args.select_items_list_file_path):
        open(DEFAULT_SELECT_ITEMS_LIST_FILE, "w").close()
    else:
        with open(args.select_items_list_file_path, "r") as f:
            SELECT_ITEMS_LIST = json.loads(f.read())

    log_level = logging.INFO

    if args.debug:
        log_level = logging.DEBUG

    logging.basicConfig(level=log_level)

    migrator = TFCMigrator(api_source, api_target, TFE_VCS_CONNECTION_MAP, SENSITIVE_DATA_MAP, SELECT_ITEMS_LIST, log_level)

    main(migrator, args.delete_all, args.no_confirmation, args.migrate_all_state, args.migrate_sensitive_data, args.migrate_select_items, TFE_VERIFY_SOURCE)
