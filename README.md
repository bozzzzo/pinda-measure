# pinda-measure


        PINDA measurements of repeatability, temperature stability, bed level
        
        Usage:
          pinda_measure measure [options]
          pinda_measure show <file> [options]
        
        Options:
          -x, --xrange=<xrange>      # X range to measure [default: 0:210:5]
          -y, --yrange=<yrange>      # Y range to measure [default: -3:207:5]
          -t, --temp_range=<trange>  # Bed temperatures to measure at [default: 20:20:1]
          -c, --cycles=<cycles>      # number of measurement cycles at each temperature [default: 1]
          --num=<num>                # change number of points for X and Y range
          --port=<port>              # Serial port of the 3d printer [default: /dev/cu.usbmodem1411]
        
        Ranges are expressed as <start>:<end>:<num> with <num> points over the range
        <end> inclusive.
        
