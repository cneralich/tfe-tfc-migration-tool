import os
from terrasnek.api import TFC
import urllib.request
import requests
import hashlib
import base64
import json
from functions import *

# SOURCE ORG
TFE_TOKEN_ORIGINAL = os.getenv("TFE_TOKEN_ORIGINAL", None)
TFE_URL_ORIGINAL = os.getenv("TFE_URL_ORIGINAL", None)
TFE_ORG_ORIGINAL = os.getenv("TFE_ORG_ORIGINAL", None)

api_original = TFC(TFE_TOKEN_ORIGINAL, url=TFE_URL_ORIGINAL)
api_original.set_org(TFE_ORG_ORIGINAL)

#NEW ORG
TFE_TOKEN_NEW = os.getenv("TFE_TOKEN_NEW", None)
TFE_URL_NEW = os.getenv("TFE_URL_NEW", None)
TFE_ORG_NEW = os.getenv("TFE_ORG_NEW", None)
TFE_OAUTH_NEW = os.getenv("TFE_OAUTH_NEW", None)

api_new = TFC(TFE_TOKEN_NEW, url=TFE_URL_NEW)
api_new.set_org(TFE_ORG_NEW)

def migrate_orgs():
    team_map = migrate_teams(api_original, api_new)
    print('teams migrated')
    workspaces_map = migrate_workspaces(api_original, api_new, TFE_OAUTH_NEW)
    print('workspaces migrated')
    #migrate_all_state(api_original, api_new, TFE_ORG_ORIGINAL, workspaces_map)
    migrate_current_state(api_original, api_new, TFE_ORG_ORIGINAL, workspaces_map)
    print('state migrated')
    migrate_workspace_variables(api_original, api_new, TFE_ORG_ORIGINAL, workspaces_map)
    print('workspace variables migrated')
    migrate_workspace_team_access(api_original, api_new, workspaces_map, team_map)
    print('workspace team access migrated')
    policies_map = migrate_policies(api_original, api_new, TFE_TOKEN_ORIGINAL, TFE_URL_ORIGINAL)
    print('policies migrated')
    policy_sets_map = migrate_policy_sets(api_original, api_new, TFE_OAUTH_NEW, workspaces_map, policies_map)
    print('policy sets migrated')
    migrate_policy_set_parameters(api_original, api_new, policy_sets_map)
    print('policy set parameters migrated')
