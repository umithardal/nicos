description = 'setup for the poller'
group = 'special'

sysconfig = dict(
    cache = 'localhost'
)

devices = dict(
    Poller = device('nicos.services.poller.Poller',
        alwayspoll = [  # setups that should be polled regardless if loaded
            'outerworld'
        ],
        neverpoll = [],  # setups that should not be polled even if loaded
        blacklist = [],  # DEVICES that should never be polled
        # (usually detectors or devices that have problems
        # with concurrent access from processes)
    ),
)
