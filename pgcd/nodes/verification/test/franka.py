from sympy import *
from sympy.vector import CoordSys3D
from mpmath import mp
from spec import *
from utils.geometry import *

# A rough model for a franka emika panda arm
#
# Side view:
#     | |f------e--
#     | |--------\  \
#      g         | d|
#   -------      /  /
#   -------     / c/
#      h       /  /
#             /  /
#            | b|
#            |  |
#             a
#        ----------
#        -- base --
# data taken from:
# * https://www.franka.de/Panda_Datasheet_May_2019.pdf
# * https://frankaemika.github.io/docs/control_parameters.html to get an idea
# * https://github.com/frankaemika/franka_ros/tree/kinetic-devel/franka_description/robots



class FrankaEmikaPanda(Process):

    def __init__(self, name, parent, index = 0):
        # frame is the center of the base on the ground
        super().__init__(name, parent, index)
        # footrpint parameters
        # the arm is mounted at the center of the base
        self.base_x = 0.60
        self.base_y = 0.70
        self.base_z = 0.07
        # for the rest of the robot we use 3 cylinder and a cube for the last part
        # see https://frankaemika.github.io/docs/control_parameters.html to get an idea
        # footprint of the a+b part modeled as a cylinder
        self.ab_r = 0.13
        self.ab_h = 0.40
        # footprint of the c+d part modeled as a cylinder
        self.cd_r = 0.17
        self.cd_h = 0.40
        # footprint of the e+f part modeled as a cylinder
        self.ef_r = 0.17
        self.ef_h = 0.40
        # footprint of the g part as a cube
        self.g_x = 0.15
        self.g_y = 0.10
        self.g_z = 0.20
        # XXX we don't model the gripper
        # home offset (where the 0 position actually is compared to the neutral joint position)
        self.a_ref = 0.000000
        self.b_ref = -0.785398
        self.c_ref = -0.000000
        self.d_ref = -2.356195
        self.e_ref = 0.000000
        self.f_ref = 1.570796
        self.g_ref = 0.785398
        # state variables (see ascii art above)
        self._a = symbols(name + '_a')
        self._b = symbols(name + '_b')
        self._c = symbols(name + '_c')
        self._d = symbols(name + '_d')
        self._e = symbols(name + '_e')
        self._f = symbols(name + '_f')
        self._g = symbols(name + '_g')
        # angles limits
        self.minAngleA = -2.8973 - self.a_ref
        self.maxAngleA =  2.8973 - self.a_ref 
        self.minAngleB = -1.7628 - self.b_ref
        self.maxAngleB =  1.7628 - self.b_ref
        self.minAngleC = -2.8973 - self.c_ref
        self.maxAngleC =  2.8973 - self.c_ref
        self.minAngleD = -3.0718 - self.d_ref
        self.maxAngleD = -0.0698 - self.d_ref
        self.minAngleE = -2.8973 - self.e_ref
        self.maxAngleE =  2.8973 - self.e_ref
        self.minAngleF = -0.0175 - self.f_ref
        self.maxAngleF =  3.7525 - self.f_ref
        self.minAngleG = -2.8973 - self.g_ref
        self.maxAngleG =  2.8973 - self.g_ref
        # frame and stuff
        self._frame = parent.mountingPoint(index)
        self._af = self._frame.orient_new_axis( name + '_af', self._a + self.a_ref, self._frame.k, location= self.base_z * self._frame.k)
        self._bf = self._af.orient_new_axis(    name + '_bf', self._b + self.b_ref, self._af.j,    location= 0.333 * self._af.k)
        self._cf = self._bf.orient_new_axis(    name + '_cf', self._c + self.c_ref, self._bf.k,    location= 0.316 * self._bf.k)
        self._df = self._cf.orient_new_axis(    name + '_df', self._d + self.d_ref, self._cf.j,    location= 0.0825 * self._cf.i)
        self._ef = self._df.orient_new_axis(    name + '_ef', self._e + self.e_ref, self._df.k,    location=-0.0825 * self._df.i)
        self._ff = self._ef.orient_new_axis(    name + '_ff', self._f + self.f_ref, self._ef.j,    location= 0.384 * self._ef.k)
        self._effector = self._ff.locate_new(name + '_effector', 0.088 * self._ff.i)
        # motion primitives
        Idle(self)
        HomePos(self)
        MoveTo(self)
        Grasp(self)
        Open(self)
    
    def frame(self):
        return self._frame
    
    def internalVariables(self):
        return [self._a, self._b, self._c, self._d, self._e, self._f, self._g]

    # min and max for all the angles
    def invariant(self):
        domain_a = And(self._a >= self.minAngleA, self._a <= self.maxAngleA)
        domain_b = And(self._b >= self.minAngleB, self._b <= self.maxAngleB)
        domain_c = And(self._c >= self.minAngleC, self._c <= self.maxAngleC)
        domain_d = And(self._d >= self.minAngleD, self._d <= self.maxAngleD)
        domain_e = And(self._e >= self.minAngleE, self._e <= self.maxAngleE)
        domain_f = And(self._f >= self.minAngleF, self._f <= self.maxAngleF)
        domain_g = And(self._g >= self.minAngleG, self._g <= self.maxAngleG)
        return And(domain_a, domain_b, domain_c, domain_d, domain_e, domain_f, domain_g)
        
    def ownResources(self, point, delta = 0.0):
        lowerBackLeft1   = -self.base_x * self._frame.i / 2 - self.base_y * self._frame.j / 2
        upperFrontRight1 =  self.base_x * self._frame.i / 2 + self.base_y * self._frame.j / 2 + self.base_z * self._frame.k
        baseFP = cube(self._frame, lowerBackLeft1, upperFrontRight1, point, delta)
        #
        abFP = cylinder(self._af, self.upperArmRadius, self.upperArmLength, point, delta)
        cdFP = cylinder(self._cf, self.lowerArmRadius, self.lowerArmLength, point, delta)
        efFP = cylinder(self._ef, self.lowerArmRadius, self.lowerArmLength, point, delta)
        #
        lowerBackLeft2   = -self.base_x * self._effector.i / 2 - self.base_y * self._effector.j / 2 - self.base_z / 2 * self._effector.k
        upperFrontRight2 =  self.base_x * self._effector.i / 2 + self.base_y * self._effector.j / 2 + self.base_z / 2 * self._effector.k
        effectorFP = cube(self._effector, lowerBackLeft2, upperFrontRight2, point, delta)
        return Or(baseFP, abFP, cdFP, efFP, effectorFP)
    
    # overapproax of the workspace in https://www.franka.de/Panda_Datasheet_May_2019.pdf
    def abstractResources(self, point, delta = 0.0):
        # delta makes it bigger
        return cylinder(self.frame(), 0.855, 1.26, point, delta)
    
    def mountingPoint(self, index):
        assert(index == 0)
        return self._effector



