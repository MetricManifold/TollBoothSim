
from random import *
from math import *
from Constants import *
import Window

class Car(object):
	def __init__(self, canvas, booth):
		self.canvas = canvas
		
		self.booth = booth
		self.dim = [CAR_WIDTH, CAR_LENGTH + uniform(-CAR_LENGTH_DELTA, CAR_LENGTH_DELTA)]
		self.bbox = [booth.startx - self.dim[0] / 2, booth.starty - self.dim[1] / 2,
				booth.startx + self.dim[0] / 2, booth.starty + self.dim[1] / 2]
		
		self.distf = FOLLOW_DISTANCE
		self.speed = 0.0
		self.accel = ACCELERATION + uniform(-ACCELERATION_DELTA, ACCELERATION_DELTA)
		self.decel = MAX_DECELERATION + uniform(-MAX_DECELERATION_DELTA, MAX_DECELERATION_DELTA)
		self.limit = MAX_SPEED + uniform(-MAX_SPEED_DELTA, MAX_SPEED_DELTA)
		self.dir = pi / 2

		self.merging = False
		self.isMerging = False
		self.toolTipState = False
		self.thisCar = self.canvas.create_rectangle(self.bbox, fill = "black")
		self.toolTip = self.canvas.create_text(self.bbox[2] + self.dim[0], self.bbox[1] - self.dim[1] / 2, anchor = "nw")
		
		self.currentAccel = 0
		self.sepDist = False

		self.canvas.tag_bind(self.thisCar, "<Button-1>", self.makeToolTip)

	def drawCar(self):
		self.canvas.coords(self.thisCar, self.bbox)

		if (self.toolTipState):
			self.canvas.coords(self.toolTip, self.bbox[2] + self.dim[0], self.bbox[1] - self.dim[1] / 2)
			self.canvas.itemconfig(self.toolTip, state = "normal", text = 
					"{} {:2.2f}kph, {:2.2f}ms-2 {}".format(self.booth.boothId, self.speed / TICK_INTERVAL / GRID_RATIO * 3.6, 
						self.currentAccel / TICK_INTERVAL ** 2 / GRID_RATIO, self.sepDist))
		else:
			self.canvas.itemconfig(self.toolTip, state = "hidden")

	# moves the car by the given x/y shift
	def moveCar(self, shiftx, shifty):
		self.bbox[0] += shiftx
		self.bbox[1] -= shifty
		self.bbox[2] += shiftx
		self.bbox[3] -= shifty

	# updates the car speed and position
	def updateCar(self):
		# slow down for car ahead or if needed for a merge
		nearCarDistAdj, nearCarSpeedAdj = self.booth.next.queryCar(self) if (self.booth.next is not None and self.merging) else (None, None)
		nearCarDist, nearCarSpeed = self.booth.queryCar(self)

		if (nearCarDistAdj is None and nearCarDist is None):
			self.sepDist = 0, 0
		else:
			self.sepDist = nearCarDist, nearCarDistAdj

		sDelta = 0
		if (nearCarDist is not None):
			sDelta = min(max(self.sensitivity(nearCarDist) * (nearCarSpeed - self.speed), -self.decel), self.accel)
		elif (nearCarDistAdj is not None):
			sDelta = -self.decel if self.speed > self.minSpeed else 0
		elif (self.speed < self.limit):
			sDelta = self.accel
		
		self.speed += sDelta
		self.speed = max(0, self.speed)

		self.currentAccel = sDelta

		if (self.merging and nearCarDistAdj is None and not self.isMerging):
			self.doMerge()

		self.bbox[0] += self.speed * cos(self.dir)
		self.bbox[1] -= self.speed * sin(self.dir)
		self.bbox[2] += self.speed * cos(self.dir)
		self.bbox[3] -= self.speed * sin(self.dir)

		self.drawCar()

		if self.bbox[1] < 0: 
			self.booth.carList.remove(self)
			self.removeCar()
		
	# enter the merge behaviour to find a spot and transfer booth lanes
	def startMerge(self):
		self.behaviourMerging = True

	# once entered, become a flow of booth lane traffic
	def endMerge(self):
		self.dir = pi / 2
		self.booth.carList.remove(self)
		self.booth = self.booth.next
		self.merging = False
		self.isMerging = False

	# once it is safe to merge, perform maneuver to switch to new lane
	def doMerge(self):
		self.dir = pi / 3
		self.isMerging = True
		self.booth.next.carList.append(self)
		self.booth.next.totalSpawned += 1

	# make a tooltip
	def makeToolTip(self, event):
		self.toolTipState = not self.toolTipState

	def getWantDist(self):
		return self.distf + self.speed / (4.4 * TICK_INTERVAL) * self.dim[1]

	def getReactDist(self, speedOther):
		return self.getWantDist() + (speedOther ** 2 - self.speed ** 2) / ((2.0 * -self.decel))

	def sensitivity(self, deltaX):
		return (14.0 * TICK_INTERVAL) / (2.0 * (deltaX - self.distf))

	def removeCar(self):
		self.canvas.delete(self.thisCar)
		self.canvas.delete(self.toolTip)

	def centreY(self):
		return (self.bbox[1] + self.bbox[3]) / 2