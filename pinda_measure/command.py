"""
PINDA measurements of repeatability, temperature stability, bed level

Usage:
  pinda_measure measure [options]
  pinda_measure show [<file>] [options]
  pinda_measure compare-G80 [options]
  pinda_measure --help

Options:
  -x, --xrange=<xrange>      # X range to measure [default: {default.X}]
  -y, --yrange=<yrange>      # Y range to measure [default: {default.Y}]
  -t, --temp_range=<trange>  # Bed temperatures to measure at
                             #           [default: {default.temp_range}]
  -c, --cycles=<cycles>      # number of measurement cycles at each temperature
                             #           [default: {default.cycles}]
  --num=<num>                # change number of points for X and Y range
  --port=<port>              # Serial port of the 3d printer
                             #           [default: /dev/cu.usbmodem1411]
  --delta-last               # show additional heatmap of change
                             #   between this and last measurement
  --delta=<file>             # show additional heatmap of change
                             #   between this and specified measurement
  --help                     # show this help
  --version                  # print version

Ranges are expressed as <start>:<end>:<num> with <num> points over the range
<end> inclusive.

When no <file> is passed to show, the results of the last measurement in this
folder are used.

"""
import os
import glob
from docopt import docopt
from . import __version__
from .comm import Extruder, Port
from .pinda_temp_correction import PindaScan, PindaScanConfig, Range
from .measure import measure_G80


def parse_config(args, default):
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


def parse_extruder(args):
    return Extruder(Port(device=args["--port"], log=False))


def measure(args):
    config = parse_config(args, default=PindaScanConfig.default())
    e = parse_extruder(args)
    p = PindaScan(e, config=config)
    points = p.scan_pinda()
    df, f = p.save_csv(points)
    show(df, args, f=f)


def nth_youngest(n=1):
    results = sorted(glob.glob("*.csv"), key=os.path.getmtime)
    if len(results) < n:
        return None
    return results[-n]


def load_and_show(args):
    from .visualize_level import load_df
    f = args["<file>"]
    if f is None:
        f = nth_youngest(1)
    df = load_df(f)
    show(df, args, f=f)


def compare_G80(args):
    from . import visualize_level as vl
    e = parse_extruder(args)
    df1 = measure_G80(e)
    if args["--num"] is None:
        args["--num"] = "7"
    config = parse_config(args, default=PindaScanConfig.default())
    p = PindaScan(e, config=config)
    points = p.scan_pinda()
    df, f = p.save_csv(points)
    vl.show_heatmap(df1, title="G80 G81 report")
    show(df, args, f)


def show(df, args, f):
    from . import visualize_level as vl
    vl.show_heatmap(df, title="G30 mesh bed level probe ({})".format(f))
    vl.show_pinda_jitter(df)
    # show_XY_jitter(df)
    of = nth_youngest(2)
    if args["--delta-last"] and of:
        show_delta(df, f, of)
    if args["--delta"] and of:
        show_delta(df, f, args["--delta"])
    vl.plt.show()

def show_delta(df, f, of):
    from . import visualize_level as vl
    odf = vl.load_df(of)
    vl.show_delta_heatmap(df, odf, title="Difference ({}) - ({})".format(f, of))


def call_main():
    args = docopt(__doc__.format(default=PindaScanConfig.default()),
                  version='Pinda Measure {version}'.format(version=__version__))
    if args["measure"]:
        measure(args)
    elif args["show"]:
        load_and_show(args)
    elif args["compare-G80"]:
        compare_G80(args)

