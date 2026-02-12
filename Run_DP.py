# Run Display Panel
# Edgar Abarca Morales
from PyQt5 import QtWidgets
from pyqt_items.pyqt_WindowItem import WindowItem
from DP import GUI_DisplayPanel
import sys

def Run_DP(files):

    # Create a new app
    app = QtWidgets.QApplication(sys.argv)

    # Create a Display Panel in a WindowItem
    # (See pyqt_WindowItem.py)
    DP = GUI_DisplayPanel(WindowItem())

    # Show the Display Panel
    DP.DisplayPanel.show()

    # Retrieve input files
    DP.GUI_files(files)

    # Run the app main loop
    sys.exit(app.exec_())
