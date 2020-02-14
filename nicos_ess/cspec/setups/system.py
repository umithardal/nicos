#  -*- coding: utf-8 -*-

description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = None,
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'liveview'],
)

modules = ['nicos.commands.standard', 'nicos_ess.cspec.commands.filewriter']

devices = dict(
    cspec = device('nicos.devices.instrument.Instrument',
        description = 'CSPEC instrument',
        facility = 'European Spallation Source (ESS)',
        instrument = 'CSPEC',
        responsible = 'P.P. Deen <pascale.deen@esss.se>',
        website = 'https://europeanspallationsource.se/instruments/cspec',
        operators = ['European Spallation Source (ESS)',
                     u'Technische Universität München (TUM)',
        ]
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = 'data',
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        lowlevel = True,
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        lowlevel = True,
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
        lowlevel = True,
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
    liveview=device('nicos.devices.datasinks.LiveViewSink', ),
    NexusDataSink=device(
        'nicos_ess.devices.datasinks.nexussink.NexusFileWriterSink',
        description="Sink for NeXus file writer (kafka-to-nexus)",
        brokers=["kafka:9092"],
        cmdtopic="TEST_writerCommand",
        status_provider='NexusFileWriter',
        templatesmodule='nicos_ess.essiip.nexus.nexus_templates',
        templatename='essiip_default',
        start_fw_file='/opt/nexus_templates/gareth.json'
    ),
    NexusFileWriter=device(
        'nicos_ess.devices.datasinks.nexussink.NexusFileWriterStatus',
        description="Status for nexus file writing",
        brokers=["kafka:9092"],
        statustopic="TEST_writerStatus",
    ),
    KafkaForwarder=device(
        'nicos_ess.devices.forwarder.EpicsKafkaForwarder',
        description="Configures commands to forward-epics-to-kafka",
        cmdtopic="TEST_forwarderConfig",
        statustopic="TEST_forwarderStatus",
        instpvtopic="",
        instpvschema='f142',
        brokers=["kafka:9092"],
    ),
)
