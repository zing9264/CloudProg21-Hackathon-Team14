import picamera
from time import sleep
from pynput import keyboard
import sys
import toS3
import json
import RPi.GPIO as GPIO

camera = picamera.PiCamera()

k=0


def on_press(key):
    global k
    try:
        print('alphanumeric key {0} pressed'.format(key.char))
        if key.char == 'a':
            print("take a picture" )
            camera.capture('test.jpg')
            sleep(1)
            res=toS3.send2S3()
            
            print("return send2S3:")
            print(res)
            message=str(toS3.waitforqueue(),encoding='utf-8')
            print("return waitforqueue:")
            message=json.loads(message)
            try:
                PIN_LED=25
                print(GPIO.BCM)
                GPIO.setmode(GPIO.BCM)
                print(GPIO.OUT)
                GPIO.setup(PIN_LED,GPIO.OUT)
                print(message['FaceDetails'])
                if len(message['FaceDetails'])!=0:
                    if float(message['FaceDetails'][0]['Confidence'])>=70:
                        GPIO.output(PIN_LED,GPIO.HIGH)
                        print("led light!")
                        sleep(5)
                        GPIO.output(PIN_LED,GPIO.LOW)
                        print("led close!")
                else:
                    print('no face detect')
            except KeyboardInterrupt:  
                print("STOP")
            except Exception as e:  
                print(e)
            finally:  
                GPIO.cleanup() # 把這段程式碼放在 finally 區域，確保程式中止時能夠執行並清掉GPIO的設定！

        if key.char == 'z':
            print("quit")
            return False
            
    except AttributeError:
        print('special key {0} pressed'.format(key))

def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False


camera.preview_fullscreen=False
camera.preview_window=(620, 320, 640, 480)

camera.resolution=(640,480)
camera.start_preview()
camera.sharpness = 10
camera.contrast = 30
camera.vflip=False
camera.hflip=False
camera.exposure_mode = 'auto'

# ...or, in a non-blocking fashion:
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()
listener.join()

camera.stop_preview()
camera.close()
