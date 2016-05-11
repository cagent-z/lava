# Copyright (C) 2010 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of Lava Dashboard.
#
# Lava Dashboard is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License version 3
# as published by the Free Software Foundation
#
# Lava Dashboard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Lava Dashboard.  If not, see <http://www.gnu.org/licenses/>.

import os

from lava_server.extension import LavaServerExtension


class DashboardExtension(LavaServerExtension):

    @property
    def app_name(self):
        return "dashboard_app"

    @property
    def main_view_name(self):
        return "dashboard_app.views.index"

    @property
    def api_class(self):
        from dashboard_app.xmlrpc import DashboardAPI
        return DashboardAPI

    def contribute_to_settings(self, settings_module):
        super(DashboardExtension, self).contribute_to_settings(settings_module)
        root_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
        settings_module['DATAVIEW_DIRS'] = [
            os.path.join(root_dir, 'examples', 'views'),
            os.path.join(root_dir, 'production', 'views')]
        settings_module['DATAREPORT_DIRS'] = [
            os.path.join(root_dir, 'examples', 'reports'),
            os.path.join(root_dir, 'production', 'reports')]

    def contribute_to_settings_ex(self, settings_module, settings_object):
        settings_module['DATAVIEW_DIRS'] = settings_object._settings.get(
            "DATAVIEW_DIRS", [])
        settings_module['DATAVIEW_HIDE'] = settings_object._settings.get(
            "DATAVIEW_HIDE", False)
        settings_module['DATAREPORT_DIRS'] = settings_object._settings.get(
            "DATAREPORT_DIRS", [])
        settings_module['DATAREPORTS_HIDE'] = settings_object._settings.get(
            "DATAREPORTS_HIDE", False)
        settings_module['PM_QA_HIDE'] = settings_object._settings.get(
            "PM_QA_HIDE", True)

        # Enable constrained dataview database if requested
        if settings_object._settings.get("use_dataview_database"):
            # Copy everything from the default database and append _dataview to user
            # name. The rest is out of scope (making sure it's actually setup
            # properly, having permissions to login, permissions to view proper data)
            settings_module['DATABASES']['dataview'] = dict(settings_module['DATABASES']['default'])
            settings_module['DATABASES']['dataview']['USER'] += "_dataview"