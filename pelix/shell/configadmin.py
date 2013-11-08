#!/usr/bin/env python
# -- Content-Encoding: UTF-8 --
"""
Configuration Admin shell commands

Provides commands to the Pelix shell to work with the Configuration Admin
service

:author: Thomas Calmant
:copyright: Copyright 2013, isandlaTech
:license: Apache License 2.0
:version: 0.1.0
:status: Beta

..

    Copyright 2013 isandlaTech

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

# Module version
__version_info__ = (0, 1, 0)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
__docformat__ = "restructuredtext en"

# -----------------------------------------------------------------------------

# Shell constants
from pelix.shell import SHELL_COMMAND_SPEC

# iPOPO Decorators
from pelix.ipopo.decorators import ComponentFactory, Requires, Provides, \
    Instantiate, Invalidate
import pelix.services

# ------------------------------------------------------------------------------

@ComponentFactory("configadmin-shell-commands-factory")
@Requires("_config_admin", pelix.services.SERVICE_CONFIGURATION_ADMIN)
@Provides(SHELL_COMMAND_SPEC)
@Instantiate("configadmin-shell-commands")
class ConfigAdminCommands(object):
    """
    Configuration Admin shell commands
    """
    def __init__(self):
        """
        Sets up members
        """
        # Injected services
        self._config_admin = None

        # Handled configurations (PID -> Configuration)
        self._configs = {}

    @Invalidate
    def invalidate(self, context):
        """
        Component invalidated
        """
        # Clean up
        self._configs.clear()


    def get_namespace(self):
        """
        Retrieves the name space of this command handler
        """
        return "config"


    def get_methods(self):
        """
        Retrieves the list of tuples (command, method) for this command handler
        """
        return [("create", self.create),
                ("update", self.update),
                ("delete", self.delete),
                ("list", self.list)]


    def _get_configuration(self, pid):
        """
        Tries to return the configuration in cache before calling the
        Configuration Admin

        :param pid: A configuration PID
        :return: The retrieved configuration
        """
        try:
            # Grab from cache
            config = self._configs[pid]

        except KeyError:
            # Not yet in cache
            self._configs[pid] = config = self._config_admin. \
                                                        get_configuration(pid)

        return config


    def create(self, io_handler, pid, **kwargs):
        """
        Creates a configuration
        """
        self._configs[pid] = config = self._config_admin.get_configuration(pid)
        if kwargs:
            # Update it immediately if some properties are already set
            config.update(kwargs)


    def update(self, io_handler, pid, **kwargs):
        """
        Updates a configuration
        """
        self._get_configuration(pid).update(kwargs)


    def delete(self, io_handler, pid, **kwargs):
        """
        Deletes a configuration
        """
        self._get_configuration(pid).delete()
        del self._configs[pid]


    def list(self, io_handler):
        """
        Lists known configurations
        """
        configs = self._config_admin.list_configurations()
        if not configs:
            io_handler.write_line("No configuration.")
            return

        lines = []
        for config in configs:
            lines.append('* {0}:'.format(config.get_pid()))
            factory_pid = config.get_factory_pid()
            if factory_pid:
                lines.append('\tFactory PID: {0}'.format(factory_pid))
            lines.append('\tLocation: {0}'.format(config.get_bundle_location()))

            try:
                properties = config.get_properties()
                if properties is None:
                    lines.append("\tNot yet updated")

                else:
                    lines.append('\tProperties:')
                    lines.extend('\t\t{0} = {1}'.format(key, value)
                                 for key, value in properties.items())

            except ValueError:
                lines.append("\t** Deleted **")

        lines.append('')
        io_handler.write_line('\n'.join(lines))
