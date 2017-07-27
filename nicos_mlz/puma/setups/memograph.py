description = 'memograph readout'

includes = []

group = 'optional'

devices = dict(
    t_in_puma      = device('nicos_mlz.frm2.devices.memograph.MemographValue',
                            hostname = 'memograph-uja02.care.frm2',
                            group = 3,
                            valuename = 'T_in PUMA',
                            description = 'inlet temperature memograph',
                            fmtstr = '%.2F',
                            warnlimits = (-1, 17.5), #-1 no lower value
                            unit = 'degC',
                           ),
    t_out_puma     = device('nicos_mlz.frm2.devices.memograph.MemographValue',
                            hostname = 'memograph-uja02.care.frm2',
                            group = 3,
                            valuename = 'T_out PUMA',
                            description = 'outlet temperature memograph',
                            pollinterval = 30,
                            maxage = 60,
                            fmtstr = '%.2F',
                            unit = 'degC',
                           ),
    p_in_puma      = device('nicos_mlz.frm2.devices.memograph.MemographValue',
                            hostname = 'memograph-uja02.care.frm2',
                            group = 3,
                            valuename = 'P_in PUMA',
                            description = 'inlet pressure memograph',
                            pollinterval = 30,
                            maxage = 60,
                            fmtstr = '%.2F',
                            unit = 'bar',
                           ),
    p_out_puma     = device('nicos_mlz.frm2.devices.memograph.MemographValue',
                            hostname = 'memograph-uja02.care.frm2',
                            group = 3,
                            valuename = 'P_out PUMA',
                            description = 'outlet pressure memograph',
                            pollinterval = 30,
                            maxage = 60,
                            fmtstr = '%.2F',
                            unit = 'bar',
                           ),
    flow_in_puma   = device('nicos_mlz.frm2.devices.memograph.MemographValue',
                            hostname = 'memograph-uja02.care.frm2',
                            group = 3,
                            valuename = 'FLOW_in PUMA',
                            description = 'inlet flow memograph',
                            pollinterval = 30,
                            maxage = 60,
                            fmtstr = '%.2F',
                            warnlimits = (0.2, 100), #100 no upper value
                            unit = 'l/min',
                           ),
    flow_out_puma  = device('nicos_mlz.frm2.devices.memograph.MemographValue',
                            hostname = 'memograph-uja02.care.frm2',
                            group = 3,
                            valuename = 'FLOW_out PUMA',
                            description = 'outlet flow memograph',
                            pollinterval = 30,
                            maxage = 60,
                            fmtstr = '%.2F',
                            unit = 'l/min',
                           ),
    leak_puma      = device('nicos_mlz.frm2.devices.memograph.MemographValue',
                            hostname = 'memograph-uja02.care.frm2',
                            group = 3,
                            valuename = 'Leak PUMA',
                            description = 'leakage memograph',
                            pollinterval = 30,
                            maxage = 60,
                            fmtstr = '%.2F',
                            warnlimits = (-1, 1), #-1 no lower value
                            unit = 'l/min',
                           ),
    cooling_puma   = device('nicos_mlz.frm2.devices.memograph.MemographValue',
                            hostname = 'memograph-uja02.care.frm2',
                            group = 3,
                            valuename = 'Cooling PUMA',
                            description = 'cooling power memograph',
                            pollinterval = 30,
                            maxage = 60,
                            fmtstr = '%.2F',
                            unit = 'kW',
                           ),
)
