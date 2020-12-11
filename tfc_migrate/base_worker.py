from abc import ABC, abstractmethod

import logging


class TFCMigratorBaseWorker(ABC):

    def __init__(self, api_source, api_target, vcs_connection_map, log_level):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(log_level)

        self._api_source = api_source
        self._api_target = api_target
        self._vcs_connection_map = vcs_connection_map

    """
    # TODO

    @abstractmethod
    def migrate_all(self):
        return []

    @abstractmethod
    def delete_all_from_target(self):
        return []
    """