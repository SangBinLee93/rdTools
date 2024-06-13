#-*- coding: utf-8 -*-

import os
import sys
import re
import imp
import ast
import math
import json
import random
import platform

from time import *
from pathlib import Path
from dataclasses import dataclass

import maya.cmds as mc
import maya.mel as mel
from pymel.core import *
import pymel.core as pm
import pymel.core.datatypes as dt
from maya.api import OpenMaya as om

prnt_path = str(Path(__file__).parent)

def matrixCreate(i=None, o=None, m=True, p=True, d=False, mc=True, reset=True, b=0):
    '''
    i = input(없어도됨)
    o = output
    m = multMatrix (True)
    p = pickMatrix (True)
    d = decompoaseMatrix
    b = 1 : blendMatrix, 2: wtAddMatrix
    mc = output.getParent().worldInverseMatrix를 multMatrix의 matrixIn[1]에 연결해줍니다. (True)
    reset = t/r/s등 잔류값을 zero셋팅해줍니다. (True)
    
    return값 :
    test = bc.matrixCreate(i,o,m,p,d,mc,reset)
    test.mmx = multMatrix
    test.pmx = pickMatrix
    test.dmx = decomposeMatrix
    test.bmx = blendMatrix
    test.wmx = wtAddMatrix
    '''
    if not i == None:
        i = PyNode(i)
    if o == None:
        error("outputNode is need to be selected")
    
    o = PyNode(o)
    
    if o.name()[-4] == '_' and o.name()[-3:-1].isupper() == True and o.name()[-2].isupper() == True and o.name()[-1].isupper() == True:
        _output_name = o.name()[:-4]
    else:
        _output_name = o.name()
    
    if o.getParent():
        _output_parent = o.getParent()
    else:
        _output_parent = None
    
    mmx_name = f"{_output_name}_MMX"
    dmx_name = f"{_output_name}_DMX"
    pmx_name = f"{_output_name}_PMX"
    bmx_name = f"{_output_name}_BMX"
    wmx_name = f"{_output_name}_WMX"
    
    if m == True:
        mmx = createNode('multMatrix', n=mmx_name)
    else:
        mmx = None
    if d == True:
        dmx = createNode('decomposeMatrix', n=dmx_name)
    else:
        dmx = None
    if p == True:
            pmx = createNode('pickMatrix', n=pmx_name)
    else:
        pmx = None
    if b == 0:
        bmx = None
        wmx = None
    elif b == 1:
        bmx = createNode('blendMatrix', n=bmx_name)
        wmx = None
    else:
        pmx = None
        wmx = createNode('wtAddMatrix', n=wmx_name)
    
    # m-b(w)-p-d
    if m == True:
        if i:
            i.worldMatrix>>mmx.matrixIn[0]
        if mc == True:
            if _output_parent:
                _output_parent.worldInverseMatrix>>mmx.matrixIn[1]
        if b == 0:
            if p == True:
                mmx.matrixSum>>pmx.inputMatrix
                pmx.useScale.set(0)
                pmx.useShear.set(0)
                if d == True:
                    pmx.outputMatrix>>dmx.inputMatrix
                    i.rotateOrder>>dmx.inputRotateOrder
                    dmx.outputTranslate>>o.t
                    dmx.outputRotate>>o.r
                    dmx.outputScale>>o.s
                    dmx.inputRotateOrder>>o.rotateOrder
                else:
                    pmx.outputMatrix>>o.offsetParentMatrix
                    if reset == True:
                        try: o.t.set(0,0,0)
                        except : pass
                        try: o.r.set(0,0,0)
                        except : pass
                        try: o.s.set(1,1,1)
                        except : pass
                        if o.nodeType() == 'joint':
                            try: o.jo.set(0,0,0)
                            except : pass
            else:
                if d == True:
                    mmx.matrixSum>>dmx.inputMatrix
                    i.rotateOrder>>dmx.inputRotateOrder
                    dmx.outputTranslate>>o.t
                    dmx.outputRotate>>o.r
                    dmx.outputScale>>o.s
                    dmx.inputRotateOrder>>o.rotateOrder
                    if reset == True and o.nodeType() == 'joint':
                        try: o.jo.set(0,0,0)
                        except : pass
                else:
                    mmx.matrixSum>>o.offsetParentMatrix
                    if reset == True:
                        try: o.t.set(0,0,0)
                        except : pass
                        try: o.r.set(0,0,0)
                        except : pass
                        try: o.s.set(1,1,1)
                        except : pass
                        if o.nodeType() == 'joint':
                            try: o.jo.set(0,0,0)
                            except : pass
        elif b == 1:
            mmx.matrixSum>>bmx.inputMatrix
            if p == True:
                bmx.outputMatrix>>pmx.inputMatrix
                pmx.useScale.set(0)
                pmx.useShear.set(0)
                if d == True:
                    pmx.outputMatrix>>dmx.inputMatrix
                    i.rotateOrder>>dmx.inputRotateOrder
                    dmx.outputTranslate>>o.t
                    dmx.outputRotate>>o.r
                    dmx.outputScale>>o.s
                    dmx.inputRotateOrder>>o.rotateOrder
                else:
                    pmx.outputMatrix>>o.offsetParentMatrix
                    if reset == True:
                        try: o.t.set(0,0,0)
                        except : pass
                        try: o.r.set(0,0,0)
                        except : pass
                        try: o.s.set(1,1,1)
                        except : pass
                        if o.nodeType() == 'joint':
                            try: o.jo.set(0,0,0)
                            except : pass
            else:
                if d == True:
                    bmx.outputMatrix>>dmx.inputMatrix
                    i.rotateOrder>>dmx.inputRotateOrder
                    dmx.outputTranslate>>o.t
                    dmx.outputRotate>>o.r
                    dmx.outputScale>>o.s
                    dmx.inputRotateOrder>>o.rotateOrder
                    if reset == True and o.nodeType() == 'joint':
                        try: o.jo.set(0,0,0)
                        except : pass
                else:
                    bmx.outputMatrix>>o.offsetParentMatrix
                    if reset == True:
                        try: o.t.set(0,0,0)
                        except : pass
                        try: o.r.set(0,0,0)
                        except : pass
                        try: o.s.set(1,1,1)
                        except : pass
                        if o.nodeType() == 'joint':
                            try: o.jo.set(0,0,0)
                            except : pass
        else:
            mmx.matrixSum>>wmx.wtMatrix.wtMatrix[0].matrixIn
            if p == True:
                wmx.matrixSum>>pmx.inputMatrix
                pmx.useScale.set(0)
                pmx.useShear.set(0)
                if d == True:
                    pmx.outputMatrix>>dmx.inputMatrix
                    i.rotateOrder>>dmx.inputRotateOrder
                    dmx.outputTranslate>>o.t
                    dmx.outputRotate>>o.r
                    dmx.outputScale>>o.s
                    dmx.inputRotateOrder>>o.rotateOrder
                else:
                    pmx.outputMatrix>>o.offsetParentMatrix
                    if reset == True:
                        try: o.t.set(0,0,0)
                        except : pass
                        try: o.r.set(0,0,0)
                        except : pass
                        try: o.s.set(1,1,1)
                        except : pass
                        if o.nodeType() == 'joint':
                            try: o.jo.set(0,0,0)
                            except : pass
            else:
                if d == True:
                    wmx.matrixSum>>dmx.inputMatrix
                    i.rotateOrder>>dmx.inputRotateOrder
                    dmx.outputTranslate>>o.t
                    dmx.outputRotate>>o.r
                    dmx.outputScale>>o.s
                    dmx.inputRotateOrder>>o.rotateOrder
                    if reset == True and o.nodeType() == 'joint':
                        try: o.jo.set(0,0,0)
                        except : pass
                else:
                    wmx.matrixSum>>o.offsetParentMatrix
                    if reset == True:
                        try: o.t.set(0,0,0)
                        except : pass
                        try: o.r.set(0,0,0)
                        except : pass
                        try: o.s.set(1,1,1)
                        except : pass
                        if o.nodeType() == 'joint':
                            try: o.jo.set(0,0,0)
                            except : pass
    else:
        if b == 0:
            if p == True:
                if i:
                    i.worldMatrix>>pmx.inputMatrix
                pmx.useScale.set(0)
                pmx.useShear.set(0)
                if d == True:
                    pmx.outputMatrix>>dmx.inputMatrix
                    if i:
                        i.rotateOrder>>dmx.inputRotateOrder
                    dmx.outputTranslate>>o.t
                    dmx.outputRotate>>o.r
                    dmx.outputScale>>o.s
                    dmx.inputRotateOrder>>o.rotateOrder
                else:
                    pmx.outputMatrix>>o.offsetParentMatrix
                    if reset == True:
                        try: o.t.set(0,0,0)
                        except : pass
                        try: o.r.set(0,0,0)
                        except : pass
                        try: o.s.set(1,1,1)
                        except : pass
                        if o.nodeType() == 'joint':
                            try: o.jo.set(0,0,0)
                            except : pass
            else:
                if d == True:
                    if i:
                        i.worldMatrix>>dmx.inputMatrix
                        i.rotateOrder>>dmx.inputRotateOrder
                    dmx.outputTranslate>>o.t
                    dmx.outputRotate>>o.r
                    dmx.outputScale>>o.s
                    dmx.inputRotateOrder>>o.rotateOrder
                    if reset == True and o.nodeType() == 'joint':
                        try: o.jo.set(0,0,0)
                        except : pass
                else:
                    if i:
                        i.matrixSum>>o.offsetParentMatrix
                    else:
                        print('there is the only output variable')
                    if reset == True:
                        try: o.t.set(0,0,0)
                        except : pass
                        try: o.r.set(0,0,0)
                        except : pass
                        try: o.s.set(1,1,1)
                        except : pass
                        if o.nodeType() == 'joint':
                            try: o.jo.set(0,0,0)
                            except : pass
        elif b == 1:
            if i:
                i.worldMatrix>>bmx.inputMatrix
            if p == True:
                bmx.outputMatrix>>pmx.inputMatrix
                pmx.useScale.set(0)
                pmx.useShear.set(0)
                if d == True:
                    pmx.outputMatrix>>dmx.inputMatrix
                    if i:
                        i.rotateOrder>>dmx.inputRotateOrder
                    dmx.outputTranslate>>o.t
                    dmx.outputRotate>>o.r
                    dmx.outputScale>>o.s
                    dmx.inputRotateOrder>>o.rotateOrder
                else:
                    pmx.outputMatrix>>o.offsetParentMatrix
                    if reset == True:
                        try: o.t.set(0,0,0)
                        except : pass
                        try: o.r.set(0,0,0)
                        except : pass
                        try: o.s.set(1,1,1)
                        except : pass
                        if o.nodeType() == 'joint':
                            try: o.jo.set(0,0,0)
                            except : pass
            else:
                if d == True:
                    bmx.outputMatrix>>dmx.inputMatrix
                    if i:
                        i.rotateOrder>>dmx.inputRotateOrder
                    dmx.outputTranslate>>o.t
                    dmx.outputRotate>>o.r
                    dmx.outputScale>>o.s
                    dmx.inputRotateOrder>>o.rotateOrder
                    if reset == True and o.nodeType() == 'joint':
                        try: o.jo.set(0,0,0)
                        except : pass
                else:
                    bmx.outputMatrix>>o.offsetParentMatrix
                    if reset == True:
                        try: o.t.set(0,0,0)
                        except : pass
                        try: o.r.set(0,0,0)
                        except : pass
                        try: o.s.set(1,1,1)
                        except : pass
                        if o.nodeType() == 'joint':
                            try: o.jo.set(0,0,0)
                            except : pass
        else:
            if i:
                i.worldMatrix>>wmx.wtMatrix.wtMatrix[0].matrixIn
            if p == True:
                wmx.matrixSum>>pmx.inputMatrix
                pmx.useScale.set(0)
                pmx.useShear.set(0)
                if d == True:
                    pmx.outputMatrix>>dmx.inputMatrix
                    if i:
                        i.rotateOrder>>dmx.inputRotateOrder
                    dmx.outputTranslate>>o.t
                    dmx.outputRotate>>o.r
                    dmx.outputScale>>o.s
                    dmx.inputRotateOrder>>o.rotateOrder
                else:
                    pmx.outputMatrix>>o.offsetParentMatrix
                    if reset == True:
                        try: o.t.set(0,0,0)
                        except : pass
                        try: o.r.set(0,0,0)
                        except : pass
                        try: o.s.set(1,1,1)
                        except : pass
                        if o.nodeType() == 'joint':
                            try: o.jo.set(0,0,0)
                            except : pass
            else:
                if d == True:
                    wmx.matrixSum>>dmx.inputMatrix
                    if i:
                        i.rotateOrder>>dmx.inputRotateOrder
                    dmx.outputTranslate>>o.t
                    dmx.outputRotate>>o.r
                    dmx.outputScale>>o.s
                    dmx.inputRotateOrder>>o.rotateOrder
                    if reset == True and o.nodeType() == 'joint':
                        try: o.jo.set(0,0,0)
                        except : pass
                else:
                    wmx.matrixSum>>o.offsetParentMatrix
                    if reset == True:
                        try: o.t.set(0,0,0)
                        except : pass
                        try: o.r.set(0,0,0)
                        except : pass
                        try: o.s.set(1,1,1)
                        except : pass
                        if o.nodeType() == 'joint':
                            try: o.jo.set(0,0,0)
                            except : pass
    
    @dataclass
    class return_data:
        i : str
        o : str
        p : str
        mmx : str
        pmx : str
        dmx : str
        bmx : str
        wmx : str
        
    return return_data(i, o, _output_parent, mmx, pmx, dmx, bmx, wmx)

