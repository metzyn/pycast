# version 1.1

import os, time, pygame, io
from PIL import Image
from flask import Flask, request
from threading import Thread
import signal

# define globals
FILE_PATH = "/tmp/pycast"
SCALE_X = 0
SCALE_Y = 0
COLUMNS = 4
ROWS = 4
DISPLAYS = 2
CELLS = (COLUMNS * DISPLAYS) * ROWS
images = []
lastUpdate = []
renderImages = []
imageRects = []
renderRects = []



# init flask
app = Flask(__name__)

@app.route('/upload', methods=['PUT'])
def upload():
	try:
		file = request.files['file']
		index = int(file.filename.split('.')[0]) - 1
		image = Image.open(io.BytesIO(file.read()))
		image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
		image = pygame.transform.smoothscale(image, (SCALE_X, SCALE_Y))
		images[index] = image.convert()
		lastUpdate[index] = time.time()
		renderImages[index] = True
		return 'Upload successful!'
	except:
		return 'Error processing upload!'

def runFlask():
	app.run(host='0.0.0.0', port=5000)



# init pygame
def gameLoop():
	
	pygame.init()
	displayInfo = pygame.display.Info()
	display = pygame.display.set_mode((displayInfo.current_w, displayInfo.current_h), pygame.FULLSCREEN, pygame.NOFRAME)
	#display = pygame.display.set_mode((displayInfo.current_w, displayInfo.current_h))
	clock = pygame.time.Clock()
	font = pygame.font.Font(None, int(displayInfo.current_h * 0.05))
	pygame.mouse.set_visible(False)
	
	global SCALE_X, SCALE_Y
	SCALE_X = int(displayInfo.current_w / (COLUMNS * DISPLAYS))
	SCALE_Y = int(displayInfo.current_h / ROWS)

	# create placeholder images
	for i in range(1, CELLS + 1):
		background_color = (i * 5 + 10, i * 5 + 10, i * 5 + 10)
		image = Image.new("RGB", (SCALE_X, SCALE_Y), background_color)
		image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
		images.append(image)
		lastUpdate.append(0)
		renderImages.append(True)
	
	positions = []
	# calculate image positions on left display
	for y in range(ROWS):
		for x in range(COLUMNS):
			positions.append((x * SCALE_X, y * SCALE_Y))
			imageRects.append(pygame.Rect(x * SCALE_X, y * SCALE_Y, SCALE_X, SCALE_Y))
	# calculate image positions on right display
	for y in range(ROWS):
		for x in range(COLUMNS):
			positions.append(((x * SCALE_X) + int(displayInfo.current_w / 2), y * SCALE_Y))
			imageRects.append(pygame.Rect((x * SCALE_X) + int(displayInfo.current_w / 2), y * SCALE_Y, SCALE_X, SCALE_Y))

	currentTime = time.time()

	# run loop
	while True:
		
		# press 'q' to quit
		pygame.event.pump()
		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
				return False
		
		# clear display
		#display.fill((0, 0, 0))
		
		# display images and their ID numbers
		for i in range(CELLS):
			color = (255, 0, 0) if time.time() - lastUpdate[i] > 10 else (0, 255, 0)
			
			# regenerate image when lost contact with agent
			if currentTime - lastUpdate[i] > 60 and lastUpdate[i] != 0:
				background_color = (i * 5 + 10, i * 5 + 10, i * 5 + 10)
				image = Image.new("RGB", (SCALE_X, SCALE_Y), background_color)
				image = pygame.image.fromstring(image.tobytes(), image.size, image.mode)
				images[i] = image
				lastUpdate[i] = 0
				renderRects.append(imageRects[i])
			
			# render image
			if renderImages[i] == True:
				display.blit(images[i], positions[i])
				
			# render text
			text = font.render(str(i + 1), True, color)
			display.blit(text, (positions[i][0] + 10, positions[i][1] + 10))
			
		# render frame time
		#text = font.render(str(clock.get_rawtime()), True, (0, 0, 255))
		#display.blit(text, (10, displayInfo.current_h - font.size("0")[1]))
		
		# flip frame buffer
		#pygame.display.flip()
		#renderRects.append(pygame.Rect(10, displayInfo.current_h - font.size("0")[1], 200, 100))
		for i in range(CELLS):
			if renderImages[i] == True:
				renderRects.append(imageRects[i])
		print(renderRects)
		pygame.display.update(renderRects)

		# set all images to not render
		for i in range(CELLS):
			renderImages[i] = False
		renderRects.clear()
		
		# set framerate to 1 FPS
		clock.tick(1)
		currentTime = time.time()
	


# start flask
flaskThread = Thread(target=runFlask)
flaskThread.start()

# start loop
restart = True
while restart == True:
	restart = gameLoop()

# quit pygame and flask
pygame.quit()
os.kill(os.getpid(), getattr(signal, "SIGKILL", signal.SIGTERM))

