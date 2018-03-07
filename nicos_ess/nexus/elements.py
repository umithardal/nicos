#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from nicos import session
from nicos.core import ConfigurationError, NicosError
from nicos.pycompat import iteritems, string_types
from nicos_ess.nexus.placeholder import PlaceholderBase, DeviceValuePlaceholder


class NexusElementBase(object):
    """ Interface class to define nexus elements. All NeXus elements define
    a method which represents the dict of this element.
    """

    def structure(self, name, metainfo):
        """ Provides the JSON for current element in NeXus structure
        :param name: Name of the element
        :param metainfo: metainfo from *dataset*
        :return: dict of the NeXus structure
        """
        raise NotImplementedError()


class NXAttribute(NexusElementBase):
    """ Class to represent NeXus Attribute
    """

    def __init__(self, value, dtype=None):
        self.value = value
        self.dtype = dtype

    def structure(self, name, metainfo):
        # Return the name and current value if value is not None

        # If the value is a placeholder then get the value from this
        # placeholder
        if isinstance(self.value, PlaceholderBase):
            info = self.value.fetch_info(metainfo)
            if not info:
                session.log.warning('Unable to fetch info for placeholder'
                                    ' %s', self.value)
                return {}
            self.value = info[0]

        # The value now should be of desired numeric/string type.
        if self.value is None:
            return {}

        return {name: self.value}


class NXDataset(NexusElementBase):
    """ Class to represent NeXus Datasets. Each dataset can have
    a data type and additional attributes.
    """

    def __init__(self, value, dtype=None, **attr):
        self.value = value
        self.dtype = dtype
        self.attrs = {}
        for key, val in iteritems(attr):
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val)
            self.attrs[key] = val

    def structure(self, name, metainfo):
        # If the value is a placeholder then get the details from this
        # placeholder
        if isinstance(self.value, PlaceholderBase):
            info = self.value.fetch_info(metainfo)
            if not info:
                session.log.warning('Unable to fetch info for placeholder'
                                    ' %s', self.value)
                return {}

            # Set the value and the unit from the info string
            self.value = info[0]
            if info[2]:
                # Write the units attribute
                self.attrs["units"] = NXAttribute(info[2])

        # Return nothing if value is None
        if self.value is None:
            return {}

        root_dict = {
            "type": "dataset",
            "name": name,
            "values": self.value,
        }

        # For lists and strings type is required
        if not self.dtype:
            if isinstance(self.value, list) and self.value:
                if isinstance(self.value[0], int):
                    self.dtype = "int32"
                elif isinstance(self.value[0], long):
                    self.dtype = "int64"
                elif isinstance(self.value[0], float):
                    self.dtype = "double"
                elif isinstance(self.value[0], string_types):
                    self.dtype = "string"

            if isinstance(self.value, string_types):
                self.dtype = 'string'

        # Add the 'dtype' if specified
        if self.dtype:
            root_dict['dataset'] = {"type": self.dtype}

            # If the type is string/list then the size is to be written
            if self.dtype == "string":
                root_dict['dataset']['string_size'] = len(self.value) + 1
            if isinstance(self.value, list):
                # Only 1D array supported by NICOS
                root_dict['dataset']['size'] = [len(self.value)]

        # Add the attributes if present
        if self.attrs:
            attr_dict = {}
            for attr_name, attr in iteritems(self.attrs):
                # It is important to check if the type is of NXAttribute
                # Subclasses can directly change the self.attrs dict
                if isinstance(attr, NXAttribute):
                    attr_structure = attr.structure(attr_name, metainfo)
                    if attr_structure:
                        attr_dict.update(attr_structure)

            root_dict["attributes"] = attr_dict

        return root_dict


class NXGroup(NexusElementBase):
    """ Class to represent NeXus Group. Each group has a class type and
    can additionally have children in the form of datasets and groups or
    can also have attributes associated.
    """

    def __init__(self, nxclass):
        self.nxclass = nxclass
        self.children = {}
        self.attrs = {}

    def structure(self, name, metainfo):
        val = {
            "type": "group",
            "name": name,
            "attributes": {
                "NX_class": self.nxclass
            },
            "children": []
        }

        # Add the children
        if self.children:
            for ename, entry in iteritems(self.children):
                if isinstance(entry, NexusElementBase):
                    child_dict = entry.structure(ename, metainfo)
                    if child_dict:
                        val["children"].append(child_dict)
                else:
                    session.log.info("%s does not provide value!!", ename)

        # Add the attributes
        if self.attrs:
            attr_dict = {}
            for attr_name, attr in iteritems(self.attrs):
                # It is important to check if the type is of NXAttribute
                # Subclasses can directly change the self.attrs dict
                if isinstance(attr, NXAttribute):
                    attr_structure = attr.structure(attr_name, metainfo)
                    if attr_structure:
                        attr_dict.update(attr_structure)

            val["attributes"].update(attr_dict)

        return val


