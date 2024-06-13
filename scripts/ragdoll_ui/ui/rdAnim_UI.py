import imp
from pathlib import Path

from PySide2 import QtWidgets, QtCore, QtGui #
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from functools import partial
from maya import OpenMayaUI
# from shiboken2 import wrapInstance

from pymel.core import *
from ragdoll_cmds import ragdoll_default_setting as rdSetting
import ragdoll.commands as rd
from ragdoll import interactive as ri

imp.reload(rdSetting)

_icon_path = f"{Path(__file__).parent.parent}/icons"

class rdAnimUI(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent=parent)
        
        self.setWindowTitle('rdAnimUI')
        
        widget = QtWidgets.QWidget(self)
        widget.setLayout(self.mainView())
        self.setCentralWidget(widget)
        
    
    def mainView(self):
        main_vl = QtWidgets.QVBoxLayout()
        main_hl = QtWidgets.QHBoxLayout()
        
        marker_btn = QtWidgets.QPushButton("", icon=QtGui.QIcon(f"{_icon_path}/select_marker.png"), iconSize=QtCore.QSize(18,18))
        pin_btn = QtWidgets.QPushButton("", icon=QtGui.QIcon(f"{_icon_path}/softpin.png"), iconSize=QtCore.QSize(18,18))
        
        separator1 = QtWidgets.QFrame(styleSheet="background: rgb(50,50,50);", fixedWidth=1)
        separator1.setFrameShape(QtWidgets.QFrame.VLine)
        
        group_btn = QtWidgets.QPushButton("", icon=QtGui.QIcon(f"{_icon_path}/group.png"), iconSize=QtCore.QSize(18,18))
        manipulator_btn = QtWidgets.QPushButton("", icon=QtGui.QIcon(f"{_icon_path}/manipulator.png"), iconSize=QtCore.QSize(18,18))
        
        separator2 = QtWidgets.QFrame(styleSheet="background: rgb(50,50,50);", fixedWidth=1)
        separator2.setFrameShape(QtWidgets.QFrame.VLine)
        
        cache_btn = QtWidgets.QPushButton("", icon=QtGui.QIcon(f"{_icon_path}/bake.png"), iconSize=QtCore.QSize(18,18))
        record_btn = QtWidgets.QPushButton("", icon=QtGui.QIcon(f"{_icon_path}/record.png"), iconSize=QtCore.QSize(18,18))
        
        main_hl.addWidget(marker_btn)
        main_hl.addWidget(separator1)
        main_hl.addWidget(group_btn)
        main_hl.addWidget(manipulator_btn)
        main_hl.addWidget(separator2)
        main_hl.addWidget(pin_btn)
        main_hl.addWidget(cache_btn)
        main_hl.addWidget(record_btn)
        main_vl.addLayout(main_hl)
        
        rdDefault = rdSetting.ragdollDefault()
        
        # CONNECT #
        marker_btn.clicked.connect(partial(rdDefault.selectMarkers))
        pin_btn.clicked.connect(partial(rdDefault.pinSelected))
        group_btn.clicked.connect(ri.group_markers)
        manipulator_btn.clicked.connect(ri.markers_manipulator)
        cache_btn.clicked.connect(partial(rdDefault.autoCache))
        record_btn.clicked.connect(ri.record_markers)
        
        return main_vl