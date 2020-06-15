from threading import Thread
import cv2
import RPi.GPIO as GPIO
import time
import random
import pygame
import numpy as np
import copy
import math



skin_lower = np.array([0, 20, 80], dtype = "uint8")
skin_upper = np.array([20, 255, 255], dtype = "uint8")

threshold = 60  #  BINARY threshold
blurValue = 41  # GaussianBlur parameter
bgSubThreshold = 40
learningRate = 0

global start
start=-1
global score_flag
score_flag=False
global sound_win,sound_lose,sound_draw
sound_win=False
sound_lose=False
sound_draw=False
global cnt_win,cnt_lose,cnt_draw
cnt_win=0
cnt_lose=0
cnt_draw=0
global player,com
player=-1
com=-1
global a
a=None
global ret,frame
global cycle
global screen
global delay
global button_val_r,button_val_y,button_val_b
global red1_pin,green1_pin,blue1_pin,red2_pin,green2_pin,blue2_pin,clock_pin,a_pin,b_pin,c_pin,latch_pin,oe_pi,button_pin_r,button_pin_y,button_pin_b
cycle = 0.0

delay = 0.000001

button_val_r=False
button_val_y=False
button_val_b=False
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
red1_pin = 11
green1_pin = 9
blue1_pin = 7
red2_pin = 8
green2_pin = 9
blue2_pin = 10
clock_pin = 17
a_pin = 22
b_pin = 23
c_pin = 24
latch_pin = 4
oe_pin = 18

button_pin_b=26
button_pin_y=25
button_pin_r=19

GPIO.setup(red1_pin, GPIO.OUT)
GPIO.setup(green1_pin, GPIO.OUT)
GPIO.setup(blue1_pin, GPIO.OUT)
GPIO.setup(red2_pin, GPIO.OUT)
GPIO.setup(green2_pin, GPIO.OUT)
GPIO.setup(blue2_pin, GPIO.OUT)
GPIO.setup(clock_pin, GPIO.OUT)
GPIO.setup(a_pin, GPIO.OUT)
GPIO.setup(b_pin, GPIO.OUT)
GPIO.setup(c_pin, GPIO.OUT)
GPIO.setup(latch_pin, GPIO.OUT)
GPIO.setup(oe_pin, GPIO.OUT)

GPIO.setup(button_pin_b,GPIO.IN)
GPIO.setup(button_pin_y,GPIO.IN)
GPIO.setup(button_pin_r,GPIO.IN)

screen = [[0 for x in xrange(32)] for x in xrange(16)]

def fill_rectangle(x1, y1, x2, y2, color):
    for x in range(x1, x2):
        for y in range(y1, y2):
            screen[y][x] = color
#fill_rectangle(20, 4, 30, 15, 0)
#fill_rectangle(20, 4, 30, 15, 2)
def clear_screen():
   for x in range(0,32):
       for y in range(0,16):
           screen[y][x] = 0

def fill_line(x1, y1, x2, y2, color):
   if abs(y2-y1)<abs(x2-x1):
       dydx = (y2 - y1)*1.0 / (x2 - x1)
       for x in range(x1, x2+1):
           screen[y1 + int(dydx*(x-x1))][x] = color
   else:
       dxdy = (x2 - x1)*1.0 / (y2 - y1)
       for y in range(y1,y2+1):
           screen[y][x1+int(dxdy*(y-y1))] = color

def num_three(color):
   screen[2][12] = color
   screen[13][12] = color
   fill_line(13,1,18,1,color)
   fill_line(12,8,18,8,color)
   fill_line(13,14,18,14,color)
   fill_line(19,2,19,13,color)
   screen[8][19] = 0

def num_two(color):
    screen[3][12] = color
    screen[2][13] = color
    screen[3][19] = color
    screen[2][18] = color
    screen[4][19] = color
    fill_line(14,1,17,1,color)
    fill_line(19,5,12,14,color)
    fill_line(12,14,19,14,color)

def num_one(color):
   fill_line(16,1,16,14,color)
   fill_line(16,1,14,3,color)

def ltr_win(color):
   # w
   fill_line(3,1,6,14,color)
   fill_line(9,2,6,14,color)
   fill_line(9,2,12,14,color)
   fill_line(15,1,12,14,color)
   #i
   fill_line(18,1,18,14,color)
   fill_line(17,1,19,1,color)
   fill_line(17,14,19,14,color)
   #n
   fill_line(21,1,21,14,color)
   fill_line(28,1,28,14,color)
   fill_line(21,1,28,14,color)

