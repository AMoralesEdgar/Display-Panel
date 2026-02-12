# CircularListWidget for PyQt5
# Edgar Abarca Morales
from PyQt5 import QtCore, QtWidgets
# Before I used QtGui instead of QtWidgets, but QtGui is now deprecated

# Upgrade QtGui.QListWidget to support infinite arrow scrolling
class CircularListWidget(QtWidgets.QListWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, event):

        # Circular scrolling behaviour
        if event.key() == QtCore.Qt.Key_Down:
            if self.currentRow() == self.count()-1:
                self.setCurrentRow(0)
                return
        elif event.key() == QtCore.Qt.Key_Up:
            if self.currentRow() == 0:
                self.setCurrentRow(self.count()-1)
                return

        # Parent behavior
        super().keyPressEvent(event)
