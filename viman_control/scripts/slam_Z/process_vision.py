#!/usr/bin/env python

import threading

import numpy as np
import cv2

import rospy
from viman_utility.msg import CamZ

"""
Common class where calibrated CV image matrix is stored and accessed
"""
class Output:
	# dummy image
	img = np.zeros((640,480,3), np.uint8)
	
	lock = threading.Condition()
	
	def __init__(self):
		pass

class IdColor(threading.Thread):
	"""
	Define color ranges for each color. Color sequence:
	green-red-purple-blue-yellow
	"""
	colors = ['green','red','purple','blue','yellow']
	lower_limits = [(41,45,0), (0,0,190), (144,0,0), (94,127,0), (26,0,86)]
	upper_limits = [(64,255,255), (7,255,255), (180,255,255), (124,255,255), (44,255,255)]
	
	def __init__(self, w=640, h=480, ch=3):
		threading.Thread.__init__(self)
		
		# create a publisher to send ID-ed color
		self.color_pub = rospy.Publisher('/viman/color_id', CamZ, queue_size=100)
		self.colorid = CamZ()
		
		# default values
		self.w = w
		self.h = h
		self.window_name = 'SLAM Z Vision'
		self.thresh_area = 65000.0
		self.img = np.zeros((h, w, ch), np.uint8)
		self.masks = np.zeros((h, w, len(self.colors)), np.uint8)
		self.stop_process = False
	
	def run(self):
		kernal = np.ones((5,5), "uint8")
		cv2.namedWindow(self.window_name)
		while not self.stop_process:
			Output.lock.acquire()
			max_area = 0
			color_idx = -1
			self.colorid.name = ''
			self.colorid.area = 0
			try:
				Output.lock.wait(0.1)
				self.img = Output.img
			except:
				print('some issue')
			finally:
				Output.lock.release()
				
			# create masks for each color, dilating to eliminate noise
			frame_hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
			for count, _ in enumerate(self.colors):
				self.masks[:,:, count] = cv2.inRange(frame_hsv,
												self.lower_limits[count],
												self.upper_limits[count])
				self.masks[:,:, count] = cv2.dilate(self.masks[:,:,count],
													kernal)
			##################################################
			# find contours of each color
			for count, col_name in enumerate(self.colors):
				_, contours, _ = cv2.findContours(self.masks[:,:,count].copy(),
														  cv2.RETR_TREE,
														  cv2.CHAIN_APPROX_SIMPLE)
														  
				# get contour of maximum area of a color
				color_max = 0
				area = 0
				c = None
				for _, contour in enumerate(contours):
					area = cv2.contourArea(contour)
					if (area > color_max):
						color_max = area
						c = contour
						
				# take the max area contour amongst the colors
				# if(color_max > self.thresh_area and color_max > max_area):
				if(color_max > self.thresh_area):

					# compute the center of the contour
					M = cv2.moments(c)
					cX = int(M["m10"] / M["m00"])
					cY = int(M["m01"] / M["m00"])
					
					if(abs(cX-self.w/2)<=20 and abs(cY-self.h/2)<=20):
						# draw the bounding rectangle
						x, y, w, h = cv2.boundingRect(c)
						self.img = cv2.rectangle(self.img, (x,y), (x+w, y+h),
												(0,0,0), 2)
						self.img = cv2.putText(self.img, str((cX, cY)), (x+w,y+h-10), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0,0,0), 2)
						self.img = cv2.circle(self.img, (cX, cY), 5, (255, 255, 255), -1)
						self.img = cv2.circle(self.img, (self.w/2, self.h/2), 5, (0, 0, 0), -1)
						self.img = cv2.circle(self.img, (self.w/2, self.h/2), 20, (0, 0, 0), 1)
						self.colorid.name = col_name
						self.colorid.area = area
				elif(color_idx == -1 and count == len(self.colors)-1):
					color_idx = -1
			################################################
			
			# self.color_pub.publish(self.colorid)
			cv2.imshow(self.window_name, self.img)
			cv2.waitKey(1)
		cv2.destroyAllWindows()
		print('Stopped IDing colors...')

if __name__ == '__main__':
	print('Please run the node z_vision.py')

