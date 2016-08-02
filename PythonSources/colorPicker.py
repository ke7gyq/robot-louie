#!/usr/bin/python
# ColorPicker.py. Mouse over something and figure out what clor it is

import cv2

#imgName='roadsigns1.jpg'
#imgName='roadsigns2.jpg'
#imgName='roadsigns3.jpg'
#imgName='roadsigns4.jpg'
imgName="foo.jpg"


range = ((23,235,90),(27,255,170))
kernel = cv2.getStructuringElement( cv2.MORPH_ELLIPSE,(7,7))

bgr = cv2.imread(imgName)
bgr = cv2.resize(bgr, (640,480))
hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, range[0],range[1])
mask = cv2.morphologyEx( mask, cv2.MORPH_CLOSE, kernel )

_,contours,heirarchy= cv2.findContours(mask.copy(),
                           cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cImage = cv2.drawContours(bgr,contours, -1, (0,0,255),2)


# Get images from color areas.
images = list()
for c in contours:
    bb = cv2.boundingRect(c)
    img = mask[bb[1]:bb[1]+bb[3],bb[0]:bb[0]+bb[2]]
    images.append(img)



def getTemplate( inString) :
    print ("inString : %s" % inString)
    img = cv2.imread( inString )
    imGray = cv2.cvtColor( img, cv2.COLOR_BGRA2GRAY)
    _,mask = cv2.threshold( imGray, 100, 255,cv2.THRESH_BINARY)
    mask = cv2.morphologyEx( mask, cv2.MORPH_CLOSE, kernel )
    _,contours,heirarchy = cv2.findContours(mask.copy(),
                                            cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    bb = cv2.boundingRect(contours[0])
    img = mask[bb[1]:bb[1]+bb[3],bb[0]:bb[0]+bb[2]]
    return img

    

# tLeft = getTemplate ( 'smallLeftTurn.png')
# tRight= getTemplate ( 'smallRightTurn.png')
# tUturn= getTemplate ( 'smallHairpinLeft.png')




# templates = (tLeft,tRight,tUturn )

# for t in templates:
#     cv2.imshow ("T", t )
#     for idx, img   in enumerate(images) :
#         cv2.imshow ( 'I_%d' % idx, img)
#         score = cv2.matchShapes ( t, img,2,0.0)
#         print "Score is %f" %score
#     cv2.waitKey(0)




def mouseCallback(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONUP:
        cHSV = hsv[y,x,:]
        print "X,Y %d %d %s " % (x,y, cHSV)
       
        

cv2.imshow ("cImage", cImage)
cv2.imshow ("Mask", mask)
cv2.imshow ("HsvImg", hsv)
cv2.imshow ("InImg", bgr)
cv2.setMouseCallback("InImg", mouseCallback)

while True:
    key = cv2.waitKey(0)
    if key & 0xff == 27:
        break
cv2.destroyAllWindows()


