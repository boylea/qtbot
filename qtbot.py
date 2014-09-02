import threading
import time

from PyQt4 import QtCore, QtGui, QtTest

import robouser

class QObj(QtCore.QObject):
    # For use with sending signals when you don't have a handle on
    # a calling widget
    somethingHappened = QtCore.pyqtSignal()

def center(widget, view_index=None):
    """
    Gets the global position of the center of the widget. If index is
    provided, widget is a view and get the center at the index position

    Args:
        widget (PyQt4.QtGui.QWidget) : widget to get the center location of
        view_index (PyQt4.QtCore.QModelIndex) : index of the item in the widget 
            to get the center location of
    
    Returns:
        (int, int) -- the (x,y) location in screen coordinates
    """
    if view_index is not None:
        # widget is a subclass of QAbstractView
        rect = widget.visualRect(view_index)
        viewport = widget.viewport()
        midpoint = QtCore.QPoint(rect.x() + rect.width()/2, rect.y() + rect.height()/2)
        global_point = viewport.mapToGlobal(midpoint)
    else:
        if isinstance(widget, QtGui.QRadioButton):
            # we want the center of the hit region
            global_point = widget.mapToGlobal(QtCore.QPoint(10,10))
        else:
            midpoint = QtCore.QPoint(widget.width()/2, widget.height()/2)
            global_point = widget.mapToGlobal(midpoint)

    return global_point.x(), global_point.y()


def click(widget, view_index=None):
    """
    Simulates a click at the center of the widget

    Args:
        view_index (PyQt4.QtCore.QModelIndex) : If not None, assumes the given 
            widget is a view, clicks the center of the indexed item in the view
    """
    pos = center(widget, view_index)
    robouser.click(pos)

def doubleclick(widget, view_index=None):
    """
    Simulates a double click at the center of the widget

    Args:
        view_index (PyQt4.QtCore.QModelIndex) : If not None, assumes the given 
            widget is a view, clicks the center of the indexed item in the view
    """
    pos = center(widget, view_index)
    robouser.doubleclick(pos)

def move(widget, view_index=None):
    """
    Moves the mouse cursor to the provided widget

    Args:
        view_index (PyQt4.QtCore.QModelIndex) : If not None, assumes the given 
            widget is a view, clicks the center of the indexed item in the view
    """
    pos = center(widget, view_index)
    robouser.move(pos)

def wheel(ticks):
    """
    Simulates a mouse wheel movement

    Args:
        ticks (int) : number of increments to scroll the wheel
    """
    if ticks < 0:
        increment = -1
    else:
        increment = 1
    # neccessary to space out mouse wheel increments
    for i in range(abs(ticks)):
        robouser.wheel(increment)
        QtTest.QTest.qWait(100)

def keypress(key):
    """
    Simulates a key press

    Args:
        key (str) : the key [a-zA-Z0-9] to enter. Use 'enter' for the return key

    """
    # convert to sting in case number was passed in
    robouser.keypress(str(key))

def type_msg(msg):
    """
    Stimulates typing a string of characters

    Args:    
        string (str) : A string of characters to enter
    """
    # covert to string if not already e.g. number
    msg = str(msg)
    # problems with typing coming out jumbled, so add a pause between each letter
    # also more satisfying watch this way
    for letter in msg:
        robouser.keypress(letter)
        QtTest.QTest.qWait(10)

def drag(src, dest, src_index=None, dest_index=None):
    """
    Simulates a smooth mouse drag from one widget to another

    Args:
        src (PyQt4.QtGui.QWidget) : source widget
        dest (PyQt4.QtGui.QWidget): widget to drag to
        src_index (PyQt4.QtCore.QModelIndex): If not None, assumes src widget is 
            a view, drags from this item at index location 
        dest_index (PyQt4.QtCore.QModelIndex) : If not None, assumes dest widget 
            is a view, drags to this item at index location
    """
    src_pos = center(src, src_index)
    dest_pos = center(dest, dest_index)
    # Use of thread because QDrag blocks event loop, doesn't give mouse
    # release chance to be processed
    thread = threading.Thread(target=robouser.drag, args=(src_pos, dest_pos))
    thread.start()
    while thread.is_alive():
        QtTest.QTest.qWait(500)

