# Copyright (c) 2016 - I.T. Dev Ltd
#
# This file is part of MCVirt.
#
# MCVirt is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# MCVirt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MCVirt.  If not, see <http://www.gnu.org/licenses/>

import socket


def get_hostname():
    """Returns the hostname of the system"""
    return socket.gethostname()


def get_all_submodules(target_class):
    """Returns all inheriting classes, recursively"""
    subclasses = []
    for subclass in target_class.__subclasses__():
        subclasses.append(subclass)
        subclasses += get_all_submodules(subclass)
    return subclasses