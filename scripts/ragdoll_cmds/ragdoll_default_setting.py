from pymel.core import *
import pymel.all as pm
from dataclasses import dataclass
import pymel.core.datatypes as dt
import ragdoll.commands as rd
from ragdoll import interactive as ri
from pprint import pprint
import imp, bc
import json
from pathlib import Path
imp.reload(bc)

class ragdollDefault():
    def __init__(self):
        '''
        ragdoll plugin 활성화 및 공용 변수 지정
        '''
        
        if not pluginInfo('ragdoll', q=True, loaded=True):
            loadPlugin('ragdoll')
            
        import bc
        
        self.spine_list = ['M_RootX_CTL', 'M_FkSpine1_CTL', 'M_FkSpine2_CTL', 'M_FkSpine3_CTL', 'M_FkNeck_CTL', 'M_FkHead_CTL']
        self.left_arm_list = ['M_FkSpine3_CTL', 'L_Scapula_JNT', 'L_Shoulder_JNT', 'L_Elbow_JNT', 'L_Wrist_JNT']
        self.right_arm_list = ['M_FkSpine3_CTL', 'R_Scapula_JNT', 'R_Shoulder_JNT', 'R_Elbow_JNT', 'R_Wrist_JNT']
        self.left_leg_list = ['M_RootX_CTL', 'L_Hip_JNT', 'L_Knee_JNT', 'L_Ankle_JNT', 'L_Toes_JNT']
        self.right_leg_list = ['M_RootX_CTL', 'R_Hip_JNT', 'R_Knee_JNT', 'R_Ankle_JNT', 'R_Toes_JNT']
        
        self.all_list = [self.spine_list, self.right_arm_list, self.left_arm_list, self.right_leg_list, self.left_leg_list]
        self.all_rd_bone_list = []
        for y in self.all_list:
            for x in y:
                if not x in self.all_rd_bone_list:
                    self.all_rd_bone_list.append(x)
                    
        #Fingers
        l_thumb_list = ['L_Wrist_JNT', 'L_ThumbFinger1_JNT', 'L_ThumbFinger2_JNT', 'L_ThumbFinger3_JNT']
        l_index_list = ['L_Wrist_JNT', 'L_IndexFinger1_JNT', 'L_IndexFinger2_JNT', 'L_IndexFinger3_JNT']
        l_middle_list = ['L_Wrist_JNT', 'L_MiddleFinger1_JNT', 'L_MiddleFinger2_JNT', 'L_MiddleFinger3_JNT']
        l_ring_list = ['L_Wrist_JNT', 'L_RingFinger1_JNT', 'L_RingFinger2_JNT', 'L_RingFinger3_JNT']
        l_pinky_list = ['L_Wrist_JNT', 'L_PinkyFinger1_JNT', 'L_PinkyFinger2_JNT', 'L_PinkyFinger3_JNT']
        
        r_thumb_list = ['R_'+x[2:] for x in l_thumb_list]
        r_index_list = ['R_'+x[2:] for x in l_index_list]
        r_middle_list = ['R_'+x[2:] for x in l_middle_list]
        r_ring_list = ['R_'+x[2:] for x in l_ring_list]
        r_pinky_list = ['R_'+x[2:] for x in l_pinky_list]
        
        self.all_finger_list = [l_thumb_list, l_index_list, l_middle_list, l_ring_list, l_pinky_list, r_thumb_list, r_index_list, r_middle_list, r_ring_list, r_pinky_list]
        
        self.all_rd_finger_bone_list = []
        for y in self.all_finger_list:
            for x in y:
                if not x in self.all_rd_finger_bone_list:
                    self.all_rd_finger_bone_list.append(x)
    
    def assignBodyRagdollMarker(self):
        '''
        body기본구조만큼 ragdoll Marker 생성
         - Rig
        '''
        for _list in self.all_list:
            ri.assign_and_connect(_list)
        all_rd_markers = [x for x in ls('*', type='rdMarker') if not 'rGround' in x.name()]
        for x in all_rd_markers:
            x.inputType.set(0)
            jnt = x.sourceTransform.inputs()[0]
            if jnt == PyNode('M_RootX_CTL'):
                ctl = PyNode('M_RootX_CTL')
                if not ctl.hasAttr('ragdollSimulate'):
                    bc.boolAttr(ctl, 'ragdollSimulate')
                ctl.ragdollSimulate.set(0)
                con = createNode('condition', n=x.replace('CTL', 'CON'))
                ctl.ragdollSimulate>>con.firstTerm
                con.colorIfTrueR.set(2)
                con.colorIfFalseR.set(3)
                con.outColorR>>x.inputType
                continue
            elif jnt.name() in self.left_arm_list[1:]:
                ctl = PyNode(jnt[:2]+'Fk'+jnt[2:].replace('JNT', 'CTL'))
            elif jnt.name() in self.right_arm_list[1:]:
                ctl = PyNode(jnt[:2]+'Fk'+jnt[2:].replace('JNT', 'CTL'))
            elif jnt.name() in self.left_leg_list[1:]:
                ctl = PyNode(jnt[:2]+'Fk'+jnt[2:].replace('JNT', 'CTL'))
            elif jnt.name() in self.right_leg_list[1:]:
                ctl = PyNode(jnt[:2]+'Fk'+jnt[2:].replace('JNT', 'CTL'))
            else:
                continue
            
            ctl.message>>x.destinationTransforms[0]
        
    def renameRagdollGuide(self):
        '''
        리스트 내의 메쉬들을 약속된 규약의 장소에 parent가 되어있다면, rename 및 그룹 정리 해줌.
         - Rig (Modeling)
        '''
        all_rd_guide_mesh = selected()
        for guide in all_rd_guide_mesh:
            guide = PyNode(guide)
            name = guide.getParent().name()
            if not objExists('ragdoll_guide_GRP'):
                ragdoll_guide_grp = group(em=1, n='ragdoll_guide_GRP')
            else:
                ragdoll_guide_grp = PyNode('ragdoll_guide_GRP')
            
            if (name in self.all_rd_bone_list) or (name in self.all_rd_finger_bone_list):
                rename(guide, name+'_RDG')
                parent(guide, ragdoll_guide_grp)
            else:
                print(f'{guide.name()}의 페런트를 확인해주세요.')
                continue
                
    def mirrorRagdollGuideLR(self):
        '''
        L -> R
        R -> L
        없는 거만 자동으로 미러해줌.
         - Rig (Modeling)
        '''
        l_rdg = ls('L_*_RDG', type='transform')
        r_rdg = ls('R_*_RDG', type='transform')
        
        
        @dataclass
        class noLR:
            lr :str
            name :str

        l_rdg_noLR = [noLR(x.name()[0], x.name()[2:]) for x in l_rdg]
        r_rdg_noLR = [noLR(x.name()[0], x.name()[2:]) for x in r_rdg]
        lr_rdg_noLR = []
        
        for x in l_rdg_noLR:
            lr_rdg_noLR.append(x)
        for y in r_rdg_noLR:
            lr_rdg_noLR.append(y)
        rdg_sorted = sorted(lr_rdg_noLR, key= lambda x : x.name)
        
        for i, x in enumerate(rdg_sorted):
            node_name = (x.lr+'_'+x.name)
            if i == 0:
                if not rdg_sorted[i].name == rdg_sorted[i+1].name:
                    if x.lr == 'L':
                        mirrored_node_name = 'R_'+x.name
                    elif x.lr == 'R':
                        mirrored_node_name = 'L_'+x.name
                    mirrored = duplicate(node_name)[0]
                    rename(mirrored, mirrored_node_name)
                    mirrored.sx.set(-1)
                    makeIdentity(mirrored, a=1, s=1, pn=1)
            elif i == len(rdg_sorted)-1:
                if not rdg_sorted[i].name == rdg_sorted[i-1].name:
                    if x.lr == 'L':
                        mirrored_node_name = 'R_'+x.name
                    elif x.lr == 'R':
                        mirrored_node_name = 'L_'+x.name
                    mirrored = duplicate(node_name)[0]
                    rename(mirrored, mirrored_node_name)
                    mirrored.sx.set(-1)
                    makeIdentity(mirrored, a=1, s=1, pn=1)
            else:
                if (rdg_sorted[i].name == rdg_sorted[i-1].name) or (rdg_sorted[i].name == rdg_sorted[i+1].name):
                    continue
                else:
                    if x.lr == 'L':
                        mirrored_node_name = 'R_'+x.name
                    elif x.lr == 'R':
                        mirrored_node_name = 'L_'+x.name
                    mirrored = duplicate(node_name)[0]
                    rename(mirrored, mirrored_node_name)
                    mirrored.sx.set(-1)
                    makeIdentity(mirrored, a=1, s=1, pn=1)
    
    def mirrorRagdollGuideM(self):
        '''
        균형을 위해 polyMirrorFace 커맨드를 줌
         - Rig (Modeling)
        '''
        m_rdg = ls('M_*_RDG', type='transform')
        for x in m_rdg:
            polyMirrorFace(PyNode(x), cutMesh=1, axis=0, axisDirection=-1, mergeMode=1, mergeThresholdType=0, mergeThreshold=0.001, mirrorAxis = 2, mirrorPosition =0, smoothingAngle=30, ch=1)
            delete(PyNode(x), ch=1)
    
    def defaultReplaceMesh(self, finger=False):
        '''
        rdMarker의 계산방식을 mesh로 하고, 약속된 규약의 메쉬이름을 따라 만들어 줌.
         - Rig
        '''
        all_rd_geos = []
        all_rd_markers = []

        if not finger:
            all_bone_list = self.all_rd_bone_list
        else:
            all_bone_list = [x for x in self.all_rd_finger_bone_list if not 'Wrist' in x]

        for i,x in enumerate(all_bone_list):
            name = x
            if finger:
                num = i + 24
            else:
                num = i + 1
            y = PyNode(name+'_RDG')
            z = PyNode([k for k in PyNode(x).outputs() if k.nodeType()=='rdMarker'][0])
            rename(z, z[:8]+str(num).zfill(2)+z[7:])
            all_rd_geos.append(y)
            all_rd_markers.append(z)
        
        select(cl=1)
        if not objExists('rdMarkers'):
            all_set = sets(n='rdMarkers')
        else:
            all_set = PyNode('rdMarkers')
            
        if not finger:
            select(all_rd_markers[6:10])
            r_arm_set = sets(n='rdMarkers_01_r_arm')
            sets(all_set, e=1, fe=r_arm_set)
            
            select(all_rd_markers[10:14])
            l_arm_set = sets(n='rdMarkers_02_l_arm')
            sets(all_set, e=1, fe=l_arm_set)
            
            select(all_rd_markers[0:6])
            spine_set = sets(n='rdMarkers_03_spine')
            sets(all_set, e=1, fe=spine_set)
            
            select(all_rd_markers[14:18])
            r_leg_set = sets(n='rdMarkers_04_r_leg')
            sets(all_set, e=1, fe=r_leg_set)
            
            select(all_rd_markers[18:22])
            l_leg_set = sets(n='rdMarkers_05_l_leg')
            sets(all_set, e=1, fe=l_leg_set)
        else:
            select(all_rd_markers[0:15])
            l_finger_set = sets(n='rdMarkers_06_l_fingers')
            sets(all_set, e=1, fe=l_finger_set)
            
            select(all_rd_markers[15:])
            r_finger_set = sets(n='rdMarkers_07_r_fingers')
            sets(all_set, e=1, fe=r_finger_set)
            
        for x,y in zip(all_rd_markers, all_rd_geos):
            select(x,y)
            ri.replace_marker_mesh()
            
    def assignFingerRagdollMarker(self):
        '''
        손가락 시뮬이 필요할 경우, 손가락을 추가해 줌.
         - Rig
        '''
        
        all_finger_rd_markers = []
        for _list in self.all_finger_list:
            ri.assign_and_connect(_list)
        for jnt in self.all_rd_finger_bone_list:
            if not 'Wrist' in jnt:
                jnt = PyNode(jnt)
                ctl = PyNode(jnt[:2]+'Fk'+jnt[2:].replace('JNT', 'CTL'))
                mk = [x for x in jnt.message.outputs() if x.nodeType() == 'rdMarker'][0]
                ctl.message>>mk.destinationTransforms[0]

    def collisionFix(self):
        '''
        팔꿈치, 무릎 아래의 하이라키끼리 그룹을 분리해서 콜리전 계산을 가능케 해줌.
        하이라키로 읽기 때문에 손가락 빌드 후에 쓰면 손가락도 포함해줌.
         - Rig
        '''
        select(ls('L_Elbow_JNT', dag=1))
        ri.select_markers_from_assigned()
        ri.group_markers()
        
        select(ls('R_Elbow_JNT', dag=1))
        ri.select_markers_from_assigned()
        ri.group_markers()
        
        select(ls('L_Knee_JNT', dag=1))
        ri.select_markers_from_assigned()
        ri.group_markers()
        
        select(ls('R_Knee_JNT', dag=1))
        ri.select_markers_from_assigned()
        ri.group_markers()
    
    def ikFix(self):
        all_markers = ls('*', type='rdMarker')

        for x in all_markers:
            if 'Ankle' in x.name():
                x.recordTranslation.set(1) #record
                if x.name() == 'rMarker_21_L_Ankle_JNT': #ikbake
                    PyNode('L_IkLeg_CTL.message')>>x.destinationTransforms[1]
                elif x.name() == 'rMarker_17_R_Ankle_JNT': #ikbake
                    PyNode('R_IkLeg_CTL.message')>>x.destinationTransforms[1]        
            elif 'Knee' in x.name():
                x.recordTranslation.set(1)
                if x.name() == 'rMarker_20_L_Knee_JNT':
                    PyNode('L_IkLeg_pv_CTL.message')>>x.destinationTransforms[1]
                elif x.name() == 'rMarker_16_R_Knee_JNT':
                    PyNode('R_IkLeg_pv_CTL.message')>>x.destinationTransforms[1]
            elif 'Elbow' in x.name():
                x.recordTranslation.set(1)
                if x.name() == 'rMarker_13_L_Elbow_JNT':
                    PyNode('L_IkArm_pv_CTL.message')>>x.destinationTransforms[1]
                elif x.name() == 'rMarker_09_R_Elbow_JNT':
                    PyNode('R_IkArm_pv_CTL.message')>>x.destinationTransforms[1]
            elif 'Wrist' in x.name():
                x.recordTranslation.set(1)
                if x.name() == 'rMarker_14_L_Wrist_JNT':
                    PyNode('L_IkArm_CTL.message')>>x.destinationTransforms[1]
                elif x.name() == 'rMarker_10_R_Wrist_JNT':
                    PyNode('R_IkArm_CTL.message')>>x.destinationTransforms[1]
    def fingerPin(self):
        '''
        중지/약지/새끼 너무 벌어지지 않도록 distanceConstraint 넣어 줌.  - Rig
        '''
        l_middle = ls('rMarker_30*', type='rdMarker')[0]
        l_ring = ls('rMarker_33*', type='rdMarker')[0]
        l_pinky = ls('rMarker_36*', type='rdMarker')[0]
        
        r_middle = ls('rMarker_45*', type='rdMarker')[0]
        r_ring = ls('rMarker_48*', type='rdMarker')[0]
        r_pinky = ls('rMarker_51*', type='rdMarker')[0]
        
        select(l_middle, l_ring)
        ri.create_distance_constraint()
        select(l_ring, l_pinky)
        ri.create_distance_constraint()
        
        select(r_middle, r_ring)
        ri.create_distance_constraint()
        select(r_ring, r_pinky)
        ri.create_distance_constraint()
    
    def pinSelected(self):
        '''
        선택한 대상을 pinContraint를 만들어주고, 움직이기에 편하게 컨트롤러(로케이터)를 만들어 줌.  - Rig / Anim
        '''
        with pm.UndoChunk():
            selection = selected()
            grps = []
            for sel in selection:
                if not sel.nodeType() == 'rdMarker':
                    rd_marker = [x for x in sel.message.listConnections() if x.nodeType()=='rdMarker'][0]
                else:
                    rd_marker = sel
                select(rd_marker)
                ri.create_pin_constraint()
                pin = [x.node() for x in rd_marker.outputs(p=1) if x.nodeType() == 'rdPinConstraint'][-1]
                pin_trans = pin.getParent()
                loc = spaceLocator(n=pin_trans+'_LOC')
                loc_shape = loc.getShape()
                loc_shape.localScale.set(2,2,2)
                loc_shape.overrideEnabled.set(1)
                loc_shape.overrideColor.set(16)
                
                select(cl=1)
                jnt = joint(n=pin_trans+'_CTL')
                parent(loc.getShape(), jnt, r=1, s=1)
                delete(loc)
                jnt.drawStyle.set(2)
                
                
                
                matchTransform(jnt, pin_trans)
                
                grp = group(em=1, n=jnt.replace('CTL', 'GRP'))
                matchTransform(grp, jnt, pos=1, rot=0)
                parent(jnt, grp)
                makeIdentity(jnt, jo=0, a=1)
                parent(pin_trans, jnt)
                parent(pin, jnt, r=1, s=1)
                pin_trans.v.set(0)
                
                select(cl=1)
                grps.append(grp)
        
        return grps
        
    def defaultPin(self):
        '''
        디폴트 캐릭터 구조일 때, pin을 알아서 만들어주고, follow기능으로 디폴트 위치가 조절가능함. - Rig
        '''
        ctls = ['M_RootX_CTL', 'M_FkHead_CTL', 'R_Wrist_JNT', 'L_Wrist_JNT', 'L_Ankle_JNT', 'R_Ankle_JNT']
        select(ctls)
        grps = self.pinSelected()
        pin_rig_grp = group(em=1, n='pin_rig_grp')
        parent(grps, pin_rig_grp)
        for c, g in zip(ctls, grps):
            sky = PyNode('Sky_LOC')
            
            ctl = g.getChildren()[0]
            
            bc.floatAttr(ctl, 'follow')
            o = bc.followMaker(g, pin_rig_grp)
            s = bc.followMaker(g, sky)
            j = bc.followMaker(g, c)
            
            bc.followAttrMaker(ctl, g, [o,s,j], ['sky', 'rig'])
            parent(s.getParent(), pin_rig_grp)
            ctl.follow.set(10)
            ctl.followTarget.set(1)
            
    def selectMarkers(self):
        a = ls(sl=1)

        select_list = []
        for x in a:
            if x.nodeType() == 'rdMarker':
                select_list.append(x)
            else:
                rgrp = [y for y in x.listRelatives(c=1,s=1) if y.nodeType() == "rdGroup"]
                if rgrp:
                    rgrp = rgrp[0]
                elif x.nodeType() == 'rdGroup':
                    rgrp = x
                else:
                    rgrp = None
                
                if rgrp:
                    markers = [y for y in rgrp.inputs() if y.nodeType()=='rdMarker']
                    for k in markers:
                        if not k in select_list:
                            select_list.append(k)
                
                mesh = [y for y in x.listRelatives(c=1,s=1) if y.nodeType() == "mesh"]
                if mesh:
                    mesh = [x for x in mesh if x.intermediateObject.get()==0][0]
                elif x.nodeType() == 'mesh':
                    mesh = x
                else:
                    mesh = None
                
                if mesh:
                    markers = [y for y in mesh.outputs() if y.nodeType()=='rdMarker']
                    for k in markers:
                        if not k in select_list:
                            select_list.append(k)
                        
                markers = [y for y in x.outputs() if y.nodeType()=='rdMarker']
                for k in markers:
                        if not k in select_list:
                            select_list.append(k)

        select(select_list)
        
        return select_list

    def limitRagdoll(self):
        with open(f"{Path(__file__).parent}/ragdoll_limits.json", 'r') as f:
            limit_json_data = json.load(f)
        
        for x in limit_json_data:
            if objExists(x):
                node = PyNode(x)
                node.lira.set(dt.Vector(limit_json_data[x]['lira']))
                pafr_trans = node.pafr.get()[-1]
                new_pafr = dt.Matrix(dt.Array(limit_json_data[x]['pafr'][0]), dt.Array(limit_json_data[x]['pafr'][1]), dt.Array(limit_json_data[x]['pafr'][2]), pafr_trans)
                node.pafr.set(new_pafr)
                
    def autoCache(self):
        a = ls('::*', type='rdSolver')
        if not a:
            return
        else:
            a = a[0]
        if a.cache.get() == 0:
            ri.cache_all()
        else:
            ri.uncache()
            
    def localBbox(self, deleteSelection = True, connectMarker = True):
        a = ls(sl=1)
        boxes = []
        parents = []
        for x in a:
            p = x.getParent()
            clu=cluster(x)
            grp = group(em=1)
            parent(clu, grp)
            grp.offsetParentMatrix.set(x.parentInverseMatrix.get())
            # x.offsetParentMatrix.set(x.parentInverseMatrix.get())
            box = geomToBBox(x, ko=1, n=p.replace(p.split('_')[-1], "BBox"), s=1, sc=(0.5,0.5,0.5))[0]
            delete(grp)
            matchTransform(box, p)
            
            if connectMarker == True:
                select(p)
                m = self.selectMarkers()
                if m:
                    m = m[0]
                    select(box, m)
                    ri.replace_marker_mesh()
            
            boxes.append(box)
            parents.append(p)
            
        grp = group(em=1, n='bboxes')
        parent(boxes,grp)
        if deleteSelection == True:
            delete(a)
        
        return boxes

    # lock rotation - ohhhhh sooo hard... based on animator/sangbin/ezreal_rig_v02_ragdoll
    # i did it roughly, you need to change little bit

'''
rd_default = ragdollDefault()

rd_default.renameRagdollGuide(selected()) #naming
rd_default.mirrorRagdollGuideLR() #mirrorLR
rd_default.mirrorRagdollGuideM() #mirrorM

rd_default.assignBodyRagdollMarker()
rd_default.defaultReplaceMesh()

rd_default.assignFingerRagdollMarker()
rd_default.defaultReplaceMesh(finger=True)

rd_default.collisionFix()
rd_default.fingerPin()

rd_default.defaultPin()
# rd_default.pinSelected()


ri.show_messageboard()
'''

# all_markers = ls('*', type='rdMarker')[:-1]
# all_markers_dict = {}

# for x in all_markers:
#     small_dict = {}
#     small_dict['lira'] = list(x.lira.get())
#     mx = list(x.pafr.get())
#     small_dict['pafr'] = [list(y) for y in mx]
#     all_markers_dict[x.name()] = small_dict

# import json
# with open(f"{pm.system.sceneName().dirname()}/ragdoll_limits.json", "w") as json_file:
#     json.dump(all_markers_dict, json_file, indent=4)