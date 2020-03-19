description = "setup for the cache server"
group = "special"

devices = dict(
    serializer=device(
        "nicos.services.cache.entry.serializer.flatbuffers.FlatbuffersCacheEntrySerializer"
    ),
    DB=device(
        "nicos.services.cache.database.kafka.KafkaCacheDatabaseWithHistory",
        currenttopic="UTGARD_nicosCacheCompacted",
        historytopic="UTGARD_nicosCacheHistory",
        brokers=["dmsc-kafka01.cslab.esss.lu.se:9092"],
        loglevel="info",
        serializer="serializer",
    ),
    Server=device(
        "nicos.services.cache.server.CacheServer", db="DB", server="", loglevel="info"
    ),
)