def floatAttr(Ctrl, LongName, Keyable = True, min=0, max=10, inf=False, dv=0):
    attr = '{}.{}'.format(Ctrl, LongName)
    if objExists(attr):
        PyNode(attr).delete()

    if inf==True:
        addAttr(Ctrl, ln=LongName, at='float', dv=dv)
    else:
        addAttr(Ctrl, ln=LongName, at='float', min=min, max=max, dv=dv)

    if Keyable == False:
        setAttr(Ctrl + '.' + LongName, cb=1)
    elif Keyable == True:
        setAttr(Ctrl + '.' + LongName, k=1)

    return PyNode(attr)

def boolAttr(Ctrl, LongName, Keyable=False, dv=0):
    attr = '{}.{}'.format(Ctrl, LongName)
    if objExists(attr):
        PyNode(attr).delete()
    addAttr(Ctrl, ln=LongName, at='bool', dv=dv)
    if Keyable == False:
        setAttr(Ctrl + '.' + LongName, cb=1)
    elif Keyable == True:
        setAttr(Ctrl + '.' + LongName, k=1)
    return PyNode(attr)

def enumAttr(Ctrl, LongName, name_list = ['----', '-'], Keyable = False):
    attr = '{}.{}'.format(Ctrl, LongName)
    if objExists(attr):
        PyNode(attr).delete()
    addAttr(Ctrl, ln=LongName, at='enum', dv=0, en=':'.join(name_list))
    if Keyable == False:
        setAttr(Ctrl + '.' + LongName, cb=1)
    elif Keyable == True:
        setAttr(Ctrl + '.' + LongName, k=1)
    return PyNode(attr)

