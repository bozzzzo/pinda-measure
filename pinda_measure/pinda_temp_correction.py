import collections
import datetime
import itertools
import pandas as pd

_PindaTrigger = collections.namedtuple(
    "_PindaTrigger",
    "cycle,timestamp,X,Y,Z,temp,bed,nozzle,bed_target")


class PindaTrigger(_PindaTrigger):
    def __str__(self):
        return "{cycle:4} {timestamp} {X:9} {Y:9} {Z:9} P{temp:6} B{bed:6}/{bed_target:6} T{nozzle:6}".format(**(self._asdict()))


def pr(*x, spinner=itertools.cycle("-/|\\")):
    x = (next(spinner), ) + x
    print(*x, end=" "*20+"\r", flush=True)


_PindaScanConfig = collections.namedtuple(
    "_PindaScanConfig",
    "X,Y,cycles,temp_range")


class PindaScanConfig(_PindaScanConfig):

    @staticmethod
    def default():
        return PindaScanConfig(
            X=range(0, 211, 30),
            Y=range(-3, 208, 30),
            cycles=1,
            temp_range=range(20,21,5),
        )


class PindaScan:

    def __init__(self, e, config=PindaScanConfig.default()):
        self.e = e
        self.config = config
        self.start_time = datetime.datetime.now()

    def probe_bed(self, cycle=None):
        temps = self.e.m105()
        probe = self.e.bed_probe()
        return PindaTrigger(
            cycle=cycle or 0,
            timestamp=datetime.datetime.now() - self.start_time,
            X=probe.X,
            Y=probe.Y,
            Z=probe.Z,
            bed_target=temps.B.target,
            temp=temps.P.current,
            bed=temps.B.current,
            nozzle=temps.T.current)

    def sweep_area(self):
        Y = self.config.Y
        X = tuple(self.config.X)
        rX = tuple(reversed(self.config.X))
        for y,x in zip((i for i in Y for j in X), itertools.cycle((X + rX))):
            yield x, y

    def sweep_bed(self, cycle):
        for x,y in self.sweep_area():
            self.e.move(x=x, y=y)
            yield self.probe_bed(cycle=cycle)

    def sweep_pinda_temp_gradient(self):
        for temp in self.config.temp_range:
            self.e.move(100,100)
            self.e.bed_temp(temp, wait=True)
            for cycle in range(self.config.cycles):
                yield from self.sweep_bed(cycle)

    def scan_pinda(self):
        self.e.home_all()
        self.e.speed = 5000
        self.e.move(x=0,y=0)
        self.e.move(x=10,y=10)
        self.e.move(x=0,y=0)
        self.e.move(x=10,y=10)
        points = []
        try:
            for point in self.sweep_pinda_temp_gradient():
                pr(point)
                points.append(point)
        except KeyboardInterrupt:
            print()
            print("Interrupted, result file will be incomplete")
            pass
        self.e.bed_temp(0)
        self.e.hotend_temp(0)
        self.e.part_fan(0)
        self.e.move(x=0,y=0,z=50)
        return points

    def save_csv(self, points, filename="results.%Y%m%d%H%M.csv")
        df = pd.DataFrame.from_records(points, columns=PindaTrigger._fields)
        results = datetime.datetime.now().strftime(filename)
        df.to_csv(results)
        print("Wrote", results)

