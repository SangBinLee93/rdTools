import imp
from pathlib import Path


from PySide2 import QtWidgets, QtCore, QtGui #
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from functools import partial
from maya import OpenMayaUI
# from shiboken2 import wrapInstance

from pymel.core import *
from bifrost_cmds import cage as cage
from ragdoll_cmds import ragdoll_default_setting as rdSetting
import ragdoll.commands as rd
from ragdoll import interactive as ri

imp.reload(cage)
imp.reload(rdSetting)

_icon_path = f"{Path(__file__).parent.parent}/icons"

class rdRigUI(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent=parent)
        
        self.setWindowTitle('rdRigUI')
        self.setMinimumWidth(300)
        
        widget = QtWidgets.QWidget(self)
        widget.setLayout(self.mainView())
        self.setCentralWidget(widget)

    def mainView(self):
        main_vl = QtWidgets.QVBoxLayout()
        
        ## mesh optimize layout ##
        mesh_layout_gb = QtWidgets.QGroupBox("Mesh Opitimize")
        ###
        mesh_vl = QtWidgets.QVBoxLayout()
        
        ####
        bf_layout_hl = QtWidgets.QHBoxLayout()
        #####
        bf_layout_gl = QtWidgets.QGridLayout()
        
        voxel_size_lb = QtWidgets.QLabel("voxel size :")
        voxel_size_le = QtWidgets.QLineEdit()
        voxel_size_le.setText("0.1")
        
        poly_count_lb = QtWidgets.QLabel("polyCount :")
        poly_count_le = QtWidgets.QLineEdit()
        poly_count_le.setText("5000")
        
        bf_mesh_pb = QtWidgets.QPushButton("", icon=QtGui.QIcon(f"{_icon_path}/bifrost_icon.png"), iconSize=QtCore.QSize(40,40))

        bf_layout_gl.addWidget(voxel_size_lb, 0,0)
        bf_layout_gl.addWidget(voxel_size_le, 0,1)
        bf_layout_gl.addWidget(poly_count_lb, 1,0)
        bf_layout_gl.addWidget(poly_count_le, 1,1)
        
        bf_layout_hl.addLayout(bf_layout_gl)
        bf_layout_hl.addWidget(bf_mesh_pb)
        
        rd_mesh_gl = QtWidgets.QGridLayout()
        match_pb = QtWidgets.QPushButton("", icon=QtGui.QIcon(f"{_icon_path}/match_icon.png"), iconSize=QtCore.QSize(40,40))
        mirrorLr_pb = QtWidgets.QPushButton("", icon=QtGui.QIcon(f"{_icon_path}/LR_icon.png"), iconSize=QtCore.QSize(40,40))
        mirrorM_pb = QtWidgets.QPushButton("", icon=QtGui.QIcon(f"{_icon_path}/M_icon.png"), iconSize=QtCore.QSize(40,40))
        rd_mesh_gl.addWidget(match_pb, 0,0)
        rd_mesh_gl.addWidget(mirrorLr_pb, 0,1)
        rd_mesh_gl.addWidget(mirrorM_pb, 0,2)
        
        bbox_hl = QtWidgets.QHBoxLayout()
        del_mesh_cb = QtWidgets.QCheckBox("del mesh")
        connect_cb = QtWidgets.QCheckBox("try Connect")
        bbox_pb = QtWidgets.QPushButton("", icon=QtGui.QIcon(f"{_icon_path}/box.png"), iconSize=QtCore.QSize(40,40))
        
        del_mesh_cb.setChecked(1)
        connect_cb.setChecked(1)
        
        bbox_hl.addWidget(del_mesh_cb)
        bbox_hl.addWidget(connect_cb)
        bbox_hl.addWidget(bbox_pb)
        
        mesh_vl.addLayout(bf_layout_hl)
        mesh_vl.addLayout(rd_mesh_gl)
        mesh_vl.addLayout(bbox_hl)
        
        mesh_layout_gb.setLayout(mesh_vl)
        
        
        ## ragdoll Rig layout ##
        build_layout_gb = QtWidgets.QGroupBox("ragdoll Rig")
        build_vl = QtWidgets.QVBoxLayout()
        build_hl = QtWidgets.QHBoxLayout()
        finger_cb = QtWidgets.QCheckBox("Finger", self)
        pin_rig_cb = QtWidgets.QCheckBox("pin rig", self)
        build_pb = QtWidgets.QPushButton("! Build !", self)
        pin_pb = QtWidgets.QPushButton("pinController", icon=QtGui.QIcon(f"{_icon_path}/softpin.png"), iconSize=QtCore.QSize(40,40))
        
        finger_cb.setChecked(True)
        pin_rig_cb.setChecked(True)
        
        build_hl.addWidget(finger_cb)
        build_hl.addWidget(pin_rig_cb)
        build_hl.addWidget(build_pb)
        build_vl.addLayout(build_hl)
        build_vl.addWidget(pin_pb)
        build_layout_gb.setLayout(build_vl)
        
        main_vl.addWidget(mesh_layout_gb)
        main_vl.addWidget(build_layout_gb)
        
        # CONNECT #
        rdDefault = rdSetting.ragdollDefault()
        
        def bfMesh_clicked():
            cage.convertToCageMesh(selected()[0], float(voxel_size_le.text()), int(poly_count_le.text()))
        
        bf_mesh_pb.clicked.connect(bfMesh_clicked)
        match_pb.clicked.connect(rdDefault.renameRagdollGuide)
        mirrorLr_pb.clicked.connect(rdDefault.mirrorRagdollGuideLR)
        mirrorM_pb.clicked.connect(rdDefault.mirrorRagdollGuideM)
        
        def bBoxBuild():
            if del_mesh_cb.isChecked():
                dm = True
            if connect_cb.isChecked():
                cn = True
            rdDefault.localBbox(dm, cn)
        
        bbox_pb.clicked.connect(bBoxBuild)
        
        def rdBuild():
            finger_cb_on = finger_cb.isChecked()
            rdDefault.assignBodyRagdollMarker()
            rdDefault.defaultReplaceMesh()
            
            if finger_cb_on:
                rdDefault.assignFingerRagdollMarker()
                rdDefault.defaultReplaceMesh(finger=True)
                rdDefault.fingerPin()
            
            rdDefault.collisionFix()
            
            if pin_rig_cb:
                rdDefault.defaultPin()
            
            rdDefault.ikFix()
            rdDefault.limitRagdoll()
            
            ri.show_messageboard()
                

        build_pb.clicked.connect(rdBuild)
        
        pin_pb.clicked.connect(rdDefault.pinSelected)

        return main_vl