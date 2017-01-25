
from tkinter import *
from TollBooth import *
from Constants import *

class Window(object):

	TIME = 0
	outputFile = open("output.txt", 'w')
	paused = False
	timeMultiplier = 1

	def __init__(self, root):
		self.WIDTH = 500
		self.HEIGHT = 850
		self.root = root
		self.boothList = []

		self.canvas = Canvas(self.root, width = self.WIDTH, height = self.HEIGHT, bg = "white")
		self.canvas.pack()

		self.time = self.canvas.create_text(10, 10, anchor = "nw")
		
		self.createTollBoothLine(7)

		self.root.bind("<space>", self.setPause)
		self.root.bind("<Left>", self.decreaseTime)
		self.root.bind("<Right>", self.increaseTime)

	def createTollBoothLine(self, count):
		boothTypes1 = [SPAWN_RATE_TELLER, SPAWN_RATE_TELLER, SPAWN_RATE_EXACT, SPAWN_RATE_EXACT, SPAWN_RATE_EXACT, SPAWN_RATE_ELECTRONIC, SPAWN_RATE_ELECTRONIC]
		boothTypes2 = [SPAWN_RATE_TELLER, SPAWN_RATE_TELLER, SPAWN_RATE_TELLER, SPAWN_RATE_EXACT, SPAWN_RATE_EXACT, SPAWN_RATE_EXACT, SPAWN_RATE_ELECTRONIC]
		boothTypes3 = [SPAWN_RATE_TELLER, SPAWN_RATE_TELLER, SPAWN_RATE_EXACT, SPAWN_RATE_EXACT, SPAWN_RATE_ELECTRONIC, SPAWN_RATE_ELECTRONIC, SPAWN_RATE_ELECTRONIC]
		boothTypes4 = [SPAWN_RATE_TELLER, SPAWN_RATE_EXACT, SPAWN_RATE_EXACT, SPAWN_RATE_EXACT, SPAWN_RATE_EXACT, SPAWN_RATE_ELECTRONIC, SPAWN_RATE_ELECTRONIC]
		
		for i in range(0, count):
			newBooth = TollBooth(self.canvas, 
					BOOTH_WIDTH * (i + 1) + SEPARATION_DISTANCE * i, 
					self.HEIGHT - ACCELERATION_DISTANCE * i - BOOTH_LENGTH, boothTypes4[i])

			if (len(self.boothList) != 0):
				self.boothList[-1].next = newBooth
			self.boothList.append(newBooth)

		self.updateBooths()

	def updateBooths(self):
		if not Window.paused:
			for b in self.boothList:
				b.update()

			self.canvas.itemconfig(self.time, text = "TIME = {:1.2f} seconds ({}x speed)".format(Window.TIME, Window.timeMultiplier))
			Window.TIME += TICK_INTERVAL
		
		self.root.after(int(TICK_INTERVAL * 1000 / Window.timeMultiplier), self.updateBooths)

	def increaseTime(self, event):
		Window.timeMultiplier += 1 if Window.timeMultiplier < 10 else 0

	def decreaseTime(self, event):
		Window.timeMultiplier -= 1 if Window.timeMultiplier > 1 else 0

	def setPause(self, event):
		Window.paused = not Window.paused