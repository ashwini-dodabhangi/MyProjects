



import numpy as np
import argparse
import imutils
import cv2
from imutils.video import VideoStream
import time

from imutils.video import FPS

from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2
import subprocess
#import lcd
import json
from handTracker import *
import cv2
import mediapipe as mp
import numpy as np
import random
import os


class ColorRect():
    def __init__(self, x, y, w, h, color, text='', alpha = 0.5):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.text=text
        self.alpha = alpha
        
    
    def drawRect(self, img, text_color=(255,255,255), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8, thickness=2):
       
        alpha = self.alpha
        bg_rec = img[self.y : self.y + self.h, self.x : self.x + self.w]
        white_rect = np.ones(bg_rec.shape, dtype=np.uint8)
        white_rect[:] = self.color
        res = cv2.addWeighted(bg_rec, alpha, white_rect, 1-alpha, 1.0)
        
      
        img[self.y : self.y + self.h, self.x : self.x + self.w] = res

       
        tetx_size = cv2.getTextSize(self.text, fontFace, fontScale, thickness)
        text_pos = (int(self.x + self.w/2 - tetx_size[0][0]/2), int(self.y + self.h/2 + tetx_size[0][1]/2))
        cv2.putText(img, self.text,text_pos , fontFace, fontScale,text_color, thickness)


    def isOver(self,x,y):
        if (self.x + self.w > x > self.x) and (self.y + self.h> y >self.y):
            return True
        return False



detector = HandTracker(detectionCon=0.8)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)


canvas = np.zeros((720,1280,3), np.uint8)


px,py = 0,0

color = (255,0,0)

brushSize = 5
eraserSize = 20

colorsBtn = ColorRect(200, 0, 100, 100, (120,255,0), 'Color')

colors = []

b = int(random.random()*255)-1
g = int(random.random()*255)
r = int(random.random()*255)
print(b,g,r)
colors.append(ColorRect(300,0,100,100, (b,g,r)))

colors.append(ColorRect(400,0,100,100, (0,0,255)))
#blue
colors.append(ColorRect(500,0,100,100, (255,0,0)))
#green
colors.append(ColorRect(600,0,100,100, (0,255,0)))
#yellow
colors.append(ColorRect(700,0,100,100, (0,255,255)))
#erase (black)
colors.append(ColorRect(800,0,100,100, (0,0,0), "Duster"))

#clear
clear = ColorRect(900,0,100,100, (100,100,100), "EraseAll")


pens = []
for i, penSize in enumerate(range(5,25,5)):
    pens.append(ColorRect(1100,50+100*i,100,100, (50,50,50), str(penSize)))

penBtn = ColorRect(1100, 0, 100, 50, color, 'Size')

# white board button
boardBtn = ColorRect(50, 0, 100, 100, (255,255,0), 'Board')

#define a white board to draw on
whiteBoard = ColorRect(50, 120, 1020, 580, (255,255,255),alpha = 0.6)

coolingCounter = 20
hideBoard = True
hideColors = True
hidePenSizes = True 

lss1=subprocess.getoutput('hostname -I')
lss1=lss1.strip()
lss1=lss1.split()
lss=lss1[0]
print(lss)


outputFrame = None
lock = threading.Lock()


app = Flask(__name__)






@app.route("/")
def index():
    
    return render_template("index.html")

