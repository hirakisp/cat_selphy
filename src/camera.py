import cv2
import time
import picamera
import io
import numpy as np
import os
import requests

print "opencv: " + cv2.__version__
TITLE = "cat's selphy"
IMG_WIDTH = 800
IMG_HEIGHT = 480

class usb_camera:
        cap = cv2.VideoCapture(0)

        def open(self, width, height):
                self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, width)
                self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, height)

        def capture(self):
                self.cap.grab()
                self.cap.grab()
                self.cap.grab()
                self.cap.grab()
                ret, image = self.cap.read()
                return image

        def close(self):
                self.cap.release()

class raspi_camera:
        stream = io.BytesIO()
        camera = picamera.PiCamera()
        count = 0
        
        def open(self, width, height):
                self.camera.resolution = (width, height)

        def capture(self):
                for foo in self.camera.capture_continuous(self.stream,
                                                          format='jpeg'):

                        self.stream.seek(0)
                	data = np.fromstring(self.stream.getvalue(),
                                             dtype=np.uint8)
                	self.image = cv2.imdecode(data, 1)
                	self.stream.seek(0)
                	self.stream.truncate()

                	return self.image

        def save(self, name):
                self.camera.resolution = (3280, 2464)
                print "save: " + name

                # save Big size
                self.camera.capture(name)
                self.count = self.count + 1
                self.camera.resolution = (IMG_WIDTH, IMG_HEIGHT)

                # save miniSize
                cv2.imwrite("tmp.jpg", self.image)
                
        def push_notification(self, file):
                url = "https://notify-api.line.me/api/notify"
                token = ""
                headers = {"Authorization" : "Bearer "+ token}
                message =  ''
                payload = {"message" :  message}
#                files = ""
                files = {"imageFile": open("tmp.jpg", "rb")} #PNG/JPEG
                r = requests.post(url ,headers = headers ,params=payload, files=files)
                print (r)
                
        def close(self):
                self.stream.truncate()

def main():
        # Cascade setting
        cascade_path = "/home/pi/selphy/haarcascade_frontalcatface.xml"
        cascade = cv2.CascadeClassifier(cascade_path)
        rect_color = (255,255,255)

        #camera = usb_camera()
        camera = raspi_camera()
        camera.open(IMG_WIDTH, IMG_HEIGHT)

        cv2.namedWindow(TITLE, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(TITLE, cv2.WND_PROP_FULLSCREEN,
                              cv2.cv.CV_WINDOW_FULLSCREEN)
        
        while True:
                start = time.clock()
                image = camera.capture()
                image_gray = cv2.cvtColor(image, cv2.cv.CV_BGR2GRAY)
                facerect = cascade.detectMultiScale(image_gray,
                                                    scaleFactor=1.1,
                                                    minNeighbors=5,
                                                    minSize=(200, 200))

                if len(facerect) > 0:
                        for rect in facerect:
                                cv2.rectangle(image,
                                              tuple(rect[0:2]),
                                              tuple(rect[0:2]+rect[2:4]),
                                              rect_color, thickness=2)
                        # capture jpeg file
                        ret, name = get_nextfile()
                        if ret == True:
                                camera.save(name)
                                camera.push_notification(name)

                get_image_time = int((time.clock()-start)*1000)
                cv2.putText( image,
                             str(get_image_time)+"ms "+str(1000/get_image_time)+"fps",
                             (10,10), 1, 1, (0,255,0))

                cv2.imshow(TITLE, image)
                if cv2.waitKey(100) > 0:
                        break
        camera.close()
        cv2.destroyAllWindows()

count = 0
def get_nextfile():
        submit = False
        name = ""
        dir = "/media/pi/Sony_4GU/"
        global count

        if os.path.isdir(dir):
                while submit == False:
                        name = dir + str(count) + ".jpg"
                        if os.path.exists(name):
                                count = count + 1
                        else:
                                submit = True
                                
        return (submit, name)
                        
if __name__ == '__main__':
        main()
