from abc import ABC

import json
import logging

from .agent_pools import AgentPoolsWorker
from .config_versions import ConfigVersionsWorker
from .notification_configs import NotificationConfigsWorker
from .org_memberships import OrgMembershipsWorker
from .policies import PoliciesWorker
from .policy_sets import PolicySetsWorker
from .policy_set_params import PolicySetParamsWorker
from .teams import TeamsWorker
from .team_access import TeamAccessWorker
from .registry_modules import RegistryModulesWorker
from .registry_module_versions import RegistryModuleVersionsWorker
from .run_triggers import RunTriggersWorker
from .ssh_keys import SSHKeysWorker
from .state_versions import StateVersionsWorker
from .ssh_keys import SSHKeysWorker
from .workspaces import WorkspacesWorker
from .workspace_ssh_keys import WorkspaceSSHKeysWorker
from .workspace_vars import WorkspaceVarsWorker

class TFCMigrator(ABC):

    def __init__(self, api_source, api_target, vcs_connection_map, sensitive_data_map, log_level):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._log_level = log_level
        self._logger.setLevel(self._log_level)
        self._api_source = api_source
        self._api_target = api_target
        self._vcs_connection_map = vcs_connection_map
        self._sensitive_data_map = sensitive_data_map

        self.agent_pools = AgentPoolsWorker(api_source, api_target, vcs_connection_map, sensitive_data_map, log_level)
        self.config_versions = \
            ConfigVersionsWorker(api_source, api_target, vcs_connection_map, sensitive_data_map, log_level)
        self.notification_configs = \
            NotificationConfigsWorker(api_source, api_target, vcs_connection_map, sensitive_data_map, log_level)
        self.org_memberships = \
            OrgMembershipsWorker(api_source, api_target, vcs_connection_map, sensitive_data_map, log_level)
        self.policies = PoliciesWorker(api_source, api_target, vcs_connection_map, sensitive_data_map, log_level)
        self.policy_sets = PolicySetsWorker(api_source, api_target, vcs_connection_map, sensitive_data_map, log_level)
        self.policy_set_params = \
            PolicySetParamsWorker(api_source, api_target, vcs_connection_map, sensitive_data_map, log_level)
        self.registry_module_versions = \
            RegistryModuleVersionsWorker(api_source, api_target, vcs_connection_map, sensitive_data_map, log_level)
        self.registry_modules = \
            RegistryModulesWorker(api_source, api_target, vcs_connection_map, sensitive_data_map, log_level)
        self.run_triggers = RunTriggersWorker(api_source, api_target, vcs_connection_map, sensitive_data_map, log_level)
        self.ssh_keys = SSHKeysWorker(api_source, api_target, vcs_connection_map, sensitive_data_map, log_level)
        self.state_versions = \
            StateVersionsWorker(api_source, api_target, vcs_connection_map, sensitive_data_map, log_level)
        self.team_access = TeamAccessWorker(api_source, api_target, vcs_connection_map, sensitive_data_map, log_level)
        self.teams = TeamsWorker(api_source, api_target, vcs_connection_map, sensitive_data_map, log_level)
        self.workspace_vars = \
            WorkspaceVarsWorker(api_source, api_target, vcs_connection_map, sensitive_data_map, log_level)
        self.workspaces = WorkspacesWorker(api_source, api_target, vcs_connection_map, sensitive_data_map, log_level)
        self.workspace_ssh_keys = \
            WorkspaceSSHKeysWorker(api_source, api_target, vcs_connection_map, sensitive_data_map, log_level)

    def migrate_all(self, migrate_all_state):
        """
        NOTE: org_memberships.migrate only sends out invites, as such, it's commented out.
        The users must exist in the system ahead of time if you want to use this.
        Lastly, since most customers use SSO, this function isn't terribly useful.
        """
        # TODO: org_membership_map = org_memberships.migrate(api_source, api_target, teams_map)

        teams_map = self.teams.migrate_all()

        ssh_keys_map, ssh_key_name_map, ssh_key_file_path_map = self.ssh_keys.migrate_all()

        agent_pools_map = self.agent_pools.migrate_all()

        workspaces_map, workspace_to_ssh_key_map = self.workspaces.migrate_all(agent_pools_map)

        self.workspace_ssh_keys.migrate_all(workspaces_map, workspace_to_ssh_key_map, ssh_keys_map)

        sensitive_variable_data = self.workspace_vars.migrate_all(workspaces_map)

        if migrate_all_state:
            self.state_versions.migrate_all(workspaces_map)
        else:
            self.state_versions.migrate_current(workspaces_map)

        self.run_triggers.migrate_all(workspaces_map)

        self.notification_configs.migrate_all(workspaces_map)

        self.team_access.migrate_all(workspaces_map, teams_map)

        workspace_to_config_version_upload_url_map, workspace_to_config_version_file_path_map = self.config_versions.migrate_all(workspaces_map)

        # TODO: manage extracting state and publishing tarball
        # config_versions.migrate_config_files(\
        #   workspace_to_config_version_upload_map, workspace_to_file_path_map)

        policies_map = self.policies.migrate_all()

        policy_sets_map = self.policy_sets.migrate_all(workspaces_map, policies_map)

        # This function returns the information that is needed to publish sensitive
        # variables, but cannot retrieve the values themselves, so those values will
        # have to be updated separately.
        sensitive_policy_set_parameter_data = self.policy_set_params.migrate_all(policy_sets_map)

        module_to_module_version_upload_map = self.registry_modules.migrate_all()

        # TODO: manage extracting module and publishing tarball, this doesn't work.
        # registry_module_versions.migrate_module_version_files()

        output_json = {
            "teams_map": teams_map,
            "ssh_keys_map": ssh_keys_map,
            "ssh_key_name_map": ssh_key_name_map,
            "workspaces_map": workspaces_map,
            "workspace_to_ssh_key_map": workspace_to_ssh_key_map,
            "workspace_to_config_version_upload_url_map": workspace_to_config_version_upload_url_map,
            "module_to_module_version_upload_map": module_to_module_version_upload_map,
            "policies_map": policies_map,
            "policy_sets_map": policy_sets_map,
            "workspace_to_config_version_file_path_map": workspace_to_config_version_file_path_map,
            "ssh_key_file_path_map": ssh_key_file_path_map,
            "sensitive_policy_set_parameter_data": sensitive_policy_set_parameter_data,
            "sensitive_variable_data": sensitive_variable_data
        }

        print(json.dumps(output_json))

    
    def migrate_sensitive(self):
        self.config_versions.migrate_config_files()
        
        self.ssh_keys.migrate_key_files()
        
        self. policy_set_params.migrate_sensitive()
        
        self.workspace_vars.migrate_sensitive()



    def delete_all_from_target(self, no_confirmation):
        if no_confirmation or self.confirm_delete_resource_type("run triggers", self._api_target):
            self.run_triggers.delete_all_from_target()

        if no_confirmation or \
            self.confirm_delete_resource_type("workspace variables", self._api_target):
            self.workspace_vars.delete_all_from_target()

        if no_confirmation or self.confirm_delete_resource_type("team access", self._api_target):
            self.team_access.delete_all_from_target()

        if no_confirmation or \
            self.confirm_delete_resource_type("workspace ssh keys", self._api_target):
            self.workspace_ssh_keys.delete_all_from_target()

        if no_confirmation or self.confirm_delete_resource_type("workspaces", self._api_target):
            self.workspaces.delete_all_from_target()

        # No need to delete the key files, they get deleted when deleting keys.
        if no_confirmation or self.confirm_delete_resource_type("SSH keys", self._api_target):
            self.ssh_keys.delete_all_from_target()

        if no_confirmation or \
            self.confirm_delete_resource_type("org memberships", self._api_target):
            self.org_memberships.delete_all_from_target()

        if no_confirmation or self.confirm_delete_resource_type("teams", self._api_target):
            self.teams.delete_all_from_target()

        if no_confirmation or self.confirm_delete_resource_type("policies", self._api_target):
            self.policies.delete_all_from_target()

        if no_confirmation or self.confirm_delete_resource_type("policy sets", self._api_target):
            self.policy_sets.delete_all_from_target()

        if no_confirmation or \
            self.confirm_delete_resource_type("policy set params", self._api_target):
            self.policy_set_params.delete_all_from_target()

        if no_confirmation or \
            self.confirm_delete_resource_type("registry modules", self._api_target):
            # NOTE: No need to delete registry module versions since this will handle that.
            self.registry_modules.delete_all_from_target()

        if no_confirmation or self.confirm_delete_resource_type("agent pools", self._api_target):
            self.agent_pools.delete_all_from_target()


    def confirm_delete_resource_type(self, resource_type, api):
        answer = ""

        while answer not in ["y", "n"]:
            question_string = \
                "This will destroy all %s in org '%s' (%s). Want to continue? [Y/N]: " \
                    % (resource_type, api.get_org(), api.get_url())
            answer = input(question_string).lower()

        return answer == "y"