class HomePos(MotionPrimitiveFactory):

    def __init__(self, component):
        super().__init__(component)

    def setParameters(self, args):
        assert(len(args) == 0)
        return FrankaHomePos(self.name(), self._component)

class FrankaHomePos(MotionPrimitive):

    def __init__(self, name, component):
        super().__init__(name, component)
    
    def duration(self):
        return DurationSpec(0, 2, False) #TODO upper as function of the angle and speed

    def pre(self):
        return S.true

    def post(self):
        return And(Eq(self._a, 0), Eq(self._b, 0), Eq(self._c, 0), Eq(self._d, 0), Eq(self._e, 0), Eq(self._f, 0), Eq(self._g, 0))

    def preFP(self, point):
        return self._component.abstractResources(point, 0.05)

    def postFP(self, point):
        return self._component.abstractResources(point, 0.05)

    def invFP(self, point):
        i = self._component.abstractResources(point, 0.05)
        return self.timify(i)



class Idle(MotionPrimitiveFactory):

    def __init__(self, component):
        super().__init__(component)

    def setParameters(self, args):
        assert(len(args) == 0)
        return FrankaIdle(self.name(), self._component)

class FrankaIdle(MotionPrimitive):

    def __init__(self, name, component):
        super().__init__(name, component)

    def modifies(self):
        return []

    def duration(self):
        return DurationSpec(0, float('inf'), True) 

    def pre(self):
        return S.true

    def post(self):
        return S.true

    def inv(self):
        return S.true

    def preFP(self, point):
        return self._component.abstractResources(point, 0.05)

    def postFP(self, point):
        return self._component.abstractResources(point, 0.05)

    def invFP(self, point):
        i = self._component.abstractResources(point, 0.05)
        return self.timify(i)



# since we don't precisely model the gripper, it is like waiting
class Grasp(MotionPrimitiveFactory):

    def __init__(self, component):
        super().__init__(component)

    def parameters(self):
        return ["grasp width"]

    def setParameters(self, args):
        assert(len(args) == 1)
        return ArmWait(self.name(), self._component)



