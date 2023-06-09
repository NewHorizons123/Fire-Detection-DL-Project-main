import os
import random

import cv2
import numpy as np
import smtplib
import playsound
import threading
import requests
from geopy.geocoders import Nominatim


Alarm_Status = False
Email_Status = False
Fire_Reported = 0
Image_Status = False
count = 0

toaddr = "maltegoforensic@gmail.com"
fromaddr = "adilmemon2022@gmail.com"
password = "Generic@#$12345"




def send_mail_function():
    recipientEmail = "adilmemon2022@gmail.com"

    recipientEmail = recipientEmail.lower()
    toaddr = "maltegoforensic@gmail.com"
    fromaddr = "adilmemon2022@gmail.com"
    password = "Generic@#$12345"

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login("adilmemon2022@gmail.com", "Generic@#$12345")
        msg = str(get_loc())

        server.sendmail("adilmemon2022@gmail.com", recipientEmail,
                        "Warning! A Fire Accident has been reported on " + msg)
        print("sent to {}".format(recipientEmail))
        server.close()


    except Exception as e:
        print(e)


video = cv2.VideoCapture(0) 

while True:
    (grabbed, frame) = video.read()
    if not grabbed:
        break
    frame = cv2.resize(frame, (960, 540))  # (960, 540)

    blur = cv2.GaussianBlur(frame, (21, 21), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    yCrCb = cv2.cvtColor(blur, cv2.COLOR_BGR2YCR_CB)

    lower = [18, 74, 200]  # [18, 40, 90] [18,74,200]
    upper = [35, 170, 255]  # [35, 255, 255] [35,170,255]
    y_lower = [0, 33.33, 88.63, 0.00]
    y_upper = [0, 84.47, 80.10, 19.22]
    lower = np.array(lower, dtype="uint8")
    upper = np.array(upper, dtype="uint8")

    mask = cv2.inRange(hsv, lower, upper)

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:

        area = cv2.contourArea(cnt)
        # print(area)

        if (area > 13000):
            cv2.drawContours(frame, [cnt], -1, (0, 0, 255), 2)
            x, y, w, h = cv2.boundingRect(cnt)

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Fire:", (x + w, y + h), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.rectangle(mask, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(mask, "Fire:", (x + w, y + h), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    output = cv2.bitwise_and(frame, hsv, mask=mask)
    no_red = cv2.countNonZero(mask)

    if int(no_red) > 13000:
        Fire_Reported = Fire_Reported + 1

    cv2.imshow("Video", frame)
    cv2.imshow("HSV", hsv)
    #cv2.imshow("Mask", mask)

    if Fire_Reported >= 1:
        if Alarm_Status == False:
            threading.Thread(target=play_alarm_sound_function).start()
            Alarm_Status = True

        if Image_Status == False:
            if (area >= 6000):
                count = random.random()
                file_name = str("images/detected/file" + str(count) + ".jpg")
                cv2.imwrite(file_name, frame)
                Image_Status = True

        if Email_Status == False:
            threading.Thread(target=send_mail_function).start()
            #SendMail(file_name)
            Email_Status = True

    # if cv2.waitKey(1) & 0xFF == ord("q"):
    # break
    key = cv2.waitKey(10)
    if (key == 27):
        break
cv2.destroyAllWindows()
video.release()
