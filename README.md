# PINDA measurements of repeatability, temperature stability, bed level

## Installation

        pip install git+https://github.com/bozzzzo/pinda-measure.git

### Upgrade

        pip install -U git+https://github.com/bozzzzo/pinda-measure.git

## Usage

          pinda_measure measure [options]
          pinda_measure show [<file>] [options]
          pinda_measure compare-G80 [options]
          pinda_measure --help
        
        Options:
          -x, --xrange=<xrange>      # X range to measure [default: 0:210:5]
          -y, --yrange=<yrange>      # Y range to measure [default: -3:207:5]
          -t, --temp_range=<trange>  # Bed temperatures to measure at
                                     #           [default: 20:20:1]
          -c, --cycles=<cycles>      # number of measurement cycles at each temperature
                                     #           [default: 1]
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

# Known Issues

## --temp-range is not supported in visualizations

Avoid `--temp-range` for now. Existing visualizations don't account for pinda
temperature drift nor firmware temperature corrections so the pictures will come
up but will probably show a jumbled mess.

you can collect measurements but need to interpret the data on your own (patches
accepted)

## using homemade serial support instead of printcore

seems to work for the use-case as-is. Can be adopted to printcore, at the
expense of more complex install...
