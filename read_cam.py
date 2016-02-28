import cv2
import cv2.cv
from pymongo import MongoClient
import datetime
import urllib 
import numpy as np

DB_IP='52.27.134.146'
CAM_URL='http://10.8.0.4:8080/?action=stream'

db_client=MongoClient(DB_IP, 27017)
db=db_client.power_stats
print(db.snapshot)
stream=urllib.urlopen(CAM_URL)
bytes=''
while True:
    bytes+=stream.read(1024)
    a = bytes.find('\xff\xd8')
    b = bytes.find('\xff\xd9')
    if a!=-1 and b!=-1:
        jpg = bytes[a:b+2]
        bytes= bytes[b+2:]
        img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
        cv2.imshow('RAW',img)
        
        # Find circles of known radius and draw them
        gray = (cv2.cvtColor(img,cv2.COLOR_BGR2GRAY))
        equalized_gray = cv2.equalizeHist(gray)

        # Find most prominent lines and draw them
        edges = cv2.Canny(gray,25,100,apertureSize = 3)
        lines = cv2.HoughLines(edges,1,np.pi/180,200)
        avg_theta = 0
        for rho,theta in lines[0]:
            avg_theta += theta
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            cv2.line(img,(x1,y1),(x2,y2),(230,255,2),1)

        # Fix image rotation
        #print(360*avg_theta/lines[0].size/2-90)
        M = cv2.getRotationMatrix2D((640/2,480/2),360*avg_theta/lines[0].size/2-90,1)
        img = cv2.warpAffine(img,M,(640,480))

        #cv2.imshow('Equalized',gray)
        circles = cv2.HoughCircles(equalized_gray,cv2.cv.CV_HOUGH_GRADIENT,1,50,param1=25,param2=25,minRadius=50,maxRadius=60)
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            # draw the outer circle
#            cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
            # draw the center of the circle
#            cv2.circle(img,(i[0],i[1]),2,(0,0,255),1)
            # draw the brightest spot in this circle
            r = 10
            (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(equalized_gray[i[1]-r:i[1]+r, i[0]-r:i[0]+r])
            cv2.circle(equalized_gray, (maxLoc[0]+i[0]-r,maxLoc[1]+i[1]-r), 2, (0, 255, 0), 2)
            cv2.circle(equalized_gray, (maxLoc[0]+i[0]-r,maxLoc[1]+i[1]-r), i[2], (0,0,255),2)
            # take the avg_point between brightest_spot & center_of_circle as mathematical center 
        
        cv2.imshow('gray,edge,hough,rotate',img)
        if cv2.waitKey(1) ==27:
            exit(0)   
