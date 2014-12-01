from __future__ import division
import time

from numpy import sqrt
from pymouse import PyMouse
from pykeyboard import PyKeyboard

def drag(source, dest, speed=1000):
    """
    Simulates a smooth mouse drag

    Args:
        source (int, int) : location (x,y) to start the drag, in screen 
            coordinates
        dest (int, int) : location (x,y) to end the drag, in screen 
            coordinates
        speed (int) : rate at which to execute the drag, in pixels/second
    """
    m = PyMouse()
    m.press(*source)

    time.sleep(0.1)

    # number of intermediate movements to make for our given speed
    npoints = int(sqrt((dest[0]-source[0])**2 + (dest[1]-source[1])**2 ) / (speed/1000))
    for i in range(npoints):
        x = int(source[0] + ((dest[0]-source[0])/npoints)*i)
        y = int(source[1] + ((dest[1]-source[1])/npoints)*i)
        m.move(x,y)
        time.sleep(0.001)

    m.release(*dest)

def click(point):
    """
    Simulates a mouse click

    Args:
        point (int,int) : location (x,y) of the screen to click
    """
    m = PyMouse()
    m.move(*point)
    m.press(*point)
    m.release(*point)

def doubleclick(point):
    """
    Simulates a mouse double click

    Args:
        point (int, int): location (x,y) of the screen to click
    """
    m = PyMouse()
    m.press(*point)
    m.release(*point)
    m.press(*point)
    m.release(*point)

def move(point):
    """
    Moves the mouse cursor to the provided location

    Args:
        point (int, int): location (x,y) of the screen to place the cursor
    """
    # wrapper just so we don't have to import pymouse separately
    m = PyMouse()
    m.move(*point)

def keypress(key):
    """
    Simulates a key press

    Args:
        key (str) : the key [a-zA-Z0-9] to enter. Use 'enter' for the 
            return key
    """
    k = PyKeyboard()
    if key == 'enter':
        key = k.return_key
    k.tap_key(key)

def type_msg(string):
    """
    Stimulates typing a string of characters

    Args:    
        string (str) : A string of characters to enter
    """
    k = PyKeyboard()
    k.type_string(string)

def wheel(ticks):
    """
    Simulates a mouse wheel movement

    Args:
        ticks (int) : number of increments to scroll the wheel
    """
    m = PyMouse()
    m.scroll(ticks)

def key_combo(key0, key1):
    k = PyKeyboard()
    if key0 == 'ctrl':
        key0 = k.control_key
    k.press_key(key0)
    k.tap_key(key1)
    k.release_key(key0)