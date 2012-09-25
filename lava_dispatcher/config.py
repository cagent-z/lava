# Copyright (C) 2011 Linaro Limited
#
# Author: Paul Larson <paul.larson@linaro.org>
#
# This file is part of LAVA Dispatcher.
#
# LAVA Dispatcher is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# LAVA Dispatcher is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along
# with this program; if not, see <http://www.gnu.org/licenses>.

from ConfigParser import ConfigParser, NoOptionError
import os
import StringIO
import logging


from configglue import parser, schema

class DeviceSchema(schema.Schema):
    connection_command = schema.StringOption(fatal=True)
    hostname = schema.StringOption()
    tester_hostname = schema.StringOption(default="linaro")
    device_type = schema.StringOption(fatal=True)
    boot_part = schema.IntOption(fatal=True)
    interrupt_boot_prompt = schema.StringOption()
    boot_cmds = schema.StringOption()
    root_part = schema.StringOption()
    boot_cmds_oe = schema.StringOption()
    pre_connect_command = schema.StringOption()
    boot_part_android_org = schema.StringOption()
    boot_cmds_android = schema.StringOption()
    qemu_machine_type = schema.StringOption()
    master_str = schema.StringOption()
    val = schema.StringOption()
    enable_network_after_boot_android = schema.StringOption()
    cache_part_android_org = schema.StringOption()
    data_part_android = schema.StringOption()
    tester_str = schema.StringOption()
    default_network_interface = schema.StringOption()
    data_part_android_org = schema.StringOption()
    bootloader_prompt = schema.StringOption()
    git_url_disablesuspend_sh = schema.StringOption()
    sdcard_part_android = schema.StringOption()
    interrupt_boot_command = schema.StringOption()
    qemu_drive_interface = schema.StringOption()
    sys_part_android = schema.StringOption()
    lmc_dev_arg = schema.StringOption()
    sdcard_part_android_org = schema.StringOption()
    android_binary_drivers = schema.StringOption()
    client_type = schema.StringOption()
    image_boot_msg = schema.StringOption()
    soft_boot_cmd = schema.StringOption()
    sys_part_android_org = schema.StringOption()

class DispatcherSchema(schema.Schema):
    lava_proxy = schema.StringOption()
    lava_image_tmpdir = schema.StringOption()
    lava_test_deb = schema.StringOption()
    lava_test_url = schema.StringOption()
    lava_cachedir = schema.StringOption()
    default_qemu_binary = schema.StringOption()
    lava_server_ip = schema.StringOption()
    lava_image_url = schema.StringOption()
    lava_result_dir = schema.StringOption()
    logging_level = schema.StringOption()


default_config_path = os.path.join(
    os.path.dirname(__file__), 'default-config')


def load_config_paths(name, config_dir):
    if config_dir is None:
        paths = [
            os.path.join(path, name) for path in [
                os.path.expanduser("~/.config"),
                "/etc/xdg",
                default_config_path]]
    else:
        paths = [config_dir, os.path.join(default_config_path, name)]
    for path in paths:
        if os.path.isdir(path):
            yield path


def _read_into(path, cp):
    s = StringIO.StringIO()
    s.write('[__main__]\n')
    s.write(open(path).read())
    s.seek(0)
    cp.readfp(s)


def _get_config(name, config_dir, cp=None, schema=None):
    """Read a config file named name + '.conf'.

    This checks and loads files from the source tree, site wide location and
    home directory -- in that order, so home dir settings override site
    settings which override source settings.
    """
    config_files = []
    for directory in load_config_paths('lava-dispatcher', config_dir):
        path = os.path.join(directory, '%s.conf' % name)
        if os.path.exists(path):
            config_files.append(path)
    if not config_files:
        raise Exception("no config files named %r found" % (name + ".conf"))
    config_files.reverse()
    if cp is None:
        if schema:
            cp = parser.SchemaConfigParser(schema)
        else:
            cp = ConfigParser()
    logging.debug("About to read %s" % str(config_files))
    for path in config_files:
        _read_into(path, cp)
    return cp

_sentinel = object()

class ConfigWrapper(object):
    def __init__(self, cp):
        self.cp = cp

    def get(self, key, default=_sentinel):
        try:
            val = self.cp.get("__main__", key)
            if default is not _sentinel and val == '':
                val = default
            return val
        except NoOptionError:
            if default is not _sentinel:
                return default
            else:
                raise
    def getint(self, key, default=_sentinel):
        try:
            return self.cp.getint("__main__", key)
        except NoOptionError:
            if default is not _sentinel:
                return default
            else:
                raise

    def getboolean(self, key, default=True):
        try:
            return self.cp.getboolean("__main__", key)
        except ConfigParser.NoOptionError:
            return default

def get_config(config_dir):
    cp = _get_config("lava-dispatcher", config_dir, schema=DispatcherSchema())
    valid, report = cp.is_valid(report=True)
    if not valid:
        logging.warning("dispatcher config is not valid:\n    %s", '\n    '.join(report))
    return ConfigWrapper(cp)


def get_device_config(name, config_dir):
    device_config = _get_config("devices/%s" % name, config_dir)
    cp = _get_config("device-defaults", config_dir, schema=DeviceSchema())
    _get_config(
        "device-types/%s" % device_config.get('__main__', 'device_type'),
        config_dir, cp=cp)
    _get_config("devices/%s" % name, config_dir, cp=cp)
    cp.set("__main__", "hostname", name)
    valid, report = cp.is_valid(report=True)
    if not valid:
        logging.warning("Config for %s is not valid:\n    %s", name, '\n    '.join(report))
    return ConfigWrapper(cp)