class KafkaStream(NXGroup):
    """ Class to represent Kafka streams. Kafka streams always appear as
    groups. The defined properties of the stream can be set. The FileWriter
    using these properties and fills up the data in the files using messages
    from Kafka.
    """
    stream_keys = ['broker', 'topic', 'source', 'module', 'type', 'array_size']

    def __init__(self, nxclass, **attr):
        NXGroup.__init__(self, nxclass=nxclass)

        self.stream = {}
        for key in self.stream_keys:
            self.stream[key] = None

        self.stream_attrs = {}
        for key, val in iteritems(attr):
            if not isinstance(val, NXAttribute):
                val = NXAttribute(val)
            self.stream_attrs[key] = val

    def set(self, key, value):
        if key not in self.stream:
            session.log.error('Unidentified key %s set for kafka stream', key)
            return
        self.stream[key] = value

    def structure(self, name, metainfo):
        root_dict = NXGroup.structure(self, name, metainfo)
        stream_dict = {
            "type": "stream",
            "stream": {k: v for k, v in iteritems(self.stream) if v}
        }

        # Add the attributes
        if self.stream_attrs:
            attr_dict = {}
            for attr_name, attr in iteritems(self.stream_attrs):
                if isinstance(attr, NXAttribute):
                    attr_structure = attr.structure(attr_name, metainfo)
                    if attr_structure:
                        attr_dict.update(attr_structure)

            stream_dict["attributes"] = attr_dict

        root_dict["children"].append(stream_dict)
        return root_dict


class DeviceStream(DeviceValuePlaceholder, KafkaStream):
    """ Streams device parameter using data of associated PVs present in
    the form of Kafka messages. Note, to use this the forwarder must be
    forwarding the PVs to the topics. Internally, PV names are fetched
    from the device and corresponding topic and schema data is fetched
    from the Forwarder Device.
    """

    def __init__(self, device, parameter='value', **attr):
        KafkaStream.__init__(self, 'NXlog', **attr)
        DeviceValuePlaceholder.__init__(self, device, parameter)

    def structure(self, name, metainfo):
        device = session.getDevice(self.device)
        parameter = self.parameter

        if parameter == 'value':
            parameter = 'readpv'

        # Fetch the PV name for the parameter. This will fail if the
        # parameter name is not mapped to the PV in class
        source = device._get_pv_name(parameter)

        # Get the forwarded topic and schema for the PV
        try:
            forwarder = session.getDevice('KafkaForwarder')
        except ConfigurationError:
            session.log.warning("FORWARDER not found!! Can't track device "
                                "%s..", device.name)
            return

        if not forwarder.is_process_running():
            session.log.warning('Forwarder is not running. Correct values will'
                                ' not be written for device %s.', device.name)

        topicandschema = forwarder.pv_forwarding_info(source)
        if not topicandschema:
            raise NicosError('Info not found for device %s and its '
                             'property: %s' % (device.name, parameter))

        # Infer the type, count of PV
        dbr_type = device._pvs[parameter].type
        count = device._pvs[parameter].count
        if '_' in dbr_type:
            dbr_type = dbr_type.split('_')[-1]

        if count > 1:
            self.set('array_size', count)

        self.set('type', dbr_type)
        self.set('source', source)
        self.set('topic', topicandschema[0])
        self.set('module', topicandschema[1])

        # Add the attributes
        self.stream_attrs["nicos_name"] = NXAttribute(self.device)
        self.stream_attrs["nicos_param"] = NXAttribute(self.parameter)
        self.stream_attrs["source_name"] = NXAttribute(source)

        info = self.fetch_info(metainfo)
        if info:
            self.stream_attrs["units"] = NXAttribute(info[2])

        return KafkaStream.structure(self, name, metainfo)


class EventStream(KafkaStream):
    """ Stream that provides event data from Kafka
    """

    def __init__(self, topic, source, broker, mod='ev42', dtype='uint64',
                 **attr):
        KafkaStream.__init__(self, 'NXevent_data', **attr)
        self.set('topic', topic)
        self.set('source', source)
        self.set('broker', broker)
        self.set('module', mod)
        self.set('type', dtype)


class DeviceAttribute(NXAttribute):
    """ NeXus Attribute, the value of which comes from a *device*.
    The *parameter* to be fetched can be set, otherwise will fetch
    the value of the device. Optionally a data type can also be
    provided.
    """

    def __init__(self, device, parameter='value', dtype=None):
        val = DeviceValuePlaceholder(device, parameter)
        NXAttribute.__init__(self, val, dtype)


class DeviceDataset(NXDataset):
    """ NeXus Attribute, the value of which comes from a *device*.
    The *parameter* to be fetched can be set, otherwise will fetch
    the value of the device. Optionally a data type and attributes
    associated to this dataset can also be added.
    """

    def __init__(self, device, parameter='value', dtype=None, **attr):
        val = DeviceValuePlaceholder(device, parameter)
        NXDataset.__init__(self, val, dtype, **attr)

        # Set the NICOS data as attributes
        self.attrs["nicos_name"] = NXAttribute(device)
        self.attrs["nicos_param"] = NXAttribute(parameter)