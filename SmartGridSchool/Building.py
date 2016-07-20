'''
from magi.util.agent import DispatchAgent, agentmethod
from magi.util.processAgent import initializeProcessAgent
'''

# commented out code: don't know if necessary/not yet implemented
import logging
from math import sin, cos, asin, acos
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
        self.panelEff = 0.17
        self.panelArea = 20
        self.ELA = 35 * (math.pi / 180)
        self.AZA = math.pi

        self.day = 1
        self.LT = 0
        self.B = (math.pi / 180) * (360 / 365) * (self.day - 81)
        self.EoT = 9.87 * sin(2 * self.B) - 7.53 * cos(self.B) - 1.5 * sin(self.B)
        self.delta = 23.45 * sin(self.B)
        self.LAT = 33.77984


    # electricity generation
    def generation(self, msg):
        self.LST = self.LT + (4 * (-13.359) + self.EoT) / 60
        self.HRA = (math.pi / 180) * 15 * (self.LST - 12)
        self.SELA = asin(sin(self.delta) * sin(self.LAT) + cos(self.delta) * cos(self.LAT) * cos(self.HRA))
        self.SAZA = acos(sin(self.delta) * cos(self.LAT) + cos(self.delta) * sin(self.LAT) * cos(self.HRA) / cos(self.SELA))
        self.declination = (1 - self.SELA)
        self.solarIrradiance = pow(1.353, pow(pow(0.7, (1 / 1e-4) + cos(1 / self.declination)), 0.678))
        self.solarIrradiance *= (cos(self.SELA) * sin(self.ELA) * cos(self.AZA - self.SAZA) + sin(self.SELA) * cos(self.ELA))
        self.gen = self.solarIrradiance * (self.panelEff * 1.5) * self.panelArea
        '''
        print(self.HRA)
        print(self.SELA)
        print(self.SAZA)
        print(self.declination)
        print(self.solarIrradiance)
        '''
        return -self.gen

    # electricity generation
    def generationMoving(self, msg, direction):
        self.LST = self.LT + (4 * (-13.359) + self.EoT) / 60
        self.HRA = (math.pi / 180) * 15 * (self.LST - 12)
        self.SELA = asin(sin(self.delta) * sin(self.LAT) + cos(self.delta) * cos(self.LAT) * cos(self.HRA))
        self.SAZA = acos(sin(self.delta) * cos(self.LAT) + cos(self.delta) * sin(self.LAT) * cos(self.HRA) / cos(self.SELA))



        self.declination = (1 - self.SELA)
        self.solarIrradiance = pow(1.353, pow(pow(0.7, (1 / 1e-4) + cos(1 / self.declination)), 0.678))

        if direction == 0:
            self.ELA = self.SELA
            self.AZA = self.SAZA
            self.solarIrradiance *= (cos(self.SELA) * sin(self.ELA) * cos(self.AZA - self.SAZA) + sin(self.SELA) * cos(self.ELA))
        elif direction == 1:
            self.ELA = self.SELA
            self.solarIrradiance *= (cos(self.SELA) * sin(self.ELA) * cos(self.AZA - self.SAZA) + sin(self.SELA) * cos(self.ELA))

        elif direction == 2:
            self.AZA = self.SAZA
            self.solarIrradiance *= (cos(self.SELA) * sin(self.ELA) * cos(self.AZA - self.SAZA) + sin(self.SELA) * cos(self.ELA))

        self.gen = self.solarIrradiance * (self.panelEff * 1.5) * self.panelArea

        return -self.gen



    # electricity consumption
    def consumption(self, msg):
        self.c = 1


if __name__ == "__main__":
    room = Building()
    room1 = Building()
    room2 = Building()
    power = 0
    power1 = 0
    power2 = 0
    for i in range(420, 1140):
        room.LT = i / 60.0
        # print(room.LT)
        power += room.generationMoving(room, 0) / 60

    for j in range(420, 1140):
        room.LT = i / 60.0
        power1 += room1.generationMoving(room1, 1) / 60

    for k in range(420, 1140):
        room.LT = i / 60.0
        power2 += room2.generationMoving(room2, 2) / 60

    print(str(power))
    print("")
    print(str(power1))
    print("")
    print(str(power2))







