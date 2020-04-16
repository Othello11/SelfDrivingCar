import numpy as np
import cv2
import serial
import pygame
from pygame.locals import *
import socket
import time
import os
import urllib

class CollectTrainingData(object):
    
    def __init__(self,serial_port, input_size):

        # connect to a serial port
        self.ser = serial.Serial(serial_port, 115200, timeout=1)
        self.send_inst = True

        self.input_size = input_size

        # create labels
        self.k = np.zeros((4, 4), 'float')
        for i in range(4):
            self.k[i, i] = 1

        pygame.init()
        pygame.display.set_mode((250, 250))

    def collect(self, url, host, port):

        saved_frame = 0
        total_frame = 0

        # collect images for training
        print("Start collecting images...")
        print("Press 'q' or 'x' to finish...")
        start = cv2.getTickCount()

        X = np.empty((0, self.input_size))
        y = np.empty((0, 4))

        # stream video frames one by one
        try:
            frame = 1        
            while(True):
                imgResp = urllib.urlopen(url)
                image = cv2.imdecode(np.frombuffer(imgResp.read(), dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                cv2.imshow('image', image)
                print("originla image size")
                print(image.shape)
	        # put the image on screen
            #cv2.imshow('IPWebcam',image)
                height, width = image.shape
                roi = image[int(height/2):height, : ]
            #print(roi.shape)
                temp_array = roi.reshape(1, int(height/2) * width).astype(np.float32)
                print("temp+array size")
                print(temp_array.shape)
                print("roi shape")
                print(roi.shape)
                
                frame += 1
                total_frame += 1

                    # get input from human driver
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        key_input = pygame.key.get_pressed()

                            # complex orders
                        if key_input[pygame.K_UP] and key_input[pygame.K_RIGHT]:
                            print("Forward Right")
                            X = np.vstack((X, temp_array))
                            y = np.vstack((y, self.k[1]))
                            saved_frame += 1
                            self.ser.write(chr(6).encode())

                        elif key_input[pygame.K_UP] and key_input[pygame.K_LEFT]:
                            print("Forward Left")
                            X = np.vstack((X, temp_array))
                            y = np.vstack((y, self.k[0]))
                            saved_frame += 1
                            self.ser.write(chr(7).encode())

                        elif key_input[pygame.K_DOWN] and key_input[pygame.K_RIGHT]:
                            print("Reverse Right")
                            self.ser.write(chr(8).encode())

                        elif key_input[pygame.K_DOWN] and key_input[pygame.K_LEFT]:
                            print("Reverse Left")
                            self.ser.write(chr(9).encode())

                            # simple orders
                        elif key_input[pygame.K_UP]:
                            print("Forward")
                            saved_frame += 1
                            X = np.vstack((X, temp_array))
                            y = np.vstack((y, self.k[2]))
                            print("x is")
                            print(X)
                            self.ser.write(chr(1).encode())

                        elif key_input[pygame.K_DOWN]:
                            print("Reverse")
                            self.ser.write(chr(2).encode())

                        elif key_input[pygame.K_RIGHT]:
                            print("Right")
                            X = np.vstack((X, temp_array))
                            y = np.vstack((y, self.k[1]))
                            saved_frame += 1
                            self.ser.write(chr(3).encode())

                        elif key_input[pygame.K_LEFT]:
                            print("Left")
                            X = np.vstack((X, temp_array))
                            y = np.vstack((y, self.k[0]))
                            saved_frame += 1
                            self.ser.write(chr(4).encode())

                        elif key_input[pygame.K_x] or key_input[pygame.K_q]:
                            print("exit")
                            self.send_inst = False
                            self.ser.write(chr(0).encode())
                            self.ser.close()
                            break

                    elif event.type == pygame.KEYUP:
                        self.ser.write(chr(0).encode())

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # save data as a numpy file
            file_name = str(int(time.time()))
            directory = "training_data"
            if not os.path.exists(directory):
                os.makedirs(directory)
            try:
                np.savez(directory + '/' + file_name + '.npz', train=X, train_labels=y)
            except IOError as e:
                print(e)

            end = cv2.getTickCount()
            # calculate streaming duration
            print("Streaming duration: , %.2fs" % ((end - start) / cv2.getTickFrequency()))

            print(X.shape)
            print(y.shape)
            print("Total frame: ", total_frame)
            print("Saved frame: ", saved_frame)
            print("Dropped frame: ", total_frame - saved_frame)
        
        finally:
            print("jhjoj");
       
            
      

if __name__ == '__main__':
    # host, port
    h, p = "192.168.1.101", 8080
    url='http://192.168.0.101:8080/shot.jpg'
    # serial port
    sp = "/dev/ttyACM0"

    # vector size, half of the image    
    s = 120 * 320

    ctd = CollectTrainingData(sp, s)
    ctd.collect(url, h, p)

 

