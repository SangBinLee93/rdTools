import ragdoll_ui.ui.rdRig_UI as rdRigUi
import imp
imp.reload(rdRigUi)

def rdRig_ui_run():
    global ui_rd_rig_ui
    try:
        ui_rd_rig_ui.close()
        ui_rd_rig_ui.deleteLater()
    except:
        pass

    ui_rd_rig_ui = rdRigUi.rdRigUI()
    ui_rd_rig_ui.show(dockable=True, floating=True)
    ui_rd_rig_ui.raise_()
    
rdRig_ui_run()