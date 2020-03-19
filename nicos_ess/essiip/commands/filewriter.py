#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Matt Clarke <matt.clarke@esss.se>
#
# *****************************************************************************
from nicos import session
from nicos.commands import usercommand, parallel_safe
from nicos.core.constants import SIMULATION
import json
import os
import time
from kafka import KafkaProducer, KafkaConsumer, TopicPartition
from streaming_data_types.run_start_pl72 import serialise_pl72
from streaming_data_types.run_stop_6s4t import serialise_6s4t

FILE_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
FW_CONFIG_FILE = os.path.join(FILE_ROOT, "nexus_structure.txt")
JOB_ID = "62075348-cfe5-11e9-9141-c8f75089fb03"
BROKER = "172.30.242.20:9092"
COMMAND_TOPIC = "UTGARD_writerCommand"
RUNINFO_TOPIC = 'UTGARD_runInfo'
FILENUMBER_TOPIC ='nicos_filenumber'


@usercommand
@parallel_safe
def start_filewriter(title="No title"):
    """
    A hacky way of starting the NeXus Filewriter.
    """
    if session.mode == SIMULATION:
        session.log.info('=> dry run: starting file writing')
    else:
        file_id = get_file_number(update=True)
        filename = file_id.zfill(8) + ".hdf"
        start_time = int(time.time() * 1000)
        with open(FW_CONFIG_FILE, "r") as f:
            nexus_struct = f.read()

        start_message = serialise_pl72(
            job_id=file_id,
            filename=filename,
            start_time=start_time,
            nexus_structure=nexus_struct,
            broker=BROKER
        )

        session.log.info('Requested start of file writing job %s at: %s',
                         str(file_id), time.strftime('%Y-%m-%d %H:%M:%S',
                         time.localtime(start_time / 1000)))
        send_to_kafka(COMMAND_TOPIC, start_message)


@usercommand
@parallel_safe
def stop_filewriter(job_id=None):
    """
    A hacky way of stopping the NeXus Filewriter.
    """
    if session.mode == SIMULATION:
        session.log.info('=> dry run: stopping file writing')
    else:
        stop_time = int(time.time() * 1000)
        job_id = get_file_number() if not job_id else str(job_id)
        stop_message = serialise_6s4t(
            job_id=job_id,
            stop_time=stop_time,
        )

        session.log.info('Request job %s to stopped file writing at: %s',
                         job_id, time.strftime('%Y-%m-%d %H:%M:%S',
                         time.localtime(stop_time / 1000)))
        send_to_kafka(COMMAND_TOPIC, stop_message)


def send_to_kafka(topic, message):
    producer = KafkaProducer(bootstrap_servers=BROKER, max_request_size=100000000)
    producer.send(topic, bytes(message))
    producer.flush()


def get_file_number(update=False):
    consumer = KafkaConsumer(bootstrap_servers=BROKER)
    tp = TopicPartition(FILENUMBER_TOPIC, 0)

    # Get last value
    consumer.assign([tp])
    consumer.seek_to_end(tp)
    pos = consumer.position(tp)
    if pos > 0:
        consumer.seek(tp, pos - 1)

        data = []
        while not data:
            data = consumer.poll(5)
        curr = int(data[tp][-1].value)
    else:
        curr = 1

    if update:
        curr += 1
        send_to_kafka(FILENUMBER_TOPIC, str(curr).encode())
    return str(curr)

