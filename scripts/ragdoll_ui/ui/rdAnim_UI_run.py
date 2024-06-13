import ragdoll_ui.ui.rdAnim_UI as rdAnimUi
import imp
imp.reload(rdAnimUi)

def rdAnim_ui_run():
    global ui_rd_anim_ui
    try:
        ui_rd_anim_ui.close()
        ui_rd_anim_ui.deleteLater()
    except:
        pass

    ui_rd_anim_ui = rdAnimUi.rdAnimUI()
    ui_rd_anim_ui.show(dockable=True, floating=True)
    ui_rd_anim_ui.raise_()
    
rdAnim_ui_run()