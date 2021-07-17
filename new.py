import cv2
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

fitToEllipse = False
cap_1 = cv2.VideoCapture(0)#กล้อง
cap_2 = cv2.VideoCapture(1)#กล้อง

time.sleep(2)

fgbg = cv2.createBackgroundSubtractorMOG2()
j_1 = 0 #room1
j_2 = 0 #room2

cred = credentials.Certificate('memoproject-f3d6e-firebase-adminsdk-fr0rq-88aae7a08c.json')
firebase_admin.initialize_app(cred)

db = firestore.client()


def process(contours, fgmask, j, frame, name):
    if contours:

        # List to hold all areas
        areas = []

        for contour in contours:
            ar = cv2.contourArea(contour)
            areas.append(ar)

        max_area = max(areas, default=0)

        max_area_index = areas.index(max_area)

        cnt = contours[max_area_index]

        fall = 0

        M = cv2.moments(cnt)

        x, y, w, h = cv2.boundingRect(cnt)

        cv2.drawContours(fgmask, [cnt], 0, (255, 255, 255), 3, maxLevel=0)

        if h < w:
            j += 1

        if j > 10:
            # print("FALL")
            # cv2.putText(fgmask, 'FALL', (x, y), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (255,255,255), 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            fall = 1

        if h > w:
            j = 0
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)


        #cv2.imshow(name, frame)

        doc_ref = db.collection(u'patient').document(name)

        doc_ref.set({
            u'action': fall
        })







while(1):
    ret, frame_1 = cap_1.read()
    ret, frame_2 = cap_2.read()

    
    #Convert each frame to gray scale and subtract the background

    gray_1 = cv2.cvtColor(frame_1, cv2.COLOR_BGR2GRAY)
    gray_2 = cv2.cvtColor(frame_2, cv2.COLOR_BGR2GRAY)

    fgmask_1 = fgbg.apply(gray_1)
    fgmask_2 = fgbg.apply(gray_2)
        
    #Find contours
    contours_1, _1 = cv2.findContours(fgmask_1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_2, _2 = cv2.findContours(fgmask_2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)



    process(contours_1, fgmask_1, j_1, frame_1, u'room1')
    process(contours_2, fgmask_2, j_2, frame_2, u'room1')



    if cv2.waitKey(33) == 27:
        break





