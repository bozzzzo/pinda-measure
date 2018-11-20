"""
PINDA measurements of repeatability, temperature stability, bed level

Usage:
  pinda_measure measure [options]
  pinda_measure show <file> [options]

Options:
  -x, --xrange=<xrange>      # X range to measure [default: {default.X}]
  -y, --yrange=<yrange>      # Y range to measure [default: {default.Y}]
  -t, --temp_range=<trange>  # Bed temperatures to measure at [default: {default.temp_range}]
  -c, --cycles=<cycles>      # number of measurement cycles at each temperature [default: {default.cycles}]
  --num=<num>                # change number of points for X and Y range
  --port=<port>              # Serial port of the 3d printer [default: /dev/cu.usbmodem1411]

Ranges are expressed as <start>:<end>:<num> with <num> points over the range
<end> inclusive.

"""
from docopt import docopt
from decimal import Decimal
from .comm import Extruder, Port
from .pinda_temp_correction import PindaScan, PindaScanConfig, Range


def parse_config(args):
    default = PindaScanConfig.default()
    x = Range.parse(args["--xrange"], default.X)
    y = Range.parse(args["--yrange"], default.Y)
    num = args["--num"]
    if num:
        if x == default.X:
            x = x._replace(num=int(num))
        if y == default.Y:
            y = y._replace(num=int(num))
    config = default._replace(
        X=x,
        Y=y,
        cycles=int(args["--cycles"]),
        temp_range=Range.parse(args["--temp_range"], default.temp_range)
    )
    print(config)
    return config

def measure(args):
    config = parse_config(args)
    e = Extruder(Port(device=args["--port"], log=False))
    p = PindaScan(e, config=config)
    points = p.scan_pinda()
    df = p.save_csv(points)
    show(df)

def load_and_show(args):
    from .visualize_level import load_df
    f = args["<file>"]
    df = load_df(f)
    show(df)

def show(df):
    from .visualize_level import show_heatmap, plt
    show_heatmap(df)
    plt.show()

def call_main():
    args = docopt(__doc__.format(default=PindaScanConfig.default()),
                  version='Pinda Measure v0.0')
    if args["measure"]:
        measure(args)
    elif args["show"]:
        load_and_show(args)