def ltr_lose(color):
   #l
   fill_line(1,1,1,14,color)
   fill_line(1,14,6,14,color)
   #o
   fill_line(7,3,7,12,color)
   fill_line(13,3,13,12,color)
   fill_line(9,1,11,1,color)
   screen[2][8] = color
   screen[2][12] = color
   screen[13][8] = color
   screen[13][12] = color
   fill_line(9,14,11,14,color)
   #s
   fill_line(17,1,19,1,color)
   screen[2][16] = color
   screen[2][20] = color
   screen[3][21] = color
   screen[12][15] = color
   screen[13][16] = color
   screen[13][20] = color
   screen[12][21] = color
   fill_line(17,14,19,14,color)
   fill_line(17,1,18,1,color)
   fill_line(17,14,18,14,color)
   fill_line(15,3,15,4,color)
   fill_line(15,4,21,11,color)
   #e
   fill_line(23,1,23,14,color)
   fill_line(23,1,28,1,color)
   fill_line(23,8,28,8,color)
   fill_line(23,14,28,14,color)

def ltr_draw(color):
    #d
    fill_line(1,2,1,13,color)
    fill_line(5,7,5,9,color)
    fill_line(2,2,5,6,color)
    fill_line(5,10,2,13,color)
    #r
    fill_line(7,2,7,13,color)
    fill_line(8,8,11,13,color)
    screen[2][8] = color
    screen[2][9] = color
    screen[7][8] = color
    screen[7][9] = color
    screen[3][10] = color
    screen[6][10] = color
    screen[4][11] = color
    screen[5][11] = color
    #a
    fill_line(16,2,13,13,color)
    fill_line(16,2,19,13,color)
    fill_line(14,8,18,8,color)
    #w
    fill_line(21,2,23,13,color)
    fill_line(25,2,23,13,color)
    fill_line(25,2,27,13,color)
    fill_line(29,2,27,13,color)

def rock(color):
    fill_line(10,15,20,15,color)
    fill_line(6,10,9,15,color)
    fill_line(23,10,20,15,color)
    fill_line(6,9,13,5,color)
    fill_line(13,5,15,7,color)
    fill_line(11,10,15,7,color)
    fill_line(8,3,8,7,color)
    fill_line(12,3,12,5,color)
    fill_line(16,3,16,8,color)
    fill_line(20,3,20,8,color)
    fill_line(24,3,24,8,color)
    fill_line(9,2,11,2,color)
    fill_line(13,2,15,2,color)
    fill_line(17,2,19,2,color)
    fill_line(21,2,23,2,color)
    fill_line(21,9,23,9,color)
    fill_line(17,9,19,9,color)
    fill_line(13,9,15,9,color)

def scissors(color):
    fill_line(12,15,20,15,color)
    fill_line(9,11,11,15,color)
    fill_line(22,12,20,15,color)
    fill_line(9,11,15,7,color)
    fill_line(15,7,17,9,color)
    fill_line(16,9,13,12,color)
    fill_line(9,2,11,9,color)
    fill_line(9,2,12,1,color)
    fill_line(12,2,15,9,color)
    fill_line(17,1,15,9,color)
    fill_line(17,1,20,2,color)
    fill_line(20,2,18,7,color)
    fill_line(16,9,16,12,color)
    fill_line(19,9,19,12,color)
    fill_line(22,9,22,12,color)
    fill_line(17,8,18,8,color)
    fill_line(20,8,21,8,color)
    fill_line(17,13,18,13,color)
    fill_line(20,13,21,13,color)

def paper(color):
    fill_line(12,15,21,15,color)
    fill_line(6,8,12,15,color)
    fill_line(25,7,21,15,color)
    fill_line(8,6,6,8,color)
    fill_line(8,6,10,10,color)
    fill_line(10,3,11,10,color)
    fill_line(11,2,12,2,color)
    fill_line(13,3,14,9,color)
    fill_line(14,2,14,9,color)
    fill_line(15,1,16,1,color)
    fill_line(17,2,17,9,color)
    fill_line(18,3,17,9,color)
    fill_line(19,2,20,2,color)
    fill_line(21,3,20,10,color)
    fill_line(23,5,21,10,color)
    fill_line(23,5,25,6,color)

