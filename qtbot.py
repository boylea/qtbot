import threading
import time

from PyQt4 import QtCore, QtGui, QtTest

import robouser

class QObj(QtCore.QObject):
    somethingHappened = QtCore.pyqtSignal()

def center(widget, view_index=None):
    """
    Gets the global position of the center of the widget. If index is
    provided, widget is a view and get the center at the index position

    Args:
        widget (PyQt4.QtGui.QWidget) : widget to get the center location of
        view_index (PyQt4.QtCore.QModelIndex) : index of the item in the widget to get the center location of
    
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
        view_index (PyQt4.QtCore.QModelIndex) : If not None, assumes the given widget is a view, clicks the center of the indexed item in the view
    """
    pos = center(widget, view_index)
    robouser.click(pos)

def doubleclick(widget, view_index=None):
    """
    Simulates a double click at the center of the widget

    Args:
        view_index (PyQt4.QtCore.QModelIndex) : If not None, assumes the given widget is a view, clicks the center of the indexed item in the view
    """
    pos = center(widget, view_index)
    robouser.doubleclick(pos)

def move(widget, view_index=None):
    """
    Moves the mouse cursor to the provided widget

    Args:
        view_index (PyQt4.QtCore.QModelIndex) : If not None, assumes the given widget is a view, clicks the center of the indexed item in the view
    """
    pos = center(widget, view_index)
    robouser.move(pos)

def wheel(ticks):
    """
    Simulates a mouse wheel movement

    Args:
        ticks (int) : number of increments to scroll the wheel
    """
    # wrapper
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
    robouser.keypress(key)

def type(msg):
    """
    Stimulates typing a string of characters

    Args:    
        string (str) : A string of characters to enter
    """
    robouser.type(str(msg))

def drag(src, dest, src_index=None, dest_index=None):
    """
    Simulates a smooth mouse drag from one widget to another

    Args:
        src (PyQt4.QtGui.QWidget) : source widget
        dest (PyQt4.QtGui.QWidget): widget to drag to
        src_index (PyQt4.QtCore.QModelIndex): If not None, assumes src widget is a view, drags from this item at index location 
        dest_index (PyQt4.QtCore.QModelIndex) : If not None, assumes dest widget is a view, drags to this item at index location
    """
    src_pos = center(src, src_index)
    dest_pos = center(dest, dest_index)
    thread = threading.Thread(target=robouser.drag, args=(src_pos, dest_pos))
    thread.start()
    while thread.is_alive():
        QtTest.QTest.qWait(500)

def handle_dialog(wait=False):
    """
    Listens for a top level dialog, and then simulates a return keypress e.g. to close it

    Args:
        wait (bool): whether to (non-blocking) wait until dialog is closed to return
    """
    thread = threading.Thread(target=_close_toplevel)
    thread.start()
    if wait:
        while thread.is_alive():
            QtTest.QTest.qWait(500)

def handle_modal_widget(fpath=None, wait=True, press_enter=True):
    """
    Listens for a modal dialog, and closes it


    :param fpath: string to type in the default focus location of widget
    :type fpath: str
    :param wait: whether to (non-blocking) wait until dialog is closed to return
    :type wait: bool
    :param press_enter: Whether to attempt to close the dialog with a simulated return key press. If False a signal is sent to the accept slot of the modal target widget.
    :type press_enter: bool
    """
    thread = threading.Thread(target=_close_modal, args=(fpath, press_enter))
    thread.start()
    if wait:
        while thread.is_alive():
            QtTest.QTest.qWait(500)

def reorder_view(view, start_idx, end_idx):
    """
    Simulates a smooth mouse drag from one widget to another

    Args:
        view (PyQt4.QtGui.QAbstractItemView): Widget where the dragging will take place
        start_idx (PyQt4.QtCore.QModelIndex): index of item in view to start drag from
        end_idx (PyQt4.QtCore.QModelIndex): index of item in view to drag to
    """
    start_pos = center(view, view.model().index(*start_idx))
    if end_idx[1] > 0:
        prev_idx = (end_idx[0], end_idx[1]-1)
        end_pos = center(view, view.model().index(*prev_idx))
        comp0len = view.visualRect(view.model().index(*prev_idx)).width()
        end_pos = (end_pos[0]+(comp0len/2)+15, end_pos[1])
    else:
        end_pos = 15, view.rowReach()*(0.5*end_idx[0])

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
    robouser.keypress('enter')

def _close_modal(fpath=None, enter=True):
    """
    Endlessly waits for a modal widget, clicks ok button when found. Safe to be run from inside thread.
    
    Args:
        fpath (str) : string to type in the default focus location of widget
    """
    modalWidget = None
    while modalWidget is None:
        modalWidget = QtGui.QApplication.activeModalWidget()
        time.sleep(1)
    if fpath is not None:
        robouser.type(fpath)
    if enter:
        robouser.keypress('enter')
    else:
        # cannot call any slots on widget from inside thread
        obj = QObj()
        obj.somethingHappened.connect(modalWidget.accept)
        obj.somethingHappened.emit()