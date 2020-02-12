description = "just-bin-it"

devices = dict(
    det=device(
        "nicos_ess.devices.datasources.just_bin_it.JustBinItDetector",
        description="The just-bin-it histogrammer",
        hist_topic="just-bin-it",
        data_topic="fake_events",
        brokers=["kafka:9092"],
        unit="evts",
        command_topic="hist_commands",
    ),
    heart_beat=device(
        "nicos_ess.devices.datasources.just_bin_it.JustBinItStatus",
        brokers=["kafka:9092"],
        statustopic="jbi_heartbeat",
    ),
)
