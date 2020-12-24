"""
Module for class that is the basic required properties for a TFC/E API migration
worker.
"""

from abc import ABC

import logging


class TFCMigratorBaseWorker(ABC):

    _api_module_used = None
    _required_entitlements = []

    def __init__(self, api_source, api_target, vcs_connection_map, sensitive_data_map, log_level):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(log_level)

        self._api_source = api_source
        self._api_target = api_target
        self._vcs_connection_map = vcs_connection_map
        self._sensitive_data_map = sensitive_data_map

    def _check_entitlements(self):
        # Make sure that our test meets the entitlements required, return true if so.
        # Options: [
        #   "cost-estimation", "configuration-designer", "operations", "private-module-registry",
        #   "sentinel", "state-storage", "teams", "vcs-integrations", "usage-reporting", "user-limit",
        #   "self-serve-billing", "audit-logging", "agents", "sso"
        # ]
        source_entitlements = self._api_source.get_entitlements()
        target_entitlements = self._api_target.get_entitlements()

        has_source_entitlements = True
        has_target_entitlements = True

        for required_entitlement in self._required_entitlements:
            if not source_entitlements[required_entitlement]:
                has_source_entitlements = False
                break

        for required_entitlement in self._required_entitlements:
            if not target_entitlements[required_entitlement]:
                has_target_entitlements = False

        return has_source_entitlments and has_target_entitlements

    def _check_terraform_platform(self):
        target_is_tfc = self._api_target.is_terraform_cloud()
        source_is_tfc = self._api_source.is_terraform_cloud()

        module_used = getattr(self._api_source, self._api_module_used)
        module_tfc_only = module_used.terraform_cloud_only()
        module_tfe_only = module_used.terraform_enterprise_only()

        valid_platform_migration = False

        if not module_tfe_only and not module_tfc_only:
            # If the endpoint is not specific to TFE or TFC, it's valid
            valid_platform_migration = True
        if module_tfe_only and not source_is_tfc and not target_is_tfc:
            # If the endpoint is specific to TFE but both are TFE, it's valid
            valid_platform_migration = True
        elif module_tfc_only and source_is_tfc and target_is_tfc:
            # If the endpoint is specific to TFC but both are TFC, it's valid
            valid_platform_migration = True

        return valid_platform_migration

    """
    def migrate_all(self):
        pass

    def delete_all_from_target(self):
        pass
    """