def score_bar(win,lose,draw):
    total = win+lose+draw
    wcolor = 4  #blue
    lcolor = 1  #red
    dcolor1 = 7  #pink
    dcolor2 = 5  #pink
    if total==0:
        #win
        fill_line(6,1,7,4,wcolor)
        fill_line(7,4,8,1,wcolor)
        fill_line(8,1,9,4,wcolor)
        fill_line(10,1,9,4,wcolor)

        #lose
        fill_line(15,1,15,4,lcolor)
        fill_line(15,4,18,4,lcolor)

        #draw
        fill_line(23,1,23,4,dcolor1)
        fill_line(23,1,25,1,dcolor1)
        fill_line(23,4,25,4,dcolor1)
        screen[2][26] = dcolor2
        screen[3][26] = dcolor2
    else :



        wbar = int(round(win * 1.0 / total * 15))
        lbar = int(round(lose * 1.0 / total * 15))
        dbar = int(round(draw * 1.0 / total *15))

        #win
        fill_line(6,1,7,4,wcolor)
        fill_line(7,4,8,1,wcolor)
        fill_line(8,1,9,4,wcolor)
        fill_line(10,1,9,4,wcolor)
        fill_rectangle(6,16 - wbar,12,16,wcolor)

        #lose
        fill_line(15,1,15,4,lcolor)
        fill_line(15,4,18,4,lcolor)
        fill_rectangle(14,16 - lbar,20,16,lcolor)

        #draw
        fill_line(23,1,23,4,dcolor1)
        fill_line(23,1,25,1,dcolor1)
        fill_line(23,4,25,4,dcolor1)
        screen[2][26] = dcolor1
        screen[3][26] = dcolor1
        fill_rectangle(22,16 - dbar,28,16,dcolor2)

class CameraClass:
    def __init__(self):
        self._running = True
        self.cap=None
    def terminate(self):

        self.cap.release()
        self._running = False

    def removeBG(self,bgModel,frame):
        fgmask = bgModel.apply(frame,learningRate=learningRate)
        #kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        #fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

        kernel = np.ones((2, 2), np.uint8)
        fgmask = cv2.erode(fgmask, kernel, iterations=1)
        res = cv2.bitwise_and(frame, frame, mask=fgmask)
        return res

    def calculateFingertip(self,res):  # -> finished bool, cnt: finger count
        #  convexity defect
        hull = cv2.convexHull(res, returnPoints=False)
        if True:
        #if len(hull) > 3:
            defects = cv2.convexityDefects(res, hull)
            if type(defects) != type(None):  # avoid crashing.   (BUG not found)

                cnt = 0

                start_list=[]
                end_list=[]

                dis_thr = 80.0
                for i in range(defects.shape[0]):  # calculate the angle
                    s, e, f, d = defects[i][0]
                    start = tuple(res[s][0])
                    end = tuple(res[e][0])
                    far = tuple(res[f][0])
                    a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)

                    b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                    c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)


                    angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))  # cosine theorem
                    if angle <= math.pi / 2.0 and b> dis_thr and c > dis_thr :  # angle less than 90 degree, treat as fingers

                        #print(str(b)+" "+str(c))
                        cnt += 1
                        #cv2.circle(drawing_loc, start, 8, [0, 0, 255], -1)

                        #cv2.circle(drawing_loc, end, 8, [0, 255, 0], -1)
                        #cv2.circle(drawing_loc, far, 8, [211, 84, 0], -1)

                        #print("angle = "+str(angle))
                        #print("b = "+str(b))
                        #print("c = "+str(c))

                        start_list.append(start)
                        end_list.append(end)

                #start_list.sort(key=takeSecond)
                #end_list.sort(key=takeFirst)

                # for start point take first 5th above
                #if count%10==0:


                return cnt



    def run(self):
        global cycle,ret,frame,delay
        global start
        global player
        sum=0
        cnt_sum=0

        self.cap=cv2.VideoCapture(-1)
        cv2.startWindowThread()
        cv2.namedWindow("camera")
        while self._running:
            ret,frame=self.cap.read()
            cv2.imshow("camera",frame)

            if start==2:
                bgModel = cv2.createBackgroundSubtractorMOG2(200, bgSubThreshold)
                img_removebg = self.removeBG(bgModel,frame)
                img = img_removebg



                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


                # convert it to the HSV color space,
        	    # and determine the HSV pixel intensities that fall into
        	    # the speicifed upper and lower boundaries
                hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                #cv2.imshow("hsv",hsv)

                skinMask = cv2.inRange(hsv, skin_lower, skin_upper)
                skinMask = cv2.erode(skinMask, None, iterations=1)
                skinMask = cv2.dilate(skinMask, None, iterations=1)

                #cv2.imshow("skinMask",skinMask)



                blur = cv2.GaussianBlur(skinMask, (blurValue, blurValue), 0)

                #cv2.imshow('blur', blur)
                ret, thresh = cv2.threshold(skinMask, threshold, 255, cv2.THRESH_BINARY)
                #cv2.imshow('ori', thresh)


                #cv2.imshow('ori_right', thresh_right)

                # get the coutours
                thresh1 = copy.deepcopy(thresh)
                _,contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)



                length = len(contours)
                maxArea = -1



                if length > 0:
                    res = max(contours, key=cv2.contourArea)
                    cnt = self.calculateFingertip(res)
                    sum+=cnt
                    cnt_sum+=1
                    if cnt_sum%10==0:
                        finger=sum/10
                        print("finger = "+str(finger))

                        if finger==0:
                            player=-1
                        elif finger==1:
                            player=0
                        elif finger<=3:
                            player=2
                        else :
                            player=1
                        sum=0
                        cnt_sum=0

            else:
                sum=0
                cnt_sum=0

            time.sleep(delay)



