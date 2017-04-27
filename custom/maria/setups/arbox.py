# -*- coding: utf-8 -*-

description = "MARIA Argon box monitoring setup"

group = "optional"

tango_base = "tango://phys.maria.frm2:10000/maria/"

devices = dict(
    ArDiff_p1 = device("devices.tango.AnalogInput",
         description = "Difference pressure between box and guide hall",
         tangodevice = tango_base + "FZJDP_Analog/ArDiff_p1",
         fmtstr = "%.2f",
         unit = "mbar",
         pollinterval = 5,
         maxage = 6,
    ),
    ArDiff_p2 = device("devices.tango.AnalogInput",
         description = "Difference pressure between box and guide hall",
         tangodevice = tango_base + "FZJDP_Analog/ArDiff_p2",
         fmtstr = "%.2f",
         unit = "mbar",
         pollinterval = 5,
         maxage = 6,
    ),
    GuideHall_p = device("devices.tango.AnalogInput",
         description = "Pressure in guide hall",
         tangodevice = tango_base + "FZJDP_Analog/GuideHall_p",
         fmtstr = "%.0f",
         unit = "mbar",
         pollinterval = 5,
         maxage = 6,
    ),
    ArO2_fill1 = device("devices.tango.AnalogInput",
         description = "O2 level in Ar box",
         tangodevice = tango_base + "FZJDP_Analog/ArO2_fill1",
         fmtstr = "%.2f",
         unit = "%",
         pollinterval = 5,
         maxage = 6,
    ),
    ArO2_fill2 = device("devices.tango.AnalogInput",
         description = "O2 level in Ar box",
         tangodevice = tango_base + "FZJDP_Analog/ArO2_fill2",
         fmtstr = "%.2f",
         unit = "%",
         pollinterval = 5,
         maxage = 6,
    ),
    GuideHallO2_fill = device("devices.tango.AnalogInput",
         description = "O2 level in guide hall",
         tangodevice = tango_base + "FZJDP_Analog/GuideHallO2_fill",
         fmtstr = "%.2f",
         unit = "%",
         pollinterval = 5,
         maxage = 6,
    ),
    T_ar_air = device("devices.tango.AnalogInput",
         description = "Argon box air temperature",
         tangodevice = tango_base + "FZJDP_Analog/TArAir",
         fmtstr = "%.1f",
         unit = "C",
         pollinterval = 5,
         maxage = 6,
    ),
    T_ar_laser = device("devices.tango.AnalogInput",
         description = "Argon box laser temperature",
         tangodevice = tango_base + "FZJDP_Analog/TArLaserMagicBox",
         fmtstr = "%.1f",
         unit = "C",
         pollinterval = 5,
         maxage = 6,
    ),
    T_ar_board = device("devices.tango.AnalogInput",
         description = "Argon box mu board temperature",
         tangodevice = tango_base + "FZJDP_Analog/TArBoardMagicBox",
         fmtstr = "%.1f",
         unit = "C",
         pollinterval = 5,
         maxage = 6,
    ),
)
