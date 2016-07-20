'''
from magi.util.agent import DispatchAgent, agentmethod
from magi.util.processAgent import initializeProcessAgent
'''
# commented out code: don't know if necessary/not yet implemented
import logging
from math import sin, cos, asin, acos, tan, atan
import math
# import scipy.io
import sys
# import time

'''
from magi.messaging.magimessage import MAGIMessage
from magi.util import helpers, database
from magi.util.agent import NonBlockingDispatchAgent, agentmethod
from magi.util.processAgent import initializeProcessAgent
import yaml
'''

class Building():  # difference between DispatchAgent and NonBlockingDispatchAgent?
    def __init__(self):
        object.__init__(self)
        
        #constant for earth
        self.oli = 23.44 * (math.pi / 180)

        #data recieved from array config
        self.panelEff = 0.17
        self.panelArea = 20
        self.ELA = 25.0 * (math.pi / 180.0)
        self.AZA = math.pi

        #data recieved by the simulation configuration
        self.day = 171
        #iterative
        self.LT = 0

        #calculations done for each day of simulation
        self.B = (math.pi / 180.0) * (360.0 / 365.0) * (self.day - 10)
        self.EoT = 9.87 * sin(2.0 * self.B) - 7.53 * cos(self.B) - 1.5 * sin(self.B)
        self.delta = (math.pi / 180.0) * asin(sin(self.oli) * sin(self.B))

        #constant latitude of Chadwick
        self.LAT = 33.77984 * (math.pi / 180.0)



    # electricity generation
    def generation(self, msg):
        
        #calculations done for each iteration 
        self.LST = self.LT + (4.0 * (-13.361) + self.EoT) / 60.0
        self.HRA = (math.pi / 180.0) * (15.0 * (self.LST - 12))
        
        self.SELA = asin(sin(self.delta) * sin(self.LAT) + cos(self.delta) * cos(self.LAT) * cos(self.HRA))
        self.SAZA = acos((sin(self.delta) * cos(self.LAT) - cos(self.delta) * sin(self.LAT) * cos(self.HRA)) / cos(self.SELA))  #cos(self.SELA)
        self.declination = (1 - self.SELA)
        
        #done only if the array is a tracking array 
        '''building needs to parce for an argument called "tracking" or something of the kind'''
        if self.tracking:
            self.ELA = self.SELA
            self.AZA = self.SAZA
        
        #implement solar irradiance equation, 
        '''in self.gen 1.5 refers to the general maximum power of the solar irradiance cast over one square meter of earth'''

        self.solarIrradiance = pow(1.353, pow(pow(0.7, (1.0 / 1e-4) + cos(1.0 / self.declination)), 0.678))
        self.solarIrradiance *= (cos(self.SELA) * sin(self.ELA) * cos(self.AZA - self.SAZA) + sin(self.SELA) * cos(self.ELA))
        self.gen = self.solarIrradiance * (self.panelEff * 1.5) * self.panelArea
        
        #debugging loggers        
        '''
        print(self.HRA)
        print(self.SELA)
        print(self.SAZA)
        print(self.declination)
        print(self.solarIrradiance)
        '''
        return self.gen

    # electricity consumption
    def consumption(self, msg):
        #this operation is to satisfy the consumption functions need of at least one directive, because we have no implemented models for consumption yet
        self.c = 1


if __name__ == "__main__":
    room = Building()
    power = 0

    #sunrise and sunset calculator, will need a stream related implementation
    rise = -tan(room.LAT) * tan(room.delta)
    set = tan(room.LAT) * tan(room.delta)

    rise = (math.pi / 2) + rise
    set = (3 * math.pi / 2) + set

    #converts to minutes / 1440 (per day)
    rise /= 2 * math.pi
    set /= 2 * math.pi

    rise *= 1440
    set *= 1440

    rise = int(rise)
    set = int(set)

    #print(str(rise))
    #print(str(set))

    rise = int(rise)
    set = int(set)

    for i in range(rise + 1, set - 1):
        room.LT = i / 60.0
        #print(room.LT)
        power += room.generation(room) / 60.0
        #print str(i / 60.0)
    #prints the Power generation for the day in Kilowatt*Hours
    print(str(power))
    print("")




