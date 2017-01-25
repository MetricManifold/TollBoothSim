
from random import *
from math import *
from Constants import *
import Window

class Car(object):

	# initializes the car object by setting its properties based on the constants
	# and drawing it to the screen
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

		self.wantsMerging = False
		self.toolTipState = False

		self.thisCar = self.canvas.create_rectangle(self.bbox, fill = "black")
		self.toolTip = self.canvas.create_text(self.bbox[2] + self.dim[0], self.bbox[1] - self.dim[1] / 2, anchor = "nw")
		self.currentAccel = 0
		self.sepDist = 0, 0

		self.canvas.tag_bind(self.thisCar, "<Button-1>", self.showToolTip)

	# updates the car speed and position
	def updateCar(self):

		# update the merging behaviour
		if (self.next):
			nextDist = self.getCenter()[0] - self.booth.next.getCenter()[0]
			if (self.shouldMerge()):	# if the car should begin to merge
				self.startMerge()
			elif (nextDist > 0):		# if the car has entered the other booth lane
				self.moveCar(-nextDist, 0)
				self.endMerge()		

		# slow down for car ahead or if needed for a merge
		nearCarDistAdj, nearCarSpeedAdj = self.booth.next.queryCars(self) if self.wantsMerging else (None, None)
		nearCarDist, nearCarSpeed = self.booth.queryCars(self)

		if (car.booth.next == self):
			if (-(car.dim[1] + carClose.dim[1] + car.fDist) < nearCarDist < car.fDist):
				return sepDist, carClose.speed
		else:
			sepDist = car.bbox[1] - carFront.bbox[3]
			reactDist = car.getReactDist(carFront.speed)
			wantDist = car.getWantDist()
			if (-car.dim[1] < sepDist < reactDist):
				return abs(sepDist), carClose.speed

		return None, None


		if (self.wantsMerging and nearCarDistAdj is None):
			self.doMerge()

		sDelta = self.accel
		if (nearCarDist is not None):
			sDelta = self.getSensitivity(nearCarDist) * (nearCarSpeed - self.speed)
		elif (nearCarDistAdj is not None):
			sDelta = self.mergeAcceleration()
		
		sDelta = min(max(sDelta, -self.decel), self.accel)
		self.speed = min(max(self.speed + sDelta, 0), self.limit)
		self.moveCar(self.speed * cos(self.dir), self.speed * sin(self.dir))

		if self.bbox[1] < 0: 
			self.removeCar()
		else:		 
			self.drawCar()

		# info for tooltip
		self.sepDist = nearCarDist, nearCarDistAdj
		self.currentAccel = sDelta

	# returns whether this car should merge or not
	def shouldMerge(self):
		return self.bbox[1] < self.booth.next.bbox[1] - self.booth.next.accDist and \
			not self.wantsMerging and self not in self.booth.next.carList
		
	# enter the merge behaviour to find a spot and transfer booth lanes
	def startMerge(self):
		self.wantsMerging = True

	# once it is safe to merge, perform maneuver to switch to new lane
	def doMerge(self):
		self.dir = pi / 3
		self.wantsMerging = False
		self.booth.next.carList.append(self)
		self.booth.next.totalSpawned += 1

	# once entered, become a flow of booth lane traffic
	def endMerge(self):
		self.dir = pi / 2
		self.booth.carList.remove(self)
		self.booth = self.booth.next

	# make a tooltip
	def showToolTip(self, event):
		self.toolTipState = not self.toolTipState
		self.canvas.itemconfig(self.toolTip, state = "normal" if self.toolTipState else "hidden")

	# returns the distance this car desires with the one ahead
	def getWantDist(self):
		return self.distf + self.speed / (4.4 * TICK_INTERVAL) * self.dim[1]

	# the threshold at which the car should begin braking for a car in front
	def getReactDist(self, speedOther):
		return self.getWantDist() + (speedOther ** 2 - self.speed ** 2) / ((2.0 * -self.decel))

	# a value to determine the braking power applied when choosing the desired distance
	def getSensitivity(self, dist):
		return (28.0 * TICK_INTERVAL) / (2.0 * (dist - self.getWantDist()))

	# defines the acceleration to take on while attempting to merge
	def mergeAcceleration(self):
		return -self.decel if self.speed > self.minSpeed else 0.0

	# moves the car by the given x/y shift
	def moveCar(self, shiftx, shifty):
		self.bbox[0] += shiftx
		self.bbox[1] -= shifty
		self.bbox[2] += shiftx
		self.bbox[3] -= shifty

	# draws the car to the canvas at its current position
	def drawCar(self):
		self.canvas.coords(self.thisCar, self.bbox)

		self.canvas.coords(self.toolTip, self.bbox[2] + self.dim[0], self.bbox[1] - self.dim[1] / 2)
		self.canvas.itemconfig(self.toolTip, text = 
			"{} {:2.2f}kph, {:2.2f}ms-2 {}".format(self.booth.boothId, self.speed / TICK_INTERVAL / GRID_RATIO * 3.6, 
				self.currentAccel / TICK_INTERVAL ** 2 / GRID_RATIO, self.sepDist))

	# removes this car from updates and the canvas
	def removeCar(self):
		self.booth.carList.remove(self)
		self.canvas.delete(self.thisCar)
		self.canvas.delete(self.toolTip)

	# returns the geometric center as coordinates
	def getCenter(self):
		return average(self.bbox[::2]), average(self.bbox[1::2])