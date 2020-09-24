# TFC/E Migration Utility

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

Choose which components you want to migrate and comment out any others in `migration.py`.

### 3. Run the Migration Script
```
python migration.py
```

### NOTES
This migration utility leverages the [Terraform Cloud/Enterprise API](https://www.terraform.io/docs/cloud/api/index.html) and the [terrasnek](https://github.com/dahlke/terrasnek) Python Client for interacting with it.  For security reasons, there are certain sensitive values that cannot be extracted (ex. Sensitive Variables and SSH Keys), so those will need to be readded after the migration is complete (the Keys will, however, be migrated).
