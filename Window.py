
from tkinter import *
from TollBooth import *
from Constants import *

import time

class Window(object):

	TIME = 1
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

		boothTypes1 = [SPAWN_RATE_TELLER, SPAWN_RATE_TELLER, SPAWN_RATE_EXACT, SPAWN_RATE_EXACT, SPAWN_RATE_EXACT, SPAWN_RATE_ELECTRONIC, SPAWN_RATE_ELECTRONIC]
		boothTypes2 = [SPAWN_RATE_TELLER, SPAWN_RATE_TELLER, SPAWN_RATE_TELLER, SPAWN_RATE_EXACT, SPAWN_RATE_EXACT, SPAWN_RATE_EXACT, SPAWN_RATE_ELECTRONIC]
		boothTypes3 = [SPAWN_RATE_TELLER, SPAWN_RATE_TELLER, SPAWN_RATE_EXACT, SPAWN_RATE_EXACT, SPAWN_RATE_ELECTRONIC, SPAWN_RATE_ELECTRONIC, SPAWN_RATE_ELECTRONIC]
		boothTypes4 = [SPAWN_RATE_TELLER, SPAWN_RATE_EXACT, SPAWN_RATE_EXACT, SPAWN_RATE_EXACT, SPAWN_RATE_EXACT, SPAWN_RATE_ELECTRONIC, SPAWN_RATE_ELECTRONIC]

		self.createTollBoothLine(boothTypes1)

		self.root.bind("<space>", self.setPause)
		self.root.bind("-", self.decreaseTime)
		self.root.bind("=", self.increaseTime)
		self.root.bind("<MouseWheel>", self.zoom)


		self.setupUI()

	def setupUI(self):
		lenX = 40
		lenY = 20
		posX = self.WIDTH - 10 - lenX
		posY = 20
		disX = 10
		disY = 10

		buttons = []
		for i in range(0, 2):
			bbox = [posX, 
					posY + (lenY + disY) * i, 
					posX + lenX, 
					posY + lenY * (i + 1) + disY * i]
			buttons.append(self.canvas.create_rectangle(bbox, fill = "#A3A3A3"))

		self.canvas.tag_bind(buttons[0], "<Button-1>", self.toggleCarToolTips)
		self.canvas.tag_bind(buttons[1], "<Button-1>", self.toggleBoothToolTips)

	def createTollBoothLine(self, boothList):
		for i in range(0, len(boothList)):
			newBooth = TollBooth(self.canvas, 
					BOOTH_WIDTH * (i + 1) + SEPARATION_DISTANCE * i, 
					self.HEIGHT - ACCELERATION_DISTANCE * i - BOOTH_LENGTH, boothList[i])

			if (len(self.boothList) != 0):
				self.boothList[-1].next = newBooth
			self.boothList.append(newBooth)

		self.updateBooths()

	def updateBooths(self):
		start = time.time()

		if not Window.paused:
			for b in self.boothList:
				b.update()

			Window.TIME += TICK_INTERVAL
		
		end = time.time()
		self.canvas.itemconfig(self.time, text = "TIME = {:1.2f} seconds ({}x speed)".format(Window.TIME, Window.timeMultiplier))
		self.root.after(max(1, int(TICK_INTERVAL * 1000 / Window.timeMultiplier + start - end)), self.updateBooths)

	def increaseTime(self, event):
		Window.timeMultiplier += 1 if Window.timeMultiplier < 10 else 0

	def decreaseTime(self, event):
		Window.timeMultiplier -= 1 if Window.timeMultiplier > 1 else 0

	def setPause(self, event):
		Window.paused = not Window.paused

	def toggleCarToolTips(self, event):
		for b in self.boothList:
			for c in b.carList:
				c.toggleToolTip()

	def toggleBoothToolTips(self, event):
		for b in self.boothList:
			b.toggleToolTip()

	def zoom(self, event):
		self.canvas.yview_scroll(-1*(event.delta/120), "units")