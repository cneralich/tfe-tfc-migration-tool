"""
Module for class that is the basic required properties for a TFC/E API migration
worker.
"""

from abc import ABC

import logging


class TFCMigratorBaseWorker(ABC):

    def __init__(self, api_source, api_target, vcs_connection_map, sensitive_data_map, log_level):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(log_level)

        self._api_source = api_source
        self._api_target = api_target
        self._vcs_connection_map = vcs_connection_map
        self._sensitive_data_map = sensitive_data_map

    """
    def migrate_all(self):
        pass

    def delete_all_from_target(self):
        pass
    """