class ButtonClass:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def button_check(self):
        global button_pin_b,button_pin_y,button_pin_r
        global button_val_b,button_val_y,button_val_r
        if GPIO.input(button_pin_b)==GPIO.HIGH:
            button_val_b=True
        else:
            button_val_b=False

        if GPIO.input(button_pin_y)==GPIO.HIGH:
            button_val_y=True
        else:
            button_val_y=False

        if GPIO.input(button_pin_r)==GPIO.HIGH:
            button_val_r=True

        else:

            button_val_r=False

    def judge(self):
        global player,com

        # 0 = Rock,1 = Paper,2=Scissors
        if com==0:
            if player == 1:
                return "Win"
            elif player ==2:
                return "Lose"
            elif player ==0:
                return "Draw"
        elif com==1:
            if player == 2:
                return "Win"
            elif player ==0:
                return "Lose"
            elif player ==1:
                return "Draw"
        elif com==2:
            if player == 0:
                return "Win"
            elif player ==1:
                return "Lose"
            elif player ==2:
                return "Draw"

    def run(self):
        global score_flag
        global sound_win,sound_lose,sound_draw
        global cnt_win,cnt_lose,cnt_draw
        global screen
        global start
        global player,com
        global cycle
        global button_val
        button_delay=1000
        button_delay2=1500
        count_game=0
        count=0

        winner=None
        while self._running:
            if count>=button_delay:
                self.button_check()
                if button_val_b and button_val_y:
                    print("Start Game")
                    score_flag=False
                    start=1
                    count=0
                    count_game=0
                    player=-1

                elif button_val_y and button_val_r:
                    #reset score

                    if start==-1:
                        score_flag=False
                        clear_screen()
                        print("Reset Score")
                        cnt_win=0
                        cnt_lose=0
                        cnt_draw=0
                        count=0

                elif button_val_b and button_val_r:
                    #print score

                    if start==-1:
                        if score_flag==False:
                            print("Print Score")
                            score_flag=True
                            score_bar(cnt_win,cnt_lose,cnt_draw)
                            print("win = "+str(cnt_win))
                            print("lose = "+str(cnt_lose))
                            print("draw = "+str(cnt_draw))
                        elif score_flag==True:
                            score_flag=False
                            clear_screen()
                        count=0


                elif button_val_b:
                    if start==2:

                        print("blue")
                        count=0
                        player=0
                        count_game=button_delay*3


                elif button_val_r:
                    if start==2:

                        print("red")
                        count=0
                        player=1
                        count_game=button_delay*3

                elif button_val_y:
                    if start==2:

                        print("yellow")
                        count=0
                        player=2
                        count_game=button_delay*3



            if start==1:
                if count_game==0:
                    #3
                    clear_screen()
                    num_three(6)

                    #fill_rectangle(20, 4, 30, 15, 2)

                elif count_game==button_delay:
                    #2
                    clear_screen()
                    num_two(7)

                    #fill_rectangle(15, 0, 19, 7, 7)

                elif count_game==button_delay*2:
                    #1
                    clear_screen()
                    num_one(1)

                    #fill_rectangle(0, 0, 12, 12, 1)
                    count_game=0
                    start=2
            if start==2:
                if count_game==button_delay2:
                    clear_screen()
                    #wait for push button
                if count_game==button_delay2*4:
                    #start janken
                    if player==-1:
                        count_game=-1
                        start=1
                        print("Please push button at the end of 3 2 1")
                    else:
                        com=random.randint(0,2)
                        print("com = "+str(com))
                        print("player = "+str(player))

                        winner = self.judge()
                        count_game=-1
                        start=3
            if start==3:
                if count_game==button_delay:
                    #print com's hand
                    if com==0:
                        #Rock
                        clear_screen()
                        rock(1)
                    elif com==1:
                        #Paper
                        clear_screen()
                        paper(4)
                    elif com==2:
                        #Scissors
                        clear_screen()
                        scissors(5)

                elif count_game==button_delay*2:
                    # print Win / Lose / Draw
                    clear_screen()
                    if winner=="Win":
                        cnt_win+=1
                        sound_win=True
                        ltr_win(3)
                    elif winner=="Lose":
                        cnt_lose+=1
                        ltr_lose(4)
                    elif winner=="Draw":
                        cnt_draw+=1
                        ltr_draw(5)


                    print(winner)
                elif count_game==button_delay*3:

                    clear_screen()
                    start=-1
                    count_game=-1


            count+=1
            #print("count = "+str(count))
            #print("start = "+str(start))
            if start>=1:
                count_game+=1

            if count>button_delay*10:
                count=button_delay
            time.sleep(delay)

