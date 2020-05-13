description = 'Sample table'

group = 'lowlevel'

devices = dict(
    # x = device('nicos.devices.generic.Axis',
    #     description = 'X',
    #     motor = device('nicos.devices.generic.VirtualMotor',
    #         abslimits = (-10, 10),
    #         unit = 'mm',
    #         speed = 1,
    #         fmtstr = '%.2f',
    #     ),
    #     precision = 0.01,
    # ),
    # y = device('nicos.devices.generic.Axis',
    #     description = 'X',
    #     motor = device('nicos.devices.generic.VirtualMotor',
    #         abslimits = (-10, 10),
    #         unit = 'mm',
    #         speed = 1,
    #         fmtstr = '%.2f',
    #     ),
    #     precision = 0.01,
    # ),
    # z = device('nicos.devices.generic.Axis',
    #     description = 'Z',
    #     motor = device('nicos.devices.generic.VirtualMotor',
    #         abslimits = (0, 10),
    #         unit = 'mm',
    #         speed = 0.5,
    #         fmtstr = '%.2f',
    #     ),
    #     precision = 0.01,
    # ),
    sgx = device('nicos.devices.generic.Axis',
        description = 'SGX',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-4.5, 4.5),
            unit = 'deg',
            speed = 0.5,
            fmtstr = '%.2f',
        ),
        precision = 0.01,
    ),
    # sgy = device('nicos.devices.generic.Axis',
    #     description = 'SGY',
    #     motor = device('nicos.devices.generic.VirtualMotor',
    #         abslimits = (-10, 10),
    #         unit = 'deg',
    #         speed = 0.5,
    #         fmtstr = '%.2f',
    #     ),
    #     precision = 0.1,
    # ),
)
