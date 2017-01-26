
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

		self.drawnCar = self.canvas.create_rectangle(self.bbox, fill = "black")
		self.toolTip = self.canvas.create_text(self.bbox[2] + self.dim[0], self.bbox[1] - self.dim[1] / 2, anchor = "nw", state = "hidden")
		self.currentAccel = 0
		self.sepDist = 0, 0

		self.canvas.tag_bind(self.drawnCar, "<Button-1>", self.toggleToolTip)

	# updates the car speed and position
	def updateCar(self):

		# slow down for car ahead or if needed for a merge
		nearCarDistAdj, nearCarSpeedAdj = self.booth.next.queryCars(self) if self.wantsMerging and self.booth.next else (None, None)
		nearCarDist, nearCarSpeed = self.booth.queryCars(self)

		sDelta1 = self.accel
		sDelta2 = self.accel
		if (nearCarDist and nearCarDist < self.getReactDist()):
			sDelta1 = self.getSensitivity(nearCarDist) * (nearCarSpeed - self.speed)
		if (nearCarDistAdj and self.wantsMerging and nearCarDistAdj < self.getMergeDist()):
			sDelta2 = self.mergeAcceleration()

		sDelta = min(max(min(sDelta1, sDelta2), -self.decel), self.accel)
		self.speed = min(max(self.speed + sDelta, 0), self.limit)
		self.moveCar(self.speed * cos(self.dir), self.speed * sin(self.dir))
		self.workMerge(nearCarDistAdj)

		if self.bbox[1] < 0: 
			self.removeCar()
		else:		 
			self.drawCar()
			self.drawToolTip()

		# info for tooltip
		self.currentAccel = sDelta
		self.sepDist = nearCarDist, nearCarDistAdj

	# moves the car by the given x/y shift
	def moveCar(self, shiftx, shifty):
		self.bbox[0] += shiftx
		self.bbox[1] -= shifty
		self.bbox[2] += shiftx
		self.bbox[3] -= shifty

	# update the merging behaviour
	def workMerge(self, mergingDistFree):
		if (not self.booth.next): return

		if (self.bbox[1] < self.booth.next.bbox[1] - self.booth.next.accDist):
			nextDist = self.getCenter()[0] - self.booth.next.getCenter()[0]
			if (not self.wantsMerging and self not in self.booth.next.carList):
				self.startMerge()
			elif (self.wantsMerging and (mergingDistFree == None or mergingDistFree > self.getMergeDist())):
				self.doMerge()
			elif (nextDist > 0):
				self.moveCar(-nextDist, 0)
				self.endMerge()

	# enter the merge behaviour to find a spot and transfer booth lanes
	def startMerge(self):
		self.wantsMerging = True

	# once it is safe to merge, perform maneuver to switch to new lane
	def doMerge(self):
		self.dir = pi / 3
		self.wantsMerging = False
		self.booth.next.carList.append(self)

	# once entered, become a flow of booth lane traffic
	def endMerge(self):
		self.dir = pi / 2
		self.booth.carList.remove(self)
		self.booth = self.booth.next
		self.booth.totalSpawned += 1

	# make a tooltip
	def toggleToolTip(self, event):
		self.toolTipState = not self.toolTipState
		self.canvas.itemconfig(self.toolTip, state = "normal" if self.toolTipState else "hidden")

	# returns the distance this car desires with the one ahead
	def getFollowDist(self):
		return self.distf + self.speed / (4.4 * TICK_INTERVAL) * self.dim[1]

	# returns the distance this car desires with the one ahead
	def getMergeDist(self):
		return self.distf + self.speed / (14.0 * TICK_INTERVAL) * self.dim[1]

	# the threshold at which the car should begin braking for a car in front
	def getReactDist(self):
		return self.getFollowDist() - (self.speed ** 2) / ((2.0 * -self.decel))

	# a value to determine the braking power applied when choosing the desired distance with distance > 0
	def getSensitivity(self, distDelta):
		denominator = 2.0 * max(0.001, distDelta - self.getFollowDist())
		return (28.0 * TICK_INTERVAL) / denominator

	# defines the acceleration to take on while attempting to merge
	def mergeAcceleration(self):
		return -self.decel if self.speed > self.limit / 2 else 0.0

	# draws the car to the canvas at its current position
	def drawCar(self):
		self.canvas.coords(self.drawnCar, self.bbox)

	def drawToolTip(self):
		self.canvas.coords(self.toolTip, self.bbox[2] + self.dim[0], self.bbox[1] - self.dim[1] / 2)
		self.canvas.itemconfig(self.toolTip, text = 
			"{:2.2f}kph, {:2.2f}ms-2 {:2.2f},{:2.2f},{:2.2f}".format(self.speed / TICK_INTERVAL / GRID_RATIO * 3.6, 
				self.currentAccel / TICK_INTERVAL ** 2 / GRID_RATIO, (self.sepDist[0] if self.sepDist[0] else 0) * GRID_RATIO, self.getFollowDist(),self.getReactDist()))

	# removes this car from updates and the canvas
	def removeCar(self):
		self.booth.carList.remove(self)
		self.canvas.delete(self.drawnCar)
		self.canvas.delete(self.toolTip)

	# returns the geometric center as coordinates
	def getCenter(self):
		return sum(self.bbox[::2]) / len(self.bbox) * 2, sum(self.bbox[1::2]) / len(self.bbox) * 2