class SoundClass:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self):
        pygame.mixer.init()
        sound_win= pygame.mixer.Sound("win.wav")
        while self._running:
            if sound_win==True:
                play_chord.play(loops=0)
                sound_win==False

            time.sleep(delay)



class LightClass:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False
        clear_screen()
        self.refresh()

    def clock(self):
        GPIO.output(clock_pin, 1)
        GPIO.output(clock_pin, 0)

    def latch(self):
        GPIO.output(latch_pin, 1)
        GPIO.output(latch_pin, 0)

    def bits_from_int(self,x):
        a_bit = x & 1
        b_bit = x & 2
        c_bit = x & 4
        return (a_bit, b_bit, c_bit)

    def set_row(self,row):
        #time.sleep(delay)
        a_bit, b_bit, c_bit = self.bits_from_int(row)
        GPIO.output(a_pin, a_bit)
        GPIO.output(b_pin, b_bit)
        GPIO.output(c_pin, c_bit)
        #time.sleep(delay)

    def set_color_top(self,color):
        #time.sleep(delay)
        red, green, blue = self.bits_from_int(color)
        GPIO.output(red1_pin, red)
        GPIO.output(green1_pin, green)
        GPIO.output(blue1_pin, blue)
        #time.sleep(delay)

    def set_color_bottom(self,color):
        #time.sleep(delay)
        red, green, blue = self.bits_from_int(color)
        GPIO.output(red2_pin, red)
        GPIO.output(green2_pin, green)
        GPIO.output(blue2_pin, blue)
        #time.sleep(delay)

    def refresh(self):
        global delay
        global screen
        global red1_pin,green1_pin,blue1_pin,red2_pin,green2_pin,blue2_pin,clock_pin,a_pin,b_pin,c_pin,latch_pin,oe_pi,button_pin
        for row in range(8):
            GPIO.output(oe_pin, 1)
            self.set_color_top(0)
            self.set_row(row)
            #time.sleep(delay)
            for col in range(32):
                self.set_color_top(screen[row][col])
                self.set_color_bottom(screen[row+8][col])
                self.clock()
            #GPIO.output(oe_pin, 0)
            self.latch()
            GPIO.output(oe_pin, 0)
            time.sleep(delay)

    def run(self):
        global cycle
        global button_val
        while self._running:
            self.refresh()





#Create Class
Camera = CameraClass()
#Create Thread
CameraThread = Thread(target=Camera.run)
#Start Thread
CameraThread.start()


#Create Class
Button = ButtonClass()
#Create Thread
ButtonThread = Thread(target=Button.run)
#Start Thread
ButtonThread.start()

#Create Class
Light = LightClass()
#Create Thread
LightThread = Thread(target=Light.run)
#Start Thread
LightThread.start()



#Create Class
#Sound = SoundClass()
#Create Thread
#SoundThread = Thread(target=Sound.run)
#Start Thread
#SoundThread.start()

global file
file = open("score.txt", "r")
cnt_win=int(file.readline())
cnt_lose=int(file.readline())
cnt_draw=int(file.readline())

Exit = False #Exit flag
while Exit==False:
    a=raw_input()
    if a=='q':
        Camera.terminate()
        Light.terminate()
        #Sound.terminate()
        Button.terminate()
        cv2.destroyAllWindows()
        file_out=open("score.txt", "w")
        file_out.write("%d\n" % cnt_win)
        file_out.write("%d\n" % cnt_lose)
        file_out.write("%d\n" % cnt_draw)
        Exit=True
print "Goodbye :)"
