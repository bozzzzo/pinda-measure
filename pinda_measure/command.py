"""
PINDA measurements of repeatability, temperature stability, bed level

Usage:
  pinda_measure [options]

Options:
  --x=<xrange>     # X range to measure [default: {default.X}]
  --y=<yrange>     # Y range to measure [default: {default.Y}]
  --t=<trange>     # Bed temperatures to measure at [default: {default.temp_range}]
  --c=CYCLES       # number of measurement cycles at each temperature [default: {default.cycles}]

Ranges are expressed as <start>:<end>:<num> with <num> points over the range
<end> inclusive.

"""
from docopt import docopt
from decimal import Decimal
from .comm import Extruder, Port
from .pinda_temp_correction import PindaScan, PindaScanConfig, Range


def parse_config(args):
    default = PindaScanConfig.default()
    config = default._replace(
        X=Range.parse(args["--x"], default.X),
        Y=Range.parse(args["--y"], default.Y),
        cycles=int(args["--c"]),
        temp_range=Range.parse(args["--t"], default.temp_range)
    )
    return config


def call_main():
    args = docopt(__doc__.format(default=PindaScanConfig.default()),
                  version='Pinda Measure v0.0')
    config = parse_config(args)
    e = Extruder(Port(log=False))
    p = PindaScan(e, config=config)
    points = p.scan_pinda()
    p.save_csv(points)
