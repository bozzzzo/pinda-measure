from .comm import Extruder, Port
from .pinda_temp_correction import PindaScan, PindaScanConfig

def call_main():
    e = Extruder(Port(log=False))
    p = PindaScan(e)
    points = p.scan_pinda()
    p.save_csv(points)
