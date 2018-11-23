import pandas as pd

from .comm import Port, FilePort, Extruder


def measure_G80(port):
    port.command("G80")
    data = port.command("G81")
    data = list(
        reversed(list(
            map(lambda row: list(map(float, row)),
                map(str.split, data[-8:-1])))))
    data = pd.DataFrame(data).round(3)
    return data.stack().reset_index().rename(
        columns={'level_0':'Y',
                 'level_1':'X',
                 0:'Z'})


def calibrate_linear_advance(port, k_range):
    intro = """
        M107
        M83                      ; extruder relative mode
        M104 S210                ; set extruder temp
        M140 S55                 ; set bed temp
        M190 S55                 ; wait for bed temp
        M109 S210                ; wait for extruder temp
        G28 W                    ; home all without mesh bed level
        G80                      ; mesh bed leveling
        G1 Y-3.0 F1000.0         ; go outside print area
        G1 X60.0 E9.0  F1000.0   ; intro line
        G1 X100.0 E12.5  F1000.0 ; intro line
        G21                      ; set units to millimeters
        G90                      ; use absolute coordinates
        M83                      ; use relative distances for extrusion
        G1 Z0.200 F7200.000
        M204 S500
                                 ; 20mm/s = F1200
                                 ; 70mm/s = F4200
                                 ; 120mm/s = F7200
        G1 E-0.80000 F2100.00000
        G1 X10 Y10 F7200.000
        G1 E0.80000 F2100.00000
    """

    outro = """
        M107
        G4                       ; wait
        M104 S0                  ; turn off temperature
        M140 S0                  ; turn off heatbed
        M107                     ; turn off fan
        G91                      ; relative cooridantes
        G1 Z100 F4500            ;
        G90                      ; set absolute coordinates
        G1 X0 Y200               ; home X axis
        M84                      ; disable motors
    """

    extruder = Extruder(port, 10, 10, 0.2, 0.45, 0.2)

    slooow = 600
    slow = 1200
    fast = 4200
    insane = 7200

    def calibration_line(k):
        y = k * 1.2 + 10
        extruder.command("M900", k=k)
        extruder.move(x=10, y=y, f=insane)         # beginning
        extruder.extrude(x=12, y=y, f=slooow)      # prime
        extruder.extrude(x=20, y=y, f=slow)        # prime
        extruder.extrude(x=50, y=y, f=slow)        # slow
        extruder.extrude(x=80, y=y, f=fast)        # fast
        extruder.extrude(x=100, y=y, f=slow)       # slow
        if k % 10 == 0:
            extruder.extrude(x=104, y=y, f=slow)   # slow
        elif k % 5 == 0:
            extruder.extrude(x=102, y=y, f=slow)   # slow
        extruder.move(x=105, y=y + 1, f=slow)      # empty

    port.command_block(intro)
    for k in k_range:
        calibration_line(k)
    port.command_block(outro)


if __name__ == "__main__":
    port = FilePort("K_factor_calibration.gcode")
    calibrate_linear_advance(port, range(0, 100, 1))