def notExistThenMake(nodeName, nodeType='transform'):
    '''
    없으면 만들기
    있으면 변수지정
    return값으로 받아서 쓰면됨다.
    '''
    if not objExists(nodeName):
        if not nodeType == 'locator':
            x = createNode(nodeType, n=nodeName)
        else:
            x = spaceLocator(n=nodeName)
    else:
        x = PyNode(nodeName)
    return x

def unitConversion(v=1.0, _input=None, _output=None):
    '''
    _input(attr) -> unitConversion(conversionFactor=v) -> _output(attr)
    _input/_output skip가능
    return값 unitConversion노드
    기본적으로는 노드에디터상 보이지 않으므로 네이밍 수정 안함.
    '''
    unit =createNode('unitConversion')
    unit.conversionFactor.set(v)
    if _input:
        _input>>unit.input
    if _output:
        unit.output>>_output
    return unit

def followMaker(node, target):
    '''
    node : off_grp 선택
    target : follow 기준 선택
    static 만들 때도 node = off_grp, target = off_grp의 상위를 선택.
    '''
    follow_grp = notExistThenMake(f"{node.replace('_off_GRP', '')}_follow_GRP")
    follow_target_group = group(em=1, n=f"{node.replace('_off_GRP', '')}_{target.replace('_off_GRP', '')}_followTarget_GRP")
    parent(follow_target_group, follow_grp)
    matrixCreate(target, follow_target_group, p=1)
    matchTransform(follow_target_group, node, pos=1, rot=1, scl=0)
    return follow_target_group

