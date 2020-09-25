# TFC/E Migration Utility

## STEPS:
### 1. Set Required Environment Variables for both the Source Org and the New Org
```
# SOURCE ORG
TFE_TOKEN_ORIGINAL = os.getenv("TFE_TOKEN_ORIGINAL", None)
TFE_URL_ORIGINAL = os.getenv("TFE_URL_ORIGINAL", None)
TFE_ORG_ORIGINAL = os.getenv("TFE_ORG_ORIGINAL", None)

api_original = TFC(TFE_TOKEN_ORIGINAL, url=TFE_URL_ORIGINAL)
api_original.set_org(TFE_ORG_ORIGINAL)

# NEW ORG
TFE_TOKEN_NEW = os.getenv("TFE_TOKEN_NEW", None)
TFE_URL_NEW = os.getenv("TFE_URL_NEW", None)
TFE_ORG_NEW = os.getenv("TFE_ORG_NEW", None)
TFE_OAUTH_NEW = os.getenv("TFE_OAUTH_NEW", None)

api_new = TFC(TFE_TOKEN_NEW, url=TFE_URL_NEW)
api_new.set_org(TFE_ORG_NEW)
```

### 2. Select Desired Functions

Choose which components you want to migrate and comment out any others in [`migration.py`](migration.py).  For example, you may choose whether you want to `migrate_all_state` for your Workspaces or `migrate_current_state`, but you should not select both.  For more insight into what each function does, please refer to the contents of[`functions.py`](functions.py).

### 3. Run the Migration Script
```
python migration.py
```

### NOTES
This migration utility leverages the [Terraform Cloud/Enterprise API](https://www.terraform.io/docs/cloud/api/index.html) and the [terrasnek](https://github.com/dahlke/terrasnek) Python Client for interacting with it.  For security reasons, there are certain sensitive values that cannot be extracted (ex. Sensitive Variables and SSH Keys), so those will need to be re-added after the migration is complete (the Keys will, however, be migrated).

If needed (ex. for testing purposes), a set of helper delete functions have been included as well in [`delete_functions.py`](delete_functions.py).
