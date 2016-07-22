# non-working model 07/21
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

        self.outsideTemperature = 296

    # general building specifications
        self.surfaceArea = 0 # in meters squared
        self.volume = self.surfaceArea * 1 # should be multiplied by an average or a building specific varible

        # hard coded to room temperature for now
        self.insideTemperature = 296

        # the rate that the building looses thermal energy in Kw / hr, in relation to its volume in meters^3
        self.insulationCe = 0

        '''generation calculation varibles'''
        #constant for earth
        self.OLI = 23.44 * (math.pi / 180)

        #constant latitude of chadwick
        self.LAT = 33.77984 * (math.pi / 180.0)

        #varibles
        self.day = 152
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

        # the amount of energy in Kilojoules, the air conditioner can remove from the air per hour
        # 1.057 Kilojoules per Btu / h
        self.thermalCapacity = 12000 * 1.057

        # A / C power use when on in Watts
        self.acPowerUse = 5000

        self.targetTemperature = 23 + 273

        self.humidity = 0.6

        # air density, Kilograms / meter^3, baseline
        self.P = 1

        # aptmospheric pressure in kpa
        self.ATM = 101.325

        # specific heat capacities KJ / Kg
        self.airCp = 1.005
        self.waterCp = 1.8723


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

    # initializers for temperature calculation
        self.dMax = (5 / 9) * (6.5 * sin(.0172 * self.day - 2.25) + 72.8 - 32) + 273
        self.dMin = (5 / 9) * (6.5 * sin(.0172 * self.day - 2.25) + 56.5 - 32) + 273
        self.ran = self.dMax - self.dMin
        self.ave = (self.dMax + self.dMin) / 2

        # print "Ave: " + str(self.ave)
        # print "Ran: " + str(self.ran)

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

        #'''
        print "EoT: " + str(self.EoT)
        print "SELA: " + str(self.SELA)
        print "SAXA: " + str(self.SAZA)
        print "s_module coeff: " + str(self.module_coeff)
        print "solar Irradiance 1: " + str(self.solarIrradiance)
        #'''
        # monitor the change of solarIrradiance
        self.solarIrradiance *= self.module_coeff

        #print str(cos(self.AZA - self.SAZA))

        #'''
        print "solar Irradiance 2: " + str(self.solarIrradiance)
        print "Area: " + str(self.panelArea)
        print "Panel Eff: " + str(self.panelEff)
        #'''

        self.gen = self.solarIrradiance * self.panelArea * self.panelEff
        print "Gen: " + str(self.gen)

        return self.gen

# consumption
    def consumption(self, msg):

        self.cons = 0

        self.dMax = (5 / 9) * (6.5 * sin(.0172 * self.day - 2.25) + 72.8 - 32) + 273
        self.dMin = (5 / 9) * (6.5 * sin(.0172 * self.day - 2.25) + 56.5 - 32) + 273
        self.ran = self.dMax - self.dMin
        self.ave = (self.dMax + self.dMin) / 2

        # temperature calculation
        tempEq1 = 2.0 * pow(sin(math.pi * (self.LT - 9) / 12), 3)
        tempEq2 = 7.0 * pow(sin(math.pi * (self.LT - 9) / 19), 2)
        tempEq3 = 4.5 * pow(sin(math.pi * (self.LT - 19) / 40), 19)

        self.outsideTemperature = (self.ran / 2) * (tempEq1 + tempEq2 + tempEq3) + self.ave

        # print "Outside: " + str(self.outsideTemperature)
        # print "Inside: " + str(self.insideTemperature)

        # Air Conditioning
        if self.insideTemperature > self.targetTemperature:
            # air condititioning consumption
            self.cons += self.acPowerUse * 60
            # the amount of thermal energy vented from the building by the A / C unit, in kilojoules per minute
            self.thermalVent = self.thermalCapacity / 60

            # full temperature change calculation
            self.waterVaporCe = 0.03 * self.humidity

            self.volCeT = ((self.waterVaporCe * 0.4615) + (1 - self.waterVaporCe) * 0.287) * self.insideTemperature

            self.cAve = self.waterVaporCe * self.waterCp + (1 - self.waterVaporCe) * self.airCp
            # density in Kg / meter^3
            self.P = (self.ATM / self.volCeT)

            self.deltaT = (self.thermalCapacity / 60) / ((self.P * self.volume) * (self.cAve))

            self.insideTemperature -= self.deltaT

            print "Changed: " + str(self.insideTemperature)

        return self.cons



if __name__ == "__main__":
    b = Building()
    powerGen = 0
    powerCon = 0
    for min in range(b.rise, b.sets):
        print str(min)
        b.LT = float(min) / 60.0
        #print str(b.generation(b) / 60)
        powerGen += b.generation(b) / 60

        powerCon += b.consumption(b) / 60
        print
    print powerGen
    print powerCon
    #print str(power)