def detect_gesture(frameCount):
   
    global cap, outputFrame, lock, coolingCounter, hidePenSizes, hideBoard, hideColors, color, canvas, brushSize, eraserSize
   

   
    total = 0



    while True:
        if coolingCounter:
            coolingCounter -=1
       
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (1280, 720))
        frame = cv2.flip(frame, 1)
    
        detector.findHands(frame)
        positions = detector.getPostion(frame, draw=False)
        upFingers = detector.getUpFingers(frame)
    
        if upFingers:
            x, y = positions[8][0], positions[8][1]
            if upFingers[1] and not whiteBoard.isOver(x, y):
                px, py = 0, 0
    
             
                if not hidePenSizes:
                    for pen in pens:
                        if pen.isOver(x, y):
                            brushSize = int(pen.text)
                            pen.alpha = 0
                        else:
                            pen.alpha = 0.5
    
               
                if not hideColors:
                    for cb in colors:
                        if cb.isOver(x, y):
                            color = cb.color
                            cb.alpha = 0
                        else:
                            cb.alpha = 0.5
    
                    
                    if clear.isOver(x, y):
                        clear.alpha = 0
                        canvas = np.zeros((720,1280,3), np.uint8)
                    else:
                        clear.alpha = 0.5
                
               
                if colorsBtn.isOver(x, y) and not coolingCounter:
                    coolingCounter = 10
                    colorsBtn.alpha = 0
                    hideColors = False if hideColors else True
                    colorsBtn.text = 'Colors' if hideColors else 'Hide'
                else:
                    colorsBtn.alpha = 0.5
                
               
                if penBtn.isOver(x, y) and not coolingCounter:
                    coolingCounter = 10
                    penBtn.alpha = 0
                    hidePenSizes = False if hidePenSizes else True
                    penBtn.text = 'Pen' if hidePenSizes else 'Hide'
                else:
                    penBtn.alpha = 0.5
    
                
                
                if boardBtn.isOver(x, y) and not coolingCounter:
                    coolingCounter = 10
                    boardBtn.alpha = 0
                    hideBoard = False if hideBoard else True
                    boardBtn.text = 'Board' if hideBoard else 'Hide'
    
                else:
                    boardBtn.alpha = 0.5
                
                
                
    
            elif upFingers[1] and not upFingers[2]:
                if whiteBoard.isOver(x, y) and not hideBoard:
                    
                    cv2.circle(frame, positions[8], brushSize, color,-1)
                   
                    if px == 0 and py == 0:
                        px, py = positions[8]
                    if color == (0,0,0):
                        cv2.line(canvas, (px,py), positions[8], color, eraserSize)
                    else:
                        cv2.line(canvas, (px,py), positions[8], color,brushSize)
                    px, py = positions[8]
            
            else:
                px, py = 0, 0
            

        colorsBtn.drawRect(frame)
        cv2.rectangle(frame, (colorsBtn.x, colorsBtn.y), (colorsBtn.x +colorsBtn.w, colorsBtn.y+colorsBtn.h), (255,255,255), 2)
    
      
        boardBtn.drawRect(frame)
        cv2.rectangle(frame, (boardBtn.x, boardBtn.y), (boardBtn.x +boardBtn.w, boardBtn.y+boardBtn.h), (255,255,255), 2)
    
        
        if not hideBoard:       
            whiteBoard.drawRect(frame)
         
            canvasGray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
            _, imgInv = cv2.threshold(canvasGray, 20, 255, cv2.THRESH_BINARY_INV)
            imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
            frame = cv2.bitwise_and(frame, imgInv)
            frame = cv2.bitwise_or(frame, canvas)
    
    
       
        if not hideColors:
            for c in colors:
                c.drawRect(frame)
                cv2.rectangle(frame, (c.x, c.y), (c.x +c.w, c.y+c.h), (255,255,255), 2)
    
            clear.drawRect(frame)
            cv2.rectangle(frame, (clear.x, clear.y), (clear.x +clear.w, clear.y+clear.h), (255,255,255), 2)
    
    
   
        penBtn.color = color
        penBtn.drawRect(frame)
        cv2.rectangle(frame, (penBtn.x, penBtn.y), (penBtn.x +penBtn.w, penBtn.y+penBtn.h), (255,255,255), 2)
        if not hidePenSizes:
            for pen in pens:
                pen.drawRect(frame)
                cv2.rectangle(frame, (pen.x, pen.y), (pen.x +pen.w, pen.y+pen.h), (255,255,255), 2)
    
    
        #cv2.imshow('video', frame)
        #print("showed video")
                        

                    
   
        total += 1

      
        with lock:
            outputFrame = frame.copy()
            #outputFrame =cv2.flip(outputFrame, 1)
        
def generate():
  
    global outputFrame, lock

  
    while True:
      
        with lock:
           
            if outputFrame is None:
                continue

         
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

          
            if not flag:
                continue

       
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
   
    return Response(generate(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")


if __name__ == '__main__':
   
 

   
    t = threading.Thread(target=detect_gesture, args=(
        32,))
    t.daemon = True
    t.start()

    # start the flask app
    app.run(host='192.168.78.9', port="8000", debug=True,
        threaded=True, use_reloader=False)


cap.release()
cv2.destroyAllWindows()

