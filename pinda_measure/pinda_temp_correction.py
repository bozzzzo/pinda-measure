import collections
import datetime
import itertools
import pandas as pd
import numpy as np
from decimal import Decimal

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

_Range = collections.namedtuple("_Range", "start, stop, num")


class Range(_Range):
    def __iter__(self):
        return iter(tuple(np.linspace(self.start, self.stop, self.num, dtype=Decimal)))

    @classmethod
    def parse(cls, s : str, default : 'Range') -> 'Range':
        parts = tuple(map(str.strip, s.split(":")))
        if len(parts) != 3:
            raise ValueError("Expected three integers start:end:num")
        def opt(t,s,d):
            return t(s) if s else t(d)
        return cls(
            opt(float, parts[0], default.start),
            opt(float, parts[1], default.stop),
            opt(int, parts[2], default.num))

    def __str__(self):
        return "{self.start}:{self.stop}:{self.num}".format(self=self)


class PindaScanConfig(_PindaScanConfig):

    @classmethod
    def default(cls) -> 'PindaScanConfig':
        return PindaScanConfig(
            X=Range(0, 210, 5),
            Y=Range(-3, 207, 5),
            cycles=1,
            temp_range=Range(20,20,1),
        )

    def __str__(self):
        return "{self.__class__.__name__}({args})".format(
            self=self,
            args=", ".join(itertools.starmap("{}={}".format,
                                             zip(self._fields, self))),
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
        Y = tuple(self.config.Y)
        X = tuple(self.config.X)
        for y,x in zip((i for i in Y for j in X), itertools.cycle((X + X[::-1]))):
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

    def save_csv(self, points, filename="results.%Y%m%d%H%M.csv"):
        df = pd.DataFrame.from_records(points, columns=PindaTrigger._fields)
        results = datetime.datetime.now().strftime(filename)
        df.to_csv(results)
        print("\nWrote", results)