def handle_dialog(wait=False):
    """
    Listens for a top level dialog, and then simulates a return keypress 
    e.g. to close it

    Args:
        wait (bool): whether to (non-blocking) wait until dialog is closed to 
            return
    """
    thread = threading.Thread(target=_close_toplevel)
    thread.start()
    if wait:
        while thread.is_alive():
            QtTest.QTest.qWait(500)

def handle_modal_widget(msg=None, wait=True, press_enter=True):
    """
    Listens for a modal dialog, and closes it

    Args:
        msg (str) : string to type in the default focus location of widget
        wait (bool) : whether to (non-blocking) wait until dialog is closed to 
            return
        press_enter (bool): Whether to attempt to close the dialog with a 
            simulated return key press. If False a signal is sent to the accept 
            slot of the modal target widget.
    """
    thread = threading.Thread(target=_close_modal, args=(msg, press_enter))
    thread.start()
    if wait:
        while thread.is_alive():
            QtTest.QTest.qWait(500)

def reorder_view(view, start_idx, end_idx):
    """
    Simulates an internal move drag-and-drop

    Args:
        view (PyQt4.QtGui.QAbstractItemView): Widget where the dragging will 
            take place
        start_idx (int, int): index (row, column) of item in view to start drag
            from
        end_idx (int, int): index (row, column) of item in view to drag to

    Indicies do not need to yet exist, as they may represent the end of a row or 
    column, but cannot be more than one larger than current column count. Assumes 
    static row height, variable column width. views must implement method rowReach 
    returning row span in pixels.
    """
    start_pos = center(view, view.model().index(*start_idx))
    if end_idx[1] > 0:
        # If not first column, go to the right 1 pixel of the previous column's item
        prev_idx = (end_idx[0], end_idx[1]-1)
        end_pos = center(view, view.model().index(*prev_idx))
        comp0len = view.visualRect(view.model().index(*prev_idx)).width()
        end_pos = (end_pos[0]+(comp0len/2)+1, end_pos[1])
    else:
        # views must implement row reach
        end_pos = 1, view.rowReach()*(0.5*end_idx[0])

    # Use of thread because QDrag blocks event loop, doesn't give mouse
    # release chance to be processed
    thread = threading.Thread(target=robouser.drag, args=(start_pos, end_pos))
    thread.start()
    # block return until drag is finished
    while thread.is_alive():
        QtTest.QTest.qWait(500)

def _close_toplevel(cls=QtGui.QDialog):
    """
    Endlessly waits for a QDialog widget, presses enter when found
    
    Args:
        cls : class of the widget to search for
    """
    dialogs = []
    while len(dialogs) == 0:
        topWidgets = QtGui.QApplication.topLevelWidgets()
        dialogs = [w for w in topWidgets if isinstance(w, cls)]
        time.sleep(1)
    # really only works for one dialog (or other widget) found at a time
    robouser.keypress('enter')

def _close_modal(msg=None, enter=True):
    """
    Endlessly waits for a modal widget, enters text (optional) and closes. Safe 
    to be run from inside thread.
    
    Args:
        msg (str) : string to type in the default focus location of widget 
            e.g. filepath in file dialog
        enter (bool) : Whether to attempt to close the dialog with a simulated 
            return key press. If False a signal is sent to the accept slot of 
            the modal target widget.
    """
    # should probably add timeout
    modalWidget = None
    while modalWidget is None:
        modalWidget = QtGui.QApplication.activeModalWidget()
        time.sleep(1)
    if msg is not None:
        type_msg(msg)
    if enter:
        robouser.keypress('enter')
    else:
        # cannot call any slots on widget from inside thread
        obj = QObj()
        obj.somethingHappened.connect(modalWidget.accept)
        obj.somethingHappened.emit()
    print 'DONE'