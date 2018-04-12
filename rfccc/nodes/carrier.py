#!/usr/bin/env python3.5

"""
Meccanum cart 
"""

from __future__ import division
import drv8825
import RPi.GPIO as GPIO
from time import sleep, time
import rospy

import sympy as sp

from multiprocessing import Process



class carrier():
    def __init__( self ):
        self.motor1 = drv8825.drv8825( pinDir = 11, pinStep = 12, pinEnable = 3, waitingTime=0.002 )
        self.motor2 = drv8825.drv8825( pinDir = 13, pinStep = 15, pinEnable = 3, waitingTime=0.002 )
        self.motor3 = drv8825.drv8825( pinDir = 16, pinStep = 18, pinEnable = 3, waitingTime=0.002 )
        self.motor4 = drv8825.drv8825( pinDir = 22, pinStep = 7, pinEnable = 3, waitingTime=0.002 )
    

        GPIO.setmode(GPIO.BOARD)
        self.pinEnable = 3
        self.pinMS1 = 5
        self.pinMS2 = 24
        self.pinMS3 = 26
        
        
        GPIO.setup( self.pinEnable, GPIO.OUT )
        GPIO.setup( self.pinMS1, GPIO.OUT )
        GPIO.setup( self.pinMS2, GPIO.OUT )
        GPIO.setup( self.pinMS3, GPIO.OUT )
        
        self.offset = 15.4

        self.stepsCart = 0 # angle in steps
        self.angleCart = 0 # angle in deg
        self.microstepping = 16 
        self.__microstepping__( 16 )
        print( self.microstepping )

        self.x = 0
        self.y = 0


    # Methods concerning moving the cart
    def __motors_start__( self ):
        GPIO.output( self.pinEnable, GPIO.LOW )

    def __motors_shutdown__( self ):
        GPIO.output( self.pinEnable, GPIO.HIGH )

    def __compute_steps__( self, straight, side, rotate ):
        """
        """
        coeff_straight=1
        coeff_side=2
        coeff_rotate=1
    
        steps_motor1 = coeff_straight * straight + coeff_side * side - coeff_rotate * rotate;
        steps_motor2 = coeff_straight * straight - coeff_side * side - coeff_rotate * rotate;
        steps_motor3 = coeff_straight * straight - coeff_side * side + coeff_rotate * rotate;
        steps_motor4 = coeff_straight * straight + coeff_side * side + coeff_rotate * rotate;

        if steps_motor1 > 0: 
            f = lambda: self.motor1.doStep( steps_motor1, 1 )
        else:
            f = lambda: self.motor1.doStep( -steps_motor1, 0 )

        if steps_motor2 > 0: 
            g = lambda: self.motor2.doStep( steps_motor2, 1 )
        else:
            g = lambda: self.motor2.doStep( -steps_motor2, 0 )
        
        if steps_motor3 > 0: 
            h = lambda: self.motor3.doStep( steps_motor3, 1 )
        else:
            h = lambda: self.motor3.doStep( -steps_motor3, 0 )

        if steps_motor4 > 0: 
            i = lambda: self.motor4.doStep( steps_motor4, 1 )
        else:
            i = lambda: self.motor4.doStep( -steps_motor4, 0 )

        p1 = Process(target = f)
        p2 = Process(target = g)
        p3 = Process(target = h)
        p4 = Process(target = i)
        p1.start()
        p2.start()
        p3.start()
        p4.start()

        p1.join()
        p2.join()
        p3.join()
        p4.join()


    def __setMSPins__( self, MS1, MS2, MS3 ):
        GPIO.output( self.pinMS1, MS1 )
        GPIO.output( self.pinMS2, MS2 )
        GPIO.output( self.pinMS3, MS3 )


    def __microstepping__( self, steps ):
        """
        A4988 config pins
        MS1     MS2     MS3     Microstep Resolution
        Low     Low     Low     Full step
        High    Low     Low     Half step
        Low     High    Low     Quarter step
        High    High    Low     Eighth step
        High    High    High    Sixteenth step
        """
        assert( steps in [1,2,4,8,16] )
        #setStepping = {
        #        1: self.__setMSPins__( 0, 0, 0 ),
        #        2: self.__setMSPins__( 1, 0, 0 ), 
        #        4: self.__setMSPins__( 0, 1, 0 ),
        #        8: self.__setMSPins__( 1, 1, 0 ),
        #        16: self.__setMSPins__( 1, 1, 1 )
        #       }[ steps ]
        GPIO.output( self.pinMS1, GPIO.HIGH )
        GPIO.output( self.pinMS2, GPIO.HIGH )
        GPIO.output( self.pinMS3, GPIO.HIGH )
        
        return steps


    def __updateAngleRos__( self, angleName, angle, maxAngle, timePerRev ):
        """
        Continuously updates the angles s.t. ros can turn the coordinate 
        systems in real time.
        """
        #now = time()
        #future = now+angle/maxAngle*timePerRev

        #cutoff = now
        #while now-cutoff < future-cutoff:
        #    print( now-cutoff, future-cutoff, now-cutoff < future-cutoff )
        #    setattr( self, angleName, sp.N(sp.rad(sp.N((now-cutoff)/(future-cutoff)*angle)) ) )
        #    print( "getAttr", getattr( self, angleName ) )
        #    print( "------>", sp.N(sp.rad(sp.N((now-cutoff)/(future-cutoff)*angle)) ))
        #    rospy.sleep(0.1)

        #    now = time()
        setattr( self, angleName, sp.N(sp.rad(angle)))

    def __updateDistanceRos__( self, xName, yName, angle, distance, timePerRev ):
        #now = time()
        #future = now+distance/157*timePerRev
        #print( "update: now, future", now, future )
        #cutoff = now
        #while now-cutoff < future-cutoff:
        #    print( now-cutoff, future-cutoff, now-cutoff < future-cutoff )
        #    setattr( self, xName, sp.N( sp.cos( sp.rad(angle))* (now-cutoff)/(future-cutoff)*distance) )
        #    setattr( self, yName, sp.N( sp.sin( sp.rad(angle))* (now-cutoff)/(future-cutoff)*distance) )

        #    print( "getAttr", getattr( self, xName ) )
        #    print( "getAttr", getattr( self, yName ) )
        #    print( "------>", sp.N( sp.cos( sp.rad(angle))* (now-cutoff)/(future-cutoff)*distance) )
        #    print( "------>", sp.N( sp.sin( sp.rad(angle))* (now-cutoff)/(future-cutoff)*distance) )
        #    rospy.sleep(0.1)

        #    now = time()
        setattr( self, xName, sp.N( sp.cos( sp.rad(angle))*distance) )
        setattr( self, yName, sp.N( sp.sin( sp.rad(angle))*distance) )


    # Cart radius = 215mm, wheel radius = 33.5mm -> 6.41 rev. per wheel per full circle
    # 200 steps per fc * microstepping

    def setAngleCart( self, angle ):
        assert( 0<=angle and angle<=360 )
        self.__motors_start__()
        steps = (angle/360)*14720*1.6
        self.__compute_steps__( 0,0, steps-self.stepsCart )
        self.stepsCart = steps
        self.angleCart = angle
        self.__motors_shutdown__()
        

    
    def moveCart( self, distance ):
        """
        Distance in mm
        wheel radius = 50mm
        """
        assert( distance > 0 )

        self.__motors_start__()
        
        steps = distance/157.075*3200+(distance/2000)*3200
        self.__compute_steps__( steps, 0, 0 )

        ##steps = (angle/360)*200*6.42*2.15*self.microstepping
        #angle = steps/(200*6.42*2.15*self.microstepping)*360
        #(angle/360)*200*6.42*2.15*self.microstepping
        #
        dx = sp.N( sp.cos(self.angleCart)*distance )
        dy = sp.N( sp.sin(self.angleCart)*distance )
        
        print( "x, y, dx, dy", self.x, self.y, dx, dy )

        self.__updateDistanceRos__( "x", "y", self.angleCart, distance, 6.4 )
        

        self.__motors_shutdown__()


    def getConfigurationMatrixCart( self ):
        angle = sp.rad( self.angleCart  )
        M = sp.Matrix( [ [sp.cos( angle ), -sp.sin( angle ), 0, sp.N(self.x)], [sp.sin(angle), sp.cos(angle), 0, sp.N(self.y)], [0, 0, 1, self.offset], [0, 0, 0, 1] ] )         
        print( "caa cart>>", M) 
        return M 



if __name__ == "__main__":
    c = cart()
    c.__motors_start__()
    print( c.getConfigurationMatrixCart() )
    c.setAngleCart( 45 )
    print( c.getConfigurationMatrixCart() )
    c.setAngleCart( 90 )
    print( c.getConfigurationMatrixCart() )
    c.setAngleCart( 180 )
    print( c.getConfigurationMatrixCart() )
    c.setAngleCart( 0 )
    print( c.getConfigurationMatrixCart() )

    
    c.__motors_shutdown__()