import cv2
import numpy as np
import pyautogui
import pygetwindow as gw
import keyboard


# Load the is_fishing image
IS_FISHING = cv2.imread('is_fishing.png', cv2.IMREAD_COLOR)

# Load the is_reeling image
IS_REELING = cv2.imread('is_reeling.png', cv2.IMREAD_COLOR)

# Load the relaxed_fish image
RELAXED_FISH = cv2.imread('relaxed_fish.png', cv2.IMREAD_COLOR)

# Load the stressed_fish image
STRESSED_FISH = cv2.imread('stressed_fish.png', cv2.IMREAD_COLOR)

# Load the hooked image
HOOKED = cv2.imread('hooked.png', cv2.IMREAD_GRAYSCALE)

# Load the bobble image
BOBBLE = cv2.imread('bobble.png', cv2.IMREAD_COLOR)

# you can access the height an width using IMAGE.shape.h and IMAGE.shape.w

def match_template(image, template, threshold=0.85):
    # Match the template to the image
    res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    
    # Find all locations where the result is at least as good as the threshold
    loc = np.where(res >= threshold)
    
    matched = False
    
    # Draw a rectangle around the matched region
    for pt in zip(*loc[::-1]):  # Switch x and y coordinates
        cv2.rectangle(image, pt, (pt[0] + template.shape[1], pt[1] + template.shape[0]), (0, 255, 0), 1)
        
        matched = True
        
    return matched


def cast():
    # Cast the fishing rod by holding down the right mouse button for 1.5 second and then releasing it
    pyautogui.mouseDown(button='right')
    pyautogui.sleep(1.5)
    pyautogui.mouseUp(button='right')
    print('casting')
    pyautogui.sleep(1.5)
    print('waiting for ripples to clear')


def fish_on():
    pyautogui.mouseDown(button='right')
    pyautogui.mouseUp(button='right')
    pyautogui.sleep(.5)
    print('fish on!')
    
    
def reel():
    # Reel in the fishing rod by holding down the right mouse button when the fish is in a relaxed state
    pyautogui.mouseDown(button='right')
    pyautogui.sleep(0.1)
    print('reeling')
    

def release():
    pyautogui.mouseUp(button='right')
    print('releasing')
    

if __name__ == '__main__':
    fishing = False;
    printed_start_fishing = False;
    printed_not_fishing = False;
    printed_fighting = False;
    printed_not_fighting = False;
    is_reeling = False;
    fish_is_on = False;
    
    while True:
        target_window = gw.getWindowsWithTitle("Core Keeper")[0]

        if target_window and fishing:
            if not printed_start_fishing:
                print('Start Fishing')
                printed_start_fishing = True
                printed_not_fishing = False
                
            # Extract the bounding box's properties
            left, top, width, height = target_window._rect.left, target_window._rect.top, target_window._rect.width, target_window._rect.height

            # Capture the screenshot for the specified region
            screenshot = pyautogui.screenshot(region=(left, top, width, height))

            # Convert the screenshot to a numpy array
            image_np = np.array(screenshot)

            # Convert RGB to BGR (OpenCV uses BGR format)
            image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            gray_image = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)

            # Match the fishing template to the screenshot
            is_fishing = match_template(image_cv, IS_FISHING, .85)
            is_reeling = match_template(image_cv, IS_REELING, .85)

            if not is_fishing and not is_reeling: # If currently not fighting a fish
                if not printed_not_fighting:
                    print('Not fighting a fish')
                    printed_not_fighting = True
                    printed_fighting = False
                    
                is_hooked = match_template(gray_image, HOOKED, .85)
                has_bobble = match_template(image_cv, BOBBLE, .85)
                
                print('is_hooked: ' + str(is_hooked))
                print('has_bobble: ' + str(has_bobble))
                
                if is_hooked:
                    fish_on()
                    fish_is_on = True;
                elif not has_bobble and not fish_is_on: # If currently there's no bobble, cast
                    cast()
            else: # If currently fighting a fishing
                if not printed_fighting:
                    print('Fighting a fish')
                    printed_fighting = True
                    printed_not_fighting = False
                    fish_is_on = False
                is_relaxed = match_template(image_cv, RELAXED_FISH, .475)
                is_stressed = match_template(image_cv, STRESSED_FISH, .475)
                
                print('is_relaxed: ' + str(is_relaxed))
                print('is_stressed: ' + str(is_stressed))
                
                if is_relaxed and not is_reeling:
                    reel()
                    is_reeling = True
                elif is_stressed:
                    release()
                    is_reeling = False
                else:
                    pyautogui.sleep(0.1)
        else:
            if not printed_not_fishing:
                print('Not Fishing')        
                printed_not_fishing = True
                printed_fishing = False

        # Add a way to start and stop fishing by pressing 'q'
        if keyboard.is_pressed('5'):
            print('Not fishing anymore' if fishing else 'Started fishing')
            fishing = not fishing
