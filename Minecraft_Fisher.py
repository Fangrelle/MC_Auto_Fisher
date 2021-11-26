from PIL import Image
import numpy as np
from skimage import io
from skimage.color import rgb2lab, deltaE_cie76, rgb2grey, label2rgb
from skimage.measure import label, regionprops
import keyboard
import mouse
from PIL import ImageGrab
import time
import pyautogui

# Helper function
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)

''' Variables '''

# mid = 960, 540
# 400 x 400
og_box = (760,340,1160,740)

# 200 x 200
#bbox = (860,440,1060,640)

bbox = og_box

bb_center = [(bbox[0] + bbox[2]) / 2,(bbox[1] + bbox[3]) / 2]

casting = 5

zoom_amount = 5

zoom_times = 0

print_output = True

def run_fishing_detection (casting, bbox, zoom_times):

    casting -= 1
    
    # Wait
    if casting > 0:
        print("Casting: ",casting)
        time.sleep(0.1)
        return casting, bbox, zoom_times

    #print(bbox)
    #Cap screen
    image_np = ImageGrab.grab(bbox)

    # Array of rgb colors
    rgb = load_image_into_numpy_array(image_np)
    
    img = rgb

    lab = rgb2lab(rgb)

    # color & threshold
    bobber_red = [200,25,25]

    threshold_fishing = 40

    #replace_colour = [[[0,0,0]]]
    replace_colour = [[[255,255,255]]]

    # bobber thresholding

    bobber_3d = np.uint8(np.asarray([[bobber_red]]))

    dE_bobber = deltaE_cie76(rgb2lab(bobber_3d), lab)

    rgb[dE_bobber > threshold_fishing] = replace_colour

    # grey version
    grey = rgb2grey(rgb)

    # only black parts
    thres_img = np.empty_like(grey)
    thres_img[grey == 1] = 0
    thres_img[grey < 1] = 1

    # label parts
    label_image = label(thres_img,connectivity = 2,background = 0)
    
    io.imsave("output_img.jpg",img)

    image_label_overlay = label2rgb(label_image, image=img)
    
    
    # Region
    big_region = {"area" : 0, "bbox" : (0,0,0,0), "center" : (0,0)}
    
    # Region/Label analysis
    for region in regionprops(label_image):
        if region.area <= 2000: #and region.area < 600 and region.extent >= 0.5:
        
            # region bounding box
            minr, minc, maxr, maxc = region.bbox
            bbox_ = [minc,minr,maxc,maxr]
            
            # center
            center = region.centroid
            
            # get biggest area region
            if region.area > big_region["area"]:
                big_region["area"] = region.area
                big_region["bbox"] = bbox_
                big_region["center"] = center
                
    
    # Control
    
    # Found bobber
    if big_region["area"] > 0:
        print("Found bobber")
        center = big_region["center"]
        #time.sleep(0.1)
        #xypos = print((center[1],center[0]))
        
        # Move mouse to position (remember bbox coords are relatice to the entire sceen)
        mouse.move(center[1] + bbox[0],center[0] + bbox[1],absolute=True,duration=0)
        time.sleep(0.5)
        
        # Resize bbox to shrink around the bobber
        # real x coords: bbox[0] + big_region["bbox"][0] = real coord of that coord
        # Only resize/zoom a certain number of times
        if zoom_times < zoom_amount:
            zoom_times += 1
            bbox = (bbox[0] + (big_region["bbox"][0] / 2),bbox[1] + (big_region["bbox"][1] / 2),((bbox[0] + big_region["bbox"][2]) + bbox[2]) / 2, ((bbox[1] + big_region["bbox"][3]) + bbox[3]) / 2 )
            print("Zoomed in: ", zoom_times,"/",zoom_amount)
            # Save image
            if zoom_times == 3 and print_output:
                print("Printing")
                io.imsave("output.jpg",image_label_overlay)
        
        
        
    
    # If no bobber, recast
    else:
        print("-- Recasting --")
        
        # Pull rell in, Catch fish
        print("- Pulls in -")
        mouse.click(button='right')
        casting = 5
        time.sleep(2)
        
        # Wait and recast
        print("- Throws -")
        mouse.click(button='right')
        time.sleep(3)
        
        # Resize bbox to original size
        bbox = og_box
        
        # Reset zoom number
        zoom_times = 0

    return casting, bbox, zoom_times#, bb_center
    
    # Save image
    #io.imsave("output.jpg",image_label_overlay)


time.sleep(0.1)
mouse.click(button='left')
time.sleep(1)

# First throw
mouse.click(button='right')
time.sleep(4)

for i in range(10000):
    casting, bbox, zoom_times = run_fishing_detection(casting, bbox, zoom_times) #, bb_center



