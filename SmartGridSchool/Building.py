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
    #parses varibles from the config file, declared once
    def __init__(self):
        object.__init__(self)

    # general physics
        # base-lined at room temperature
        self.minTemp = 20
        self.maxTemp = 30

        self.outsideTemperature = 23

    # general building specifications
        self.surfaceArea = 0 # in meters squared
        self.volume = surfaceArea * 1 # should be multiplied by an average or a building specific varible

        # hard coded to room temperature for now
        self.insideTemperature = 23

        # the rate that the building looses thermal energy in Kw / hr, in relation to its volume in meters^3
        self.insulationCe = 0

        '''generation calculation varibles'''
        #constant for earth
        self.OLI = 23.44 * (math.pi / 180)

        #constant latitude of chadwick
        self.LAT = 33.77984 * (math.pi / 180.0)

        #varibles
        self.day = 0
        self.LT = 0
        self.panelEff = 0.17
        self.panelArea = 20

        #hard coded
        self.ELA = 36.0 * (math.pi / 180.0)
        self.AZA = math.pi
        self.tracking = False

        #calculated daily
        self.W = (360.0 / 365.24)
        self.A = self.W * (self.day - 10)
        self.B = self.A * 1.914 * sin(self.W * (self.day - 2))
        self.C = self.A - atan(tan(self.B) / cos(self.OLI)) / 180
        self.EoT = 720 * self.C - round(self.C, 0)


        #self.EoT = 9.87 * sin(2 * self.B) - 7.53 * cos(self.B) - 1.5 * sin(self.B)
        self.delta = (math.pi / 180.0) * asin(sin(self.OLI) * sin(self.B))

        #preliminary rise/set calculation
        self.rise = -tan(self.LAT) * tan(self.delta)
        self.sets = -self.rise

        self.rise = int(1440 * ((math.pi / 2.0) + self.rise) / (2 * math.pi))
        self.sets = int(1440 * ((3.0 * math.pi / 2.0) + self.sets) / (2 * math.pi))

        '''consumption initialization varibles'''
        '''A / C'''

        # the amount of energy in Kw, the air conditioner can remove from the air per hour
        self.thermalCapacity = 60000

        # A / C power use when on in Watts
        self.acPowerUse = 5000

        self.targetTemperature = 23

        '''Lights'''
        # arbitrary average values
        self.numLights = 50
        self.averageWattage = 60

        '''Appliances'''
        # insert a formula or space related varible
        '''think about how to pass appliances'''
        self.applianceKey = [[],[]]

        '''Outlets'''
        # number of outlets and range of likely usage times
        self.numOutlets = 10
        self.oTimeIndex = [] # probably uneccessary


    # electricity generation
    def generation(self, msg):

        #rise / set calculations
        self.rise = -tan(self.LAT) * tan(self.delta)
        self.sets = -self.rise

        self.rise = int(1440 * ((math.pi / 2.0) + self.rise) / (2 * math.pi))
        self.sets = int(1440 * ((3.0 * math.pi / 2.0) + self.sets) / (2 * math.pi))

        #local time, hour angle
        self.LST = self.LT + (4.0 * (-13.361) + self.EoT)
        self.HRA = (math.pi / 180.0) * (15.0 * (self.LST - 12))

        '''
        print str(self.EoT)
        print str(self.LT)
        print str(self.LST)
        print str(self.HRA)
        '''
        #solar elevation angle and azimuth angle
        self.SELA = asin(sin(self.delta) * sin(self.LAT) + cos(self.delta) * cos(self.LAT) * cos(self.HRA))
        self.SAZA = acos((sin(self.delta) * cos(self.LAT) - cos(self.delta) * sin(self.LAT) * cos(self.HRA)) / cos(self.SELA))

        #declination
        self.declination = (90 - (180 / math.pi) * self.SELA) * (math.pi / 180)

        # done only if the array is a tracking array
        if self.tracking:
            self.ELA = self.SELA
            self.AZA = self.SAZA

        self.am = 1 / cos(self.declination)

        if self.am > 1.0:
            self.am = 1
        elif self.am < -1.0:
            self.am = -1

        # implement solar irradiance equation,
        self.solarIrradiance = 1.353 * pow(pow(0.7, self.am), 0.678)


        self.SELA = (90 + (180 / math.pi) * self.SELA) * (math.pi / 180)
        #print str(self.solarIrradiance)

        self.module_coeff = cos(self.SELA) * sin(self.ELA) * cos(self.AZA - self.SAZA) + sin(self.SELA) * cos(self.ELA)
        if self.module_coeff < 0:
            self.module_coeff = 0

        print "EoT: " + str(self.EoT)
        print "SELA: " + str(self.SELA)
        print "SAXA: " + str(self.SAZA)
        print "s_module coeff: " + str(self.module_coeff)
        print "solar Irradiance 1: " + str(self.solarIrradiance)

        # monitor the change of solarIrradiance
        self.solarIrradiance *= (self.module_coeff)

        #print str(cos(self.AZA - self.SAZA))

        print "solar Irradiance 2: " + str(self.solarIrradiance)
        print "Area: " + str(self.panelArea)
        print "Panel Eff: " + str(self.panelEff)

        self.gen = self.solarIrradiance * self.panelArea * self.panelEff
        print "Gen: " + str(self.gen)

        return self.gen

# consumption
    def consumption(self, msg):
        self.consumption = 0

        # temperature calculation
        self.dMax = (5 / 9) * (6.5 * sin(.0172 - 2.25) + 72.8 - 32)
        self.dMin = (5 / 9) * (6.5 * sin(.0172 - 2.25) + 56.5 - 32)
        self.ran = dMax - dMin
        self.ave = (dMax + dMin) / 2



        tempEq1 = 2.0 * pow(sin(math.pi * (self.LT - 9) / 12), 3)
        tempEq2 = 7.0 * pow(sin(math.pi * (self.LT - 9) / 19), 2)
        tempEq3 = 4.5 * pow(sin(math.pi * (self.LT - 19) / 40), 19)

        self.outsideTemperature = (ran / 2) * (tempEq1 + tempEq2 + tempEq3) + ave

        # Air Conditioning
        if self.insideTemperature > self.targetTemperature:
            consumption += self.acPowerUse * 60
            # do full temperature change calculation






if __name__ == "__main__":
    b = Building()
    power = 0
    for min in range(b.rise, b.sets):
        print str(min)
        b.LT = float(min) / 60.0
        #print str(b.generation(b) / 60)
        power += b.generation(b) / 60
        print
    print power
    #print str(power)



