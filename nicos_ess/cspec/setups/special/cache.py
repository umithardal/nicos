description = 'setup for the cache server'
group = 'special'

devices = dict(
    serializer=device(
        'nicos.services.cache.entry.serializer.flatbuffers.FlatbuffersCacheEntrySerializer'),

    DB=device(
        'nicos.services.cache.database.kafka.KafkaCacheDatabaseWithHistory',
        currenttopic='TEST_nicosCacheCompacted',
        historytopic='TEST_nicosCacheHistory',
        brokers=["kafka:9092"],
        loglevel='info',
        serializer='serializer'
    ),
    Server = device('nicos.services.cache.server.CacheServer',
        db = 'DB',
        server = 'localhost',
        loglevel = 'info',
    ),
)
