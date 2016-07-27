import logging
from math import sin, cos, asin, acos, tan, atan, log
from random import randint, random
import math
import sys

def sind(x):
    return sin((math.pi / 180) * x)

def cosd(x):
    return cos((math.pi / 180) * x)

def asind(x):
    return asin((math.pi / 180) * x)

def acosd(x):
    return acos((math.pi / 180) * x)

def tand(x):
    return tan((math.pi / 180) * x)

def atand(x):
    return atan((math.pi / 180) * x)




class Building():

    def __init__(self, day):
        object.__init__(self)

        # constants and parsed values
        self.day = day
        self.LT = 0

        self.OLI = 23.44
        self.LAT = 33.77984
        self.surfaceArea = 2210
        self.volume = self.surfaceArea * 2.5

        self.panelEff = 0.21
        self.panelArea = self.surfaceArea

        self.ELA = self.LAT
        self.AZA = 180
        self.tracking = False

        self.preDawn = True
        self.dusk = False

        # calculated daily
        self.B = (360.0 / 365.0) * (self.day - 81)
        self.EoT = 9.87 * sind(2 * self.B) - 7.53 * cosd(self.B) - 1.5 * sind(self.B)
        self.delta = self.OLI * sind(self.B)

        # consumption constants and parsed values
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

        self.timeOn = [7, 19, 60, 270]

        self.insideTemperature = 23
        self.outsideTemperature = 23

        # A/C calculation
        # max and min temperatures for the day
        self.maxT = (5.0 / 9.0) * (6.5 * sin(.0172 * self.day - 2.25) + 72.8 - 32)
        self.minT = (5.0 / 9.0) * (6.5 * sin(.0172 * self.day - 2.25) + 56.5 - 32)

        self.ran = self.maxT - self.minT
        self.ave = (self.maxT + self.minT) / 2

        # target temperature in degrees celsius
        self.targetTemperature = 21

        # the amount of energy in Kw, the air conditioner can remove from the air per hour
        # 1.057 Kilojoules per Btu / h
        self.thermalCapacity = (12000 * 1.057) * 7

        # A / C power use when on in Watts
        self.acPowerUse = 5000 * 7

        # Lights calculation
        self.lightWattage = 52020
        self.activeWattage = 0  # % active wattage 0.0 - 1.0
        self.baseLineCe = 0.15

        # Appliances
        self.applianceDraw = 1200

        # Outlets
        self.numOutlets = 100
        self.activeOutlets = 0
        # a conservative baseline estimate
        self.outletDraw = 75



    def generation(self, msg):
        self.LST = (self.LT + (4.0 * (-13.361) + self.EoT)) / 60
        self.HRA = 15.0 * (self.LST - 12)

        self.SELA = asin(sind(self.delta) * sind(self.LAT) + cosd(self.delta) * cosd(self.LAT) * cosd(self.HRA))
        self.SAZA = acos(sind(self.delta) * cosd(self.LAT) - cosd(self.delta) * sind(self.LAT) * cosd(self.HRA)) / cos(self.SELA)

        if self.preDawn and self.SELA > 0: self.preDawn = False
        if not self.preDawn and self.SELA < 0: self.dusk = True

        if not self.preDawn and not self.dusk:
            #self.declination = 90 - (self.SELA) * (180 / math.pi)
            self.declination = 90 - self.SELA * (180 / math.pi)
            self.am = 1 / (cosd(self.declination) + 0.50572 * pow(96.07995 - self.declination, -1.6364))

            self.diffuseIrradience = 0.2 * pow(0.7, pow(1 / self.am, 0.678))
            self.solarIrradience = 1.353 * (1 + self.diffuseIrradience) * pow(0.7, pow(self.am, 0.678))

            self.moduleCe = cos(self.SELA) * sind(self.ELA) * cosd(self.AZA - self.SAZA * (180 / math.pi)) + sin(self.SELA) * cosd(self.ELA)

            if self.moduleCe < 0:
                self.moduleCe = 0

            self.eTotal = self.solarIrradience * self.moduleCe

            self.gen = self.eTotal * self.panelArea * self.panelEff

        else:
            self.gen = 0

        return self.gen

    def consumption(self, msg):

        self.cons = 0
        # temperature calculation
        tempEq1 = 2.0 * pow(sin(math.pi * (self.LT - 9) / 12), 3)
        tempEq2 = 7.0 * pow(sin(math.pi * (self.LT - 9) / 19), 2)
        tempEq3 = 4.5 * pow(sin(math.pi * (self.LT - 19) / 40), 19)

        temp = (1.0 / 7.8789) * (tempEq1 + tempEq2 + tempEq3)

        self.outsideTemperature = (self.ran / 2) * temp + self.ave

        # thermal leak
        self.thermalLeak = self.thermalLeakCe * (self.outsideTemperature - self.insideTemperature)
        self.insideTemperature += self.thermalLeak

        # if air conditioning meets input time parameters
        if self.LT / 60 > self.timeOn[0] and self.LT / 60 < self.timeOn[1] and self.day >= self.timeOn[2] and self.day <= self.timeOn[3]:
            if self.insideTemperature > self.targetTemperature:

                # the amount of thermal energy vented by the A/C, in kilojoules per minute
                self.thermalVent = self.thermalCapacity / 60

                # % water vapor by mass
                self.waterVaporCe = self.dewPt * self.humidity

                # gas volume calculation * temperature in kelvin
                self.volCe_t = (self.waterVaporCe * self.waterGC + (1 - self.waterVaporCe) * self.airGC) * (self.insideTemperature + 273)

                # density in Kg / m^3
                self.P = self.ATM / self.volCe_t

                # average specific heat of the air solution
                self.cAve = self.waterVaporCe * self.waterCp + (1 - self.waterVaporCe) * self.airCp

                # temperature change
                self.deltaT = (self.thermalCapacity / 60) / (self.P * self.volume * self.cAve)

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

                    #print "Changed Temperature: " + str(self.insideTemperature)

        print "Local Time: " + str(self.LT)
        if self.LT > (5.0 / 24.0) * 1440.0 and self.LT < (21.0 / 24.0) * 1440.0:
            # Outlet use
            if self.LT < 475:
                self.activeOutlets = (1.0 / randint(8, 10) * self.numOutlets)
            elif self.LT < 795:
                if (self.LT - 475) % 45 == 0:
                    self.activeOutlets = (1.0 / randint(1, 10) * self.numOutlets)
            elif self.LT < 945:
                if (self.LT - 795) % 5 == 0:
                    self.activeOutlets = (1.0 / randint(int(10 * (1 - 0.32)), 10) * self.numOutlets)
            elif self.LT < 1020:
                if (self.LT - 795) % 15 == 0:
                    self.activeOutlets = (1.0 / randint(int(10 * (1 - 2 * 0.32)), 10) * self.numOutlets)
            else:
                if self.LT % 5 == 0 and randint(0, 10) <= 10 * 0.24:
                    self.activeOutlets = (1 / randint(int(10 * (1 - 2.5 * 0.32)), 10) * self.numOutlets)
                else:
                    self.activeOutlets = 0
            self.activeOutlets = round(self.activeOutlets, 0)
            print "Active Outlets: " + str(self.activeOutlets)
            print "Outlet Consumption: " + str(self.activeOutlets * self.outletDraw)
            self.cons += self.activeOutlets * self.outletDraw

            # light use
            base = round((10 - 10 * self.baseLineCe) * 10, 0)
            print "Base: " + str(base)
            #self.baseLineCe = round(self.baseLineCe * 100, 0)

            if self.LT < 475:
                if self.LT % 10 == 0:
                    self.activeWattage = 1.0 / (0.1 * randint(round(base / 2, 0), base))
            elif self.LT < 795:
                if (self.LT - 475) % 45 == 0:
                    self.activeWattage = 1.0 / (0.1 * randint(1, base - (100 - base)))
            elif self.LT < 1020:
                if (self.LT - 795) % 15 == 0:
                    self.activeWattage = 1.0 / (0.1 * randint(1, base))
            else:
                if (self.LT - 1020) % 20 == 0 and randint(0, 10) <= 10 * self.baseLineCe:
                    self.activeWattage = (1.0 / randint(int(10 * (1 - 3 * self.baseLineCe)), base))
                else:
                    self.activeWattage = self.baseLineCe

            self.cons += self.activeWattage * self.lightWattage
            print "Light Power Draw: " + str(self.activeWattage * self.lightWattage)
            print
        return self.cons


