
from numpy.random import poisson
from enum import Enum
from Car import *
from Constants import *

import Window

class TollBooth(object):
	def __init__(self, canvas, startx, starty, tSpawn = SPAWN_RATE_TELLER, boothId = None):
		self.canvas = canvas
		self.startx = startx
		self.starty = starty

		self.runDist = RUN_DISTANCE
		self.accDist = ACCELERATION_DISTANCE
		self.carList = []
		self.tSpawn = tSpawn
		self.tRemain = 0.0
		self.totalSpawned = 0
		self.color = "brown" if tSpawn == SPAWN_RATE_TELLER else "green" if tSpawn == SPAWN_RATE_EXACT else "lightblue"

		self.dim = [BOOTH_WIDTH, BOOTH_LENGTH]
		self.bbox = [startx - self.dim[0] / 2, starty - self.dim[1] / 2,
				startx + self.dim[0] / 2, starty + self.dim[1] / 2]
		self.next = None
		self.boothId = startx * 31 + starty * 7 if boothId == None else boothId
		self.nextWrite = 0

		self.toolTipState = False
		self.toolTip = self.canvas.create_text(self.bbox[2] + self.dim[0] / 2, 
			self.bbox[1] + self.dim[1] / 2, state = "hidden", anchor = "nw")

		self.drawnBooth = self.canvas.create_rectangle(self.bbox, fill = self.color)
		self.canvas.create_rectangle([self.bbox[0], self.bbox[1] - self.accDist, 
			self.bbox[2], self.bbox[1]], fill = "gray")
		self.canvas.create_rectangle([self.bbox[0], self.bbox[1] - (self.runDist + self.accDist), 
			self.bbox[2], self.bbox[1] - self.accDist], fill = "lightgray")

		self.canvas.tag_bind(self.drawnBooth, "<Button-1>", self.toggleToolTip)

	# draw the tooltip
	def drawToolTip(self):
		self.canvas.coords(self.toolTip, self.bbox[2] + self.dim[0] / 2, self.bbox[1] + self.dim[1] / 2)
		self.canvas.itemconfig(self.toolTip, text = "{}, cars = {:2.2f}, spawn = {}".format(
			self.boothId, self.totalSpawned / Window.Window.TIME * 3600, self.tSpawn))

	# draws the car to the canvas at its current position
	def drawTollBooth(self):
		self.canvas.coords(self.drawnBooth, self.bbox)

	# creates a car out of this booth
	def spawnCar(self):
		if (self.tRemain <= 0.0):
			self.tRemain = poisson(self.tSpawn)
			
			newCar = Car(self.canvas, self)
			if (not self.queryCars(newCar)[0] or self.queryCars(newCar)[0] > 0):
				self.addCar(newCar)
		else:
			self.tRemain -= TICK_INTERVAL

	# iterates through the list of vehicles owned by this toll lane
	def updateCars(self):
		for c in self.carList:
			if (c.booth == self):
				c.updateCar()

	# performs updates for this toll lane
	def update(self):
		self.spawnCar()
		self.updateCars()
		self.drawToolTip()

		if self.next == None and self.nextWrite >= 1.0:
			Window.Window.outputFile.write(str(Window.Window.TIME) + " " + str(self.totalSpawned / Window.Window.TIME * 3600) + '\n')
			self.nextWrite = 0

		self.nextWrite += TICK_INTERVAL
			
	# finds car such with smallest distance between front bumpers and returns distance from
	#	front bumper of rear car to back bumper of front car, and front car speed
	def queryCars(self, car):
		carBehind = None
		carFront = None
		length = len(self.carList)
		
		if car not in self.carList:
			pos = 0
			for c in self.carList:
				if (car.bbox[1] > c.bbox[1] or pos == length - 1):
					break
				pos += 1
			if (pos > 0):
				carBehind = self.carList[pos]
		else:
			pos = self.carList.index(car)

		if (pos + 1 < length):
			carFront = self.carList[pos + 1]

		if not carFront and not carBehind:
			return None, None
		elif not carBehind:
			carNear = carFront
		elif not carFront:
			carNear = carBehind
		elif abs(car.bbox[1] - carFront.bbox[1]) < abs(car.bbox[1] - carBehind.bbox[1]):
			carNear = carFront
		else: carNear = carBehind

		return (car.bbox[1] - carNear.bbox[3], carNear.speed)

	# make a tooltip
	def toggleToolTip(self, event):
		self.toolTipState = not self.toolTipState
		self.canvas.itemconfig(self.toolTip, state = "normal" if self.toolTipState else "hidden")

	# returns the geometric center as coordinates
	def getCenter(self):
		return sum(self.bbox[::2]) / len(self.bbox) * 2, sum(self.bbox[1::2]) / len(self.bbox) * 2

	# add car so list is ordered with car closest to booth first
	def addCar(self, car):
		if car in self.carList:
			return
		
		if len(self.carList) == 0:
			self.carList.append(car)
		else:
			pos = 0
			length = len(self.carList)
			for c in self.carList:
				if (car.bbox[1] > c.bbox[1] or pos == length - 1):
					self.carList.insert(pos, car)
					return
				pos += 1
		
		self.totalSpawned += 1

	# remove a car from the car list
	def removeCar(self, car):
		self.carList.remove(car)




