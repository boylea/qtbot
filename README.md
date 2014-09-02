qtbot
=====

Simple test utility for simulating interaction with PyQt widgets.

Spawned out of a lack of ability to test drag-and-drop functionality with QTest. Uses PyUserInput to control the mouse and keyboard Instead of QTest, while using widgets as input to determine how to navigate the screen interaction.

Works on at least Windows 7 and Fedora.

Example usage:

    from PyQt4 import QtGui
    import qtbot

    app = QtGui.QApplication([])
    dlg = QtGui.QFileDialog()
    fname = '/foo/bar'
    qtbot.handle_modal_widget(fname, wait=False)
    dlg.exec_()
    assert fname == dlg.selectedFiles()[0];