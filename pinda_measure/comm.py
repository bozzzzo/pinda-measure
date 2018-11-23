import collections
from decimal import Decimal
from serial import Serial
from math import sqrt, pi


class Port(object):

    def log(self, x):
        if self._log:
            print(x)
        pass

    def until(self, what, why="Wait"):
        while True:
            row = self.port.readline().strip().decode("ASCII")
            if not row:
                continue
            self.log(why + ": >" + row + "<")
            yield row
            if what(row):
                break

    def wait(self, x):
        return list(x)

    def command(self, c):
        c = c.split(";", 1)[0].strip()
        if not c:
            return
        self.log(">>> " + c)
        self.port.write((c + "\r\n").encode("ASCII"))
        return self.wait(self.until(lambda row: row.startswith("ok")))

    def command_block(self, c):
        for cmd in c.splitlines():
            self.command(cmd.strip())

    def __init__(self, device="/dev/cu.usbmodem1411", log=True):
        self._log = log
        self.port = Serial()
        self.port.close()
        self.port.port = device
        self.port.baudrate = 115200
        self.port.timeout = 0.25
        self.port.dtr = True
        self.port.open()
        self.log("port opened")
        self.port.write(";\r\n".encode("ASCII"))
        self.wait(self.until(lambda row: row == "start", why="pre Init"))
        self.wait(self.until(lambda row: row.startswith("FSensor"),
                             why="Init"))
        self.log("start seen")
        self.port.write("M105\r\n".encode("ASCII"))
        self.port.write(";\r\n".encode("ASCII"))
        self.wait(self.until(lambda row: row.startswith("ok"),
                             why="post Init"))


class FilePort(Port):
    def __init__(self, file):
        self.file = open(file, "wb")

    def command(self, c):
        self.file.write((c + "\r\n").encode("ASCII"))

    def wait(self, x):
        pass

    def until(self, *args, **kwargs):
        pass


D = 1.75


class Extruder(object):
    def __init__(self, port, x=0, y=0, z=0, h=0.2, w=0.45):
        self.port = port
        self.x = x
        self.y = y
        self.z = z
        self._speed = None
        self.e_scale = (4 * w * h) / (pi * D**2)
        self.retraction = 0.8
        self.retract_state = True

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, speed):
        self._speed = speed

    def command(self, cmd, **kwargs):
        return self.port.command(" ".join(
            [cmd] + ["{}{}".format(k.upper(), v)
                     for k, v in kwargs.items()
                     if v is not None]))

    def home_all(self):
        self.command("G28", w='')

    def wait(self, message=None, p=None, s=None):
        args = dict(p=p, s=s)
        if message is not None:
            args[">>>"] = " {}".format(message)
        self.command("M0", **args)

    def g1(self, x=None, y=None, z=None, **kwargs):
        self.command("G1", x=x, y=y, z=z, **kwargs)
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if z is not None:
            self.z = z

    def extrude(self, x, y, f):
        self.retract(False)
        l = sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        e = self.e_scale * l
        self.g1(x=x, y=y, e=e, f=f)

    def move(self, x=None, y=None, f=None, z=None):
        self.retract(True)
        self.g1(x=x, y=y, z=z, f=f or self.speed)

    def retract(self, state):
        if self.retract_state == state:
            return
        e = self.retraction * (self.retract_state - state)
        self.g1(e=e, f=2400)
        self.retract_sotate = state

    def m105(self):
        data = self.command("M105")[-1]
        data = data.replace(" /", "/")
        data = data.split()[1:]
        data = {k: parseTemp(v) for k, v in (i.split(":") for i in data)}
        return Temps(T=data['T'], B=data['B'], P=data['P'], A=data['A'],
                     raw=data)

    def m211(self, s):
        self.command("M211", s=s)

    def bed_probe(self):
        return parse_bed_probe(self.command("G30"))

    def get_pinda_temp(self):
        return self.m105().P.current

    def get_bed_temp(self):
        return self.m105().P.current

    def m119(self):
        data = self.command("M119")
        return data

    def endstops(self):
        data = [x.split(":") for x in self.m119()[-7:-1]]
        return Endstops(**{k: (v.strip()=="TRIGGERED") for k,v in data})

    def where(self):
        data = self.command("M114")[-2]
        data = data.split()[:4]
        data = {k: Decimal(v) for k,v in (i.split(":") for i in data)}
        return Position(**data)

    def finish_all_moves(self):
        self.command("M400")

    def bed_temp(self, temp, wait=False):
        if wait:
            self.command("M190", s=temp)
        else:
            self.command("M140", s=temp)

    def hotend_temp(self, temp, wait=False):
        if wait:
            self.command("M109", s=temp)
        else:
            self.command("M104", s=temp)

    def part_fan(self, speed):
        if speed:
            speed = max(speed, 20)
        self.command("M106", s=speed)

def parseTemp(temp):
    temp = temp.split("/")
    if len(temp) == 1:
        return Temp(Decimal(temp[0]), None)
    else:
        return Temp(Decimal(temp[0]), Decimal(temp[1]))

def parse_bed_probe(probe):
    probe = probe[-2]
    probe = probe.split()
    return BedProbe(Decimal(probe[2]), Decimal(probe[4]), Decimal(probe[6]))

BedProbe = collections.namedtuple("BedProbe", "X, Y, Z")

Temp = collections.namedtuple("Temp", "current, target")
Temps = collections.namedtuple("Temps", "T,B,P,A,raw")
Endstops = collections.namedtuple("Endstops", ["{}_{}".format(a,b)
                                               for a in "xyz"
                                               for b in ["min","max"]])
Position = collections.namedtuple("Position", "X,Y,Z,E")
