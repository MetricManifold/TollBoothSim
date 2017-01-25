
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
		self.toolTip = self.canvas.create_text(self.bbox[2] + self.dim[0] / 2, self.bbox[1] + self.dim[1] / 2, anchor = "nw")

		self.drawBooth()
		self.canvas.tag_bind(self.thisBooth, "<Button-1>", self.makeToolTip)

	# draws this booth to the canvas
	def drawBooth(self):
		self.thisBooth = self.canvas.create_rectangle(self.bbox, fill = self.color)
		self.canvas.create_rectangle([self.bbox[0], self.bbox[1] - self.accDist, 
				self.bbox[2], self.bbox[1]], fill = "gray")
		self.canvas.create_rectangle([self.bbox[0], self.bbox[1] - (self.runDist + self.accDist), 
				self.bbox[2], self.bbox[1] - self.accDist], fill = "lightgray")

	def drawToolTip(self):
		if (self.toolTipState):
			self.canvas.itemconfig(self.toolTip, state = "normal", text = 
					"{}, cars = {:2.2f}, spawn = {}".format(self.boothId, self.totalSpawned / Window.Window.TIME * 3600, self.tSpawn))
		else:
			self.canvas.itemconfig(self.toolTip, state = "hidden")

		if self.next == None and self.nextWrite >= 1.0:
			Window.Window.outputFile.write(str(Window.Window.TIME) + " " + str(self.totalSpawned / Window.Window.TIME * 3600) + '\n')
			self.nextWrite = 0

		self.nextWrite += TICK_INTERVAL

	# creates a car out of this booth
	def spawnCar(self):
		if (self.tRemain <= 0.0):
			self.tRemain = poisson(self.tSpawn)
			self.carList.append(Car(self.canvas, self))
			self.totalSpawned += 1
		else:
			self.tRemain -= TICK_INTERVAL


	# iterates through the list of vehicles owned by this toll lane
	def updateCars(self):
		for c in self.carList:
			if (c.booth != self): continue		# if this booth does not own the car
			c.updateCar()

			if (self.next is None): continue	# if there is no next booth
			nextDist = (c.bbox[0] + c.bbox[2]) / 2 - (self.next.bbox[0] + self.next.bbox[2]) / 2

			# if the car is in the merging area
			if (not c.merging and c.bbox[3] <= self.next.bbox[1] - self.next.accDist):
				c.startMerge()
			# if the car has entered the other booth lane
			elif (nextDist > 0):
				c.moveCar(-nextDist, 0)
				c.endMerge()

	# performs updates for this toll lane
	def update(self):
		self.spawnCar()
		self.updateCars()
		self.drawToolTip()
			
	# look for a car in front of the one given by the parameter, return distance and speed
	def queryCar(self, car):
		carClose = None
		for c in self.carList:
			if (c == car): continue
			if (carClose == None): carClose = c
			elif (abs(car.centreY() - c.centreY()) < abs(car.centreY() - carClose.centreY())):
				carClose = c
		if (carClose == None): return None, None

		sepDist = car.bbox[1] - carClose.bbox[3]
		reactDist = car.getReactDist(carClose.speed)
		wantDist = car.getWantDist()

		if (car.booth.next == self):
			if (-(car.dim[1] + carClose.dim[1] + car.fDist) < sepDist < car.fDist):
				return sepDist, carClose.speed
		else:
			if (-car.dim[1] < sepDist < reactDist):
				return abs(sepDist), carClose.speed
		
		return None, None

	# make a tooltip
	def makeToolTip(self, event):
		self.toolTipState = not self.toolTipState