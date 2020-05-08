from sympy import *
from sympy.vector import CoordSys3D
from mpmath import mp
from spec.component import *
from spec.motion import *
from spec.time import *
from utils.geometry import *

# for testing, a process with a point footprint

#TODO moving in straight line (FP is cylinder)
delta = 0.01

class PointProcess(Process):

    def __init__(self, name, x, y, z, parent = None, index = 0):
        super().__init__(name, parent, index)
        self.x = x
        self.y = y
        self.z = z
        self.dummyVar = Symbol(name + '_dummy')
        Idle(self)
        Wait(self)
    
    def internalVariables(self):
        return [self.dummyVar]
    
    def ownResources(self, point, maxError = 0.0):
        f = self.frame()
        if maxError > 0.0:
            pos = f.locate_new(self.name() + '_pos', self.x * f.i + self.y * f.j + self.z * f.k)
            return sphere(pos, maxError, point)
        else:
            (px,py,pz) = point.express_coordinates(f)
            return And(Eq(px, self.x), Eq(py, self.y), Eq(pz, self.z))
    
    def abstractResources(self, point, maxError = 0.0):
        return self.ownResources(point, maxError)

    def mountingPoint(self, index):
        return ValueException(self.name() + " does not have mounting moints.")


class Idle(MotionPrimitiveFactory):

    def __init__(self, component):
        super().__init__(component)

    def parameters(self):
        return []

    def setParameters(self, args):
        assert(len(args) == 0)
        return PointIdle(self.name(), self._component)

class PointIdle(MotionPrimitive):

    def __init__(self, name, component):
        super().__init__(name, component)

    def modifies(self):
        return [self._component.dummyVar]
    
    def duration(self):
        return DurationSpec(0, float('inf'), True) 

    def preG(self):
        return S.true

    def preFP(self, point):
        return self._component.abstractResources(point, delta) #FIXME deal with δ-sat

    def postFP(self, point):
        return self._component.abstractResources(point, delta)

    def invFP(self, point):
        i = self._component.abstractResources(point, delta)
        return self.timify(i)

class Wait(MotionPrimitiveFactory):

    def __init__(self, component):
        super().__init__(component)

    def parameters(self):
        return []

    def setParameters(self, args):
        if len(args) == 1:
            return PointWait(self.name(), self._component, args[0])
        elif len(args) == 2:
            return PointWait(self.name(), self._component, args[0], args[1])
        else:
            assert Fasle, "wrong args " + str(args)

class PointWait(MotionPrimitive):

    def __init__(self, name, component, t_min, t_max = -1):
        super().__init__(name, component)
        self.t_min = t_min
        if t_max < 0:
            self.t_max = t_min
        else:
            self.t_max = t_max

    def modifies(self):
        return [self._component.dummyVar]
    
    def duration(self):
        return DurationSpec(self.t_min, self.t_max, False)

    def preG(self):
        return S.true

    def preFP(self, point):
        return self._component.abstractResources(point, delta)

    def postFP(self, point):
        return self._component.abstractResources(point, delta)

    def invFP(self, point):
        i = self._component.abstractResources(point, delta)
        return self.timify(i)