if __name__ == "__main__":
    #days = [0, 30, 60, 120, 180, 210, 240, 270, 300, 330, 360]
    days = [180, 0]
    power = 0

    for day in days:
        b = Building(day)
        print str(day)
        power = 0
        draw = 0
        for minute in range(0, 1440):
            b.LT = minute
            #print minute / 60
            x = b.generation(b) * 60
            y = b.consumption(b) * 60
            if not b.preDawn and not b.dusk:
                power += x * 1000
                #print "EoT: " + str(b.EoT)
                #print "LST: " + str(b.LST)
                #print "HRA: " + str(b.HRA)
                #print "Declination: " + str(b.declination)
                #print "SELA: " + str(b.SELA * (180 / math.pi))
                #print "SAZA: " + str(b.SAZA * (180 / math.pi))
                #print "Airmass: " + str(b.am)
                #print "Solar IR: " + str(b.solarIrradience)
                #print "Module Coe: " + str(b.moduleCe)
                #print "Generation: " + str(b.gen * 1000)
                #print "Draw: " + str(y)
                #print "Delta: " + str(b.delta)
                #print
            #print "Draw: " + str(y)
            draw += y

        print
        net = (power - draw) / 1
        #print "Delta: " + str(b.delta)
        print "Power: " + str(power / 3600 / 1000)
        print "Draw: " + str(draw / 3600 / 1000)
        print "Net: " + str(net / 3600 / 1000)
        print

