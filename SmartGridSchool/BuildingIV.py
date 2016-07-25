# function period is erratic, 7.25.16
'''
from magi.util.agent import DispatchAgent, agentmethod
from magi.util.processAgent import initializeProcessAgent
'''
# commented out code: don't know if necessary/not yet implemented
import logging
from math import sin, cos, asin, acos, tan, atan, log
import math
from random import randint
#import random
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
    def __init__(self, day):
        object.__init__(self)

    #universal time varibles, must be recieved before continuing
        self.day = day
        self.LT = 0

    # general physics
        #building specific, the amount of heat lost per minute relative
        #to the difference in inside and outside temperatures
        self.thermalLeakCe = 0.007
        # dew point in % as a float 0-1, by mass; base-lined for room temp
        self.dewPt = 0.025
        # % humidity as a float 0-1
        self.humidity = 0.6

        # atmospheric pressure in kpa
        self.ATM = 101.325

        # gas coefficents
        self.airGC = 0.287
        self.waterGC = 0.4615

        # specific heat capacities KJ / Kg
        self.airCp = 1.005
        self.waterCp = 1.8723

        # air density, Kilograms / meter^3, baseline
        self.P = 1

    # general building specifications
        self.surfaceArea = 2210 # in meters squared
        self.volume = self.surfaceArea * 2.3 # should be multiplied by an average or a building specific varible



        # the rate that the building looses thermal energy in Kw / hr, in relation to its volume in meters^3
        self.insulationCe = 0

    # generation varibles
        #constant for earth
        self.OLI = 23.44 * (math.pi / 180)

        #constant latitude of chadwick
        self.LAT = 33.77984 * (math.pi / 180.0)

        #varibles for solar array        Approximating laverty
        self.panelEff = 0.21
        #approximating 5 square meter moving arrays, 5 + 2 = 7; 2 meters of clearance
        self.panelArea = self.surfaceArea        # 25 * (self.surfaceArea / pow(7, 2))

        #hard coded
        self.ELA = 33.77 * (math.pi / 180.0)
        self.AZA = math.pi
        self.tracking = False

        #calculated daily

        self.W = (360.0 / 365.24)
        self.A = self.W * (self.day + 10)
        self.B = self.A * 1.914 * sin(self.W * (self.day - 2))
        self.C = self.A - atan(tan(self.B) / cos(self.OLI)) / 180
        self.EoT = 720 * (self.C - round(self.C, 0))


        #self.B = (360.0 / 365.0) * (self.day - 10)
        #self.EoT = 9.87 * sin(2 * self.B) - 7.53 * cos(self.B) - 1.5 * sin(self.B)

        self.delta = (math.pi / 180.0) * -asin(sin(self.OLI) * cos(self.B))

        #preliminary rise/set calculation
        self.rise = -tan(self.LAT) * tan(self.delta)
        self.sets = -self.rise

        self.rise = int(1440 * ((math.pi / 2.0) + self.rise) / (2 * math.pi))
        self.sets = int(1440 * ((3.0 * math.pi / 2.0) + self.sets) / (2 * math.pi))

        print "Rise: " + str(self.rise)
        print "Set: " + str(self.sets)

    #'''consumption initialization varibles'''

    # temperature
        # max and min temperatures for the day
        self.maxT = (5.0 / 9.0) * (6.5 * sin(.0172 * self.day - 2.25) + 72.8 - 32) + 273
        self.minT = (5.0 / 9.0) * (6.5 * sin(.0172 * self.day - 2.25) + 56.5 - 32) + 273

        #print "Max temperature: " + str(self.maxT)
        #print "Min temperature: " + str(self.minT)

        self.ran = self.maxT - self.minT
        self.ave = (self.maxT + self.minT) / 2

        # hard coded to room temperature for now
        self.insideTemperature = 23
        self.outsideTemperature = 23

    #   '''A / C'''
        # target temperature in degrees kelvin
        self.targetTemperature = 21

        # the amount of energy in Kw, the air conditioner can remove from the air per hour
        # 1.057 Kilojoules per Btu / h
        self.thermalCapacity = (12000 * 1.057) * 7

        # A / C power use when on in Watts
        self.acPowerUse = 5000 * 7

    #   '''Lights'''
        # arbitrary average values
        self.numLights = 200
        self.averageWattage = 60
        self.baselineCe = 0.25  # 25 % of lights are usually on
        self.lightsActive = 0

    #   '''Appliances'''
        # insert a formula or space related varible
        #self.applianceKey = [[],[]]
        # the amount of energy used by appliances; applied uniformly
        # number of outlets and range of likely usage times
        self.numOutlets = 10
        self.activeOutlets = 0
        self.afterNoonCe = 0.3
        self.applianceDraw = 1200

    #   '''Outlets'''
        self.outletDraw = 75 # a conservative, approximate average wattage for laptop adapters
    # might add a varible that denotes a minimum percentage of outlets used

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
        print "delta: " + str(self.delta)
        print "time in day: " + str(self.sets - self.rise)
        print str(self.EoT)
        print str(self.LT)
        print str(self.LST)
        print str(self.HRA)
        '''

        #solar elevation angle and azimuth angle
        self.SELA = asin(sin(self.delta) * sin(self.LAT) + cos(self.delta) * cos(self.LAT) * cos(self.HRA))
        self.SAZA = acos((sin(self.delta) * cos(self.LAT) - cos(self.delta) * sin(self.LAT) * cos(self.HRA)) / cos(self.SELA))

        #declination
        self.declination = abs(self.SELA)# because SELA is negative in the morning and positive in the afternoon with a maximum of 90 declination is its absolute value (90 + (180 / math.pi) * self.SELA) * (math.pi / 180)

        #airmass calculation
        self.am = 1 / (cos(self.declination) + 0.50572 * pow(96.07995 - self.declination, -1.6364))

        '''
        #print "1 / cos(declination): " + str(self.am)
        #print "Airmass: " + str(self.am)
        '''
        # a more accurate diffuse irradience correction
        self.diffuseIrradience = 0.20 * pow(0.7, pow(abs(self.am), 0.678))    # need to accound for increase of diffusion through clouds when clouds are added
        #print "Diffuse Irradience: " + str(self.diffuseIrradience)


        # 1.353 is the solar intensity outside the earth's aptmosphere, 1.1 assumes that the diffuse component of radiation to the panel is about 10 % of the direct component
        self.solarIrradience = 1.353 * (1 + self.diffuseIrradience) * pow(0.7, pow(abs(self.am), 0.678))

        # print "Solar Irradience: " + str(self.solarIrradience)

        #this offset disrupts the module_coeff equation
        #self.SELA = (90 + (180 / math.pi) * self.SELA) * (math.pi / 180)
        #print str(self.solarIrradience)

        # done only if the array is a tracking array
        if self.tracking:
            self.module_coeff = 1
        else:
            self.module_coeff = cos(self.SELA) * sin(self.ELA) * cos(self.AZA - self.SAZA) + sin(self.SELA) * cos(self.ELA)
            #self.module_coeff *= -1

        #print "s_module coeff: " + str(self.module_coeff)

        if self.module_coeff < 0:
            self.module_coeff = 0
        '''
        #print "EoT: " + str(self.EoT)
        #print "SELA: " + str(self.SELA)
        #print "SAZA: " + str(self.SAZA)
        print "ELA: " + str(self.ELA)
        #print "AZA: " + str(self.AZA)
        print "s_module coeff equation: " + str(cos(self.SELA)) + " * " + str(sin(self.ELA)) + " * " + str(cos(self.AZA - self.SAZA)) + " + " +\
                                            str(sin(self.SELA)) + " * " + str(cos(self.ELA))
        print "s_module coeff: " + str(self.module_coeff)
        print "solar Irradiance 1: " + str(self.solarIrradience)
        '''

        # monitor the change of solarIrradience
        self.solarIrradience *= self.module_coeff


        '''
        print "solar Irradiance 2: " + str(self.solarIrradience)
        print "Area: " + str(self.panelArea)
        print "Panel Eff: " + str(self.panelEff)

        if self.solarIrradience > 0:
            self.solarIrradienceTotal += self.solarIrradience
        '''

        self.gen = self.solarIrradience * self.panelArea * self.panelEff
        #print "Gen: " + str(self.gen)

        return self.gen

# consumption
    def consumption(self, msg):
        self.cons = 0

        # temperature calculation
        tempEq1 = 2.0 * pow(sin(math.pi * (self.LT - 9) / 12), 3)
        tempEq2 = 7.0 * pow(sin(math.pi * (self.LT - 9) / 19), 2)
        tempEq3 = 4.5 * pow(sin(math.pi * (self.LT - 19) / 40), 19)

        temp = (1.0 / 7.8789) * (tempEq1 + tempEq2 + tempEq3)


        '''
        print "tempEq1: " + str(tempEq1)
        print "tempEq2: " + str(tempEq2)
        print "tempEq3: " + str(tempEq3)

        print "Max temperature: " + str(self.maxT)
        print "Min temperature: " + str(self.minT)

        print "Range: " + str(self.ran)
        print "Average: " + str(self.ave)
        '''

        self.outsideTemperature = (self.ran / 2) * temp + self.ave

        #print "Time: " + str(self.LT)
        #print "Temperature: " + str(self.outsideTemperature)

        # thermal leak
        self.thermalLeak = self.thermalLeakCe * (self.outsideTemperature - self.insideTemperature)
        self.insideTemperature += self.thermalLeak

        # dew point calculation
        c = 243.5
        b = 17.67

        '''
        print "humidity: " + str(self.humidity)
        print "log(self.humidity, math.e): " + str(log(self.humidity, math.e))
        print "(b * self.insideTemperature) / (c + self.insideTemperature): " + str((b * self.insideTemperature) / (c + self.insideTemperature))
        '''
        gamma = log(self.humidity, math.e) + (b * self.insideTemperature) / (c + self.insideTemperature)

        #print "Gamma: " + str(gamma)
        #self.dewPt = (c * gamma) / (b - gamma)

        #print "Dew Point: " + str(self.dewPt)

        # Air Conditioning
        #print str(self.insideTemperature - self.targetTemperature)
        #print str(self.LT)
        if (self.LT >= 7.0 and self.LT <= 19.0):
            if self.insideTemperature > self.targetTemperature:

                # the amount of thermal energy vented form the building by the A / C unit, in kilojoules per minute
                self.thermalVent = self.thermalCapacity / 60

                # temperature change calculation
                self.waterVaporCe = self.dewPt * self.humidity

                # gas volume coefficents and temperature
                self.volCe_T = (self.waterVaporCe * self.waterGC + (1 - self.waterVaporCe) * self.airGC) * (self.insideTemperature + 273)

                # density in Kg / m^3
                self.P = self.ATM / self.volCe_T

                # average specific heat of the air solution
                self.cAve = self.waterVaporCe * self.waterCp + (1 - self.waterVaporCe) * self.airCp

                # temperature change
                self.deltaT = (self.thermalCapacity / 60) / (self.P * self.volume * self.cAve)


                '''
                print "(A/C change)"
                print "Thermal leak: " + str(self.thermalLeak)
                print "Temperature change: " + str(self.insideTemperature - self.deltaT)
                print "Inside: " + str(self.insideTemperature)
                print "Target: " + str(self.targetTemperature)
                '''

                # if deltaT is greater than the difference between the temperature and target
                # change inside temperature to target and reduce energy consumption as necessary
                if self.insideTemperature - self.deltaT < self.targetTemperature:
                    self.cons += self.acPowerUse * ((self.insideTemperature - self.targetTemperature) / self.deltaT)
                    self.insideTemperature = self.targetTemperature
                    #print "(Partial Temperature Change)"
                else:
                    #print "Temperature: " + str(self.insideTemperature)
                    self.insideTemperature -= self.deltaT
                    self.cons += self.acPowerUse

                #print "Changed Temperature: " + str(self.insideTemperature)'




        if self.LT > 5.0 and self.LT < 21.0:
            minutes = self.LT * 60

            # Outlet use
            if minutes < 475:
                self.outletsActive = int(1 / randint(8, 10) * self.numOutlets)
            elif minutes < 795:
                if (minutes - 475) % 45 == 0:
                    self.outletsActive = int(1 / randint(1, 10) * self.numOutlets)
            elif minutes < 945:
                if (minutes - 795) % 5 == 0:
                    self.outletsActive = int(1 / randint(int(10 * (1 - self.afterNoonCe)), 10) * self.numOutlets)
            elif minutes < 1020:
                if (minutes - 795) % 15 == 0:
                    self.outletsActive = int(1 / randint(int(10 * (1 - 2 * self.afterNoonCe)), 10) * self.numOutlets)
            else:
                if minutes % 30 == 0 and randint(0, 10) <= 10 * self.afterNoonCe:
                    self.outletsActive = int(1 / randint(int(10 * (1 - 3 * self.afterNoonCe)), 10) * self.numOutlets)
                else:
                    self.outletsActive = 0

            self.cons += self.outletsActive * self.outletDraw

            # light use
            base = int(10 - 10 * self.baselineCe)

            if minutes < 475:
                if minutes % 10 == 0:
                    self.lightsActive = int(1 / randint(int(base - 10 * self.baselineCe), base) * self.numLights)
            elif minutes < 795:
                if (minutes - 475) % 45 == 0:
                    self.lightsActive = int(1 / randint(1, int(10 - 10 * 2 * self.baselineCe)) * self.numLights)
            elif minutes < 1020:
                if (minutes - 795) % 15 == 0:
                    self.lightsActive = int(1 / randint(1, int(10 - 10 * 3 * self.baselineCe)) * self.numLights)
            else:
                if (minutes - 1020) % 20 == 0 and randint(0, 10) <= 10 * self.afterNoonCe:
                    self.lightsActive = int(1 / randint(int(10 * (1 - 3 * self.afterNoonCe)), base) * self.numLights)
                else:
                    self.lightsActive = self.baselineCe * self.numLights

            self.cons += self.lightsActive * self.averageWattage

        else:
            self.outletsActive = 0
            self.lightsActive = 0


        # appliances
        self.cons += self.applianceDraw

        #print "Consumption: " + str(self.cons)

        return self.cons


if __name__ == "__main__":
    #b = Building()
    power = 0
    draw = 0


    for day in range(0, 364):
        power = 0
        draw = 0
        print str(day)
        b = Building(day)
        b.day = day
        b.solarIrradienceTotal = 0

        for min in range(0, 1440):

            #print str(min)
            b.LT = float(min) / 60.0



            # get joules, convert to average watts, convert to kilowatts
            draw +=  (b.consumption(b) / 60.0) / 1000.0
            #print str(b.generation(b) / 60)

            if min >= b.rise and min <= b.sets:
                power += b.generation(b) / 60
            #else:
                #print "No power generated"

            #print
        #print "Total Irradience: " + str(b.solarIrradienceTotal)

        print "Power: " + str(power)
        print "Draw: " + str(draw)
        print
        #print str(power)