def followAttrMaker(node, follow_target, follow_list, enum_name_list):
    '''
    node는 Attribute를 갖고있는 컨트롤러를,
    follow_target은 off_grp을 말합니다.
    follow_list는 followMaker로 만든 애들을 말합니다.
    
    static은 follow_list의 0번으로 고정해주세요.
    enum_name_list은 static은 제외하고 넣어주세요.

    static = inputMatrix
    나머지 = targetMatrix
    
    rotation만 Follow시키고 싶으면, 
    off_grp에 상위그룹을 하나 더 만들던지 함으로 써 
    off_grp을 기본값으로 만든 후
    return데이터에서 pmx의 useTranslate를 꺼주세요.
    이때, bmx의 inputData와 mmx는 필요없으니 지워주시면 좋을 듯합니다.
    
    node에 follow/Global가 있는 상태를 가정하며
    (네이밍 차이는 어드밴스드 셋업차이..)
    followTarget은 없는 것으로 간주합니다.
    '''
    
    follow_data = matrixCreate(follow_list[0], follow_target, b=1,m=1,p=1)
    enumAttr(node, 'followTarget', enum_name_list, Keyable = 1)
    for i, x in enumerate(follow_list):
        if not i == 0:
            mmx = duplicate(follow_data.mmx, n= follow_data.mmx.replace('MMX', f'{enum_name_list[i-1]}_MMX'))[0]
            x.worldMatrix>>mmx.matrixIn[0]
            follow_data.mmx.matrixIn[1].inputs(p=1)[0]>>mmx.matrixIn[1]
            mmx.matrixSum>>follow_data.bmx.target.target[i-1].targetMatrix
            con = createNode('condition', n=mmx.replace('MMX', 'CON'))
            con.firstTerm.set(i-1)
            node.followTarget>>con.secondTerm
            con.colorIfTrueR.set(1)
            con.colorIfFalseR.set(0)
            con.outColorR>>follow_data.bmx.target.target[i-1].weight
    
    if node.hasAttr('follow'):
        unit = unitConversion(0.1, node.follow, follow_data.bmx.envelope)
    elif node.hasAttr('Global'):
        unit = unitConversion(0.1, node.Global, follow_data.bmx.envelope)
    
    return follow_data