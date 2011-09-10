#  -*- coding: utf-8 -*-

name = 'setup for the cache server'
group = 'special'

devices = dict(
    DB     = device('nicos.cache.server.FlatfileCacheDatabase',
                    storepath = '/data/cache',
                    loglevel = 'debug'),

    Server = device('nicos.cache.server.CacheServer',
                    db = 'DB',
                    server = 'mira1',
                    loglevel = 'info'),
)