# since we don't precisely model the gripper, it is like waiting
class Open(MotionPrimitiveFactory):

    def __init__(self, component):
        super().__init__(component)

    def setParameters(self, args):
        assert(len(args) == 0)
        return ArmWait(self.name(), self._component)

class FrankaWait(MotionPrimitive):

    def __init__(self, name, component):
        super().__init__(name, component)

    def modifies(self):
        return []
    
    def duration(self):
        return DurationSpec(0, 1, False) #TODO

    def pre(self):
        return S.true

    def post(self):
        return S.true

    def inv(self):
        return S.true

    def preFP(self, point):
        return self._component.abstractResources(point, 0.05)

    def postFP(self, point):
        return self._component.abstractResources(point, 0.05)

    def invFP(self, point):
        i = self._component.abstractResources(point, 0.05)
        return self.timify(i)



class MoveFromTo(MotionPrimitiveFactory):

    def __init__(self, component):
        super().__init__(component)

    def parameters(self):
        return ["a src", "b src", "c src", "d src", "e src", "f src", "g src",
                "a dst", "b dst", "c dst", "d dst", "e dst", "f dst", "g dst"]

    def setParameters(self, args):
        assert(len(args) == 14)
        return FrankaHomePos(self.name(), self._component,
                             args[0], args[1], args[2], args[3], args[4], args[5], args[6],
                             args[7], args[8], args[9], args[10], args[11], args[12], args[13])

class FrankaMoveFromTo(MotionPrimitive):

    def __init__(self, name, component, a0, b0, c0, d0, e0, f0, g0, a1, b1, c1, d1, e1, f1, g1):
        super().__init__(name, component)
        self.a0 = a0
        self.b0 = b0
        self.c0 = c0
        self.d0 = d0
        self.e0 = e0
        self.f0 = f0
        self.g0 = g0
        self.a1 = a1
        self.b1 = b1
        self.c1 = c1
        self.d1 = d1
        self.e1 = e1
        self.f1 = f1
        self.g1 = g1
    
    def duration(self):
        return DurationSpec(0, 2, False) #TODO upper as function of the angle and speed

    def pre(self, err = 0.1):
        return And(self.a0 - err <= self.component._a, self.component._a <= self.a0 + err,
                   self.b0 - err <= self.component._b, self.component._b <= self.b0 + err,
                   self.c0 - err <= self.component._c, self.component._c <= self.c0 + err,
                   self.d0 - err <= self.component._d, self.component._d <= self.d0 + err,
                   self.e0 - err <= self.component._e, self.component._e <= self.e0 + err,
                   self.f0 - err <= self.component._f, self.component._f <= self.f0 + err,
                   self.g0 - err <= self.component._g, self.component._g <= self.g0 + err)

    def inv(self, err = 0.1):
        return And(Min(self.a0, self.a1) - err <= self.component._a, self.component._a <= Max(self.a0, self.a1) + err,
                   Min(self.b0, self.b1) - err <= self.component._b, self.component._b <= Max(self.b0, self.b1) + err,
                   Min(self.c0, self.c1) - err <= self.component._c, self.component._c <= Max(self.c0, self.c1) + err,
                   Min(self.d0, self.d1) - err <= self.component._d, self.component._d <= Max(self.d0, self.d1) + err,
                   Min(self.e0, self.e1) - err <= self.component._e, self.component._e <= Max(self.e0, self.e1) + err,
                   Min(self.f0, self.f1) - err <= self.component._f, self.component._f <= Max(self.f0, self.f1) + err,
                   Min(self.g0, self.g1) - err <= self.component._g, self.component._g <= Max(self.g0, self.g1) + err)

    def post(self, err = 0.0):
        return And(self.a1 - err <= self.component._a, self.component._a <= self.a1 + err,
                   self.b1 - err <= self.component._b, self.component._b <= self.b1 + err,
                   self.c1 - err <= self.component._c, self.component._c <= self.c1 + err,
                   self.d1 - err <= self.component._d, self.component._d <= self.d1 + err,
                   self.e1 - err <= self.component._e, self.component._e <= self.e1 + err,
                   self.f1 - err <= self.component._f, self.component._f <= self.f1 + err,
                   self.g1 - err <= self.component._g, self.component._g <= self.g1 + err)

    def preFP(self, point):
        return self._component.abstractResources(point, 0.05)

    def postFP(self, point):
        return self._component.abstractResources(point, 0.05)

    def invFP(self, point):
        i = self._component.abstractResources(point, 0.05)
        return self.timify(i)
