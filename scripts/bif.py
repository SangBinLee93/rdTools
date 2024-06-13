from pymel.core import *
import pymel.core as pm
from functools import partial
import bc

def loadBif():
    if not pluginInfo('bifrostGraph', q=True, loaded=True):
        loadPlugin('bifrostGraph')
    if not pluginInfo('bifrostshellnode', q=True, loaded=True):
        loadPlugin('bifrostshellnode')

def vAddNodeTemp(add_node_string, bifrost_graph):
    vnn_name = pm.vnnCompound(bifrost_graph, '/', addNode=add_node_string)[0]
    return vnn_name

def vSetAttrTemp(vnn_attr, value, bifrost_graph):
    pm.vnnNode(bifrost_graph, f"/{vnn_attr.split('.')[0]}", setPortDefaultValues=[vnn_attr.split('.')[-1], str(value)])

def vSetAttrDataTypeTemp(vnn_attr, value, bifrost_graph):
    pm.vnnNode(bifrost_graph, f"/{vnn_attr.split('.')[0]}", setPortDataType=[vnn_attr.split('.')[-1], value])

def vConnectTemp(_input, _output, bifrost_graph):
    pm.vnnConnect(bifrost_graph, f"/{_input}", f"/{_output}")
    
def vInputTemp(port, port_type, bifrost_graph, option=None):
    if option:
        pm.vnnNode(bifrost_graph, "/input", createOutputPort=[port, port_type], portOptions=option)
    else:
        pm.vnnNode(bifrost_graph, "/input", createOutputPort=[port, port_type])

def vOutputTemp(port, port_type, bifrost_graph, option=None):
    if option:
        pm.vnnNode(bifrost_graph, "/output", createInputPort=[port, port_type], portOptions=option)
    else:
        pm.vnnNode(bifrost_graph, "/output", createInputPort=[port, port_type])

def bifRayCast(locs, mesh, castVector=(0,-1,0), orient=True):
    '''
    locs = 로케이터들 리스트로 담아야함
    mesh = mesh노드로 선택
    castVector = loc -> mesh로 쏠 방향.
    '''
    loadBif()

    with pm.UndoChunk():

        locs = [PyNode(x) for x in locs]
        bfGraph = createNode('bifrostGraphShape', n=locs[0].name().replace('_LOC', '')+'_BIFShape')
        
        vAddNode = partial(vAddNodeTemp, bifrost_graph=bfGraph)
        vSetAttr = partial(vSetAttrTemp, bifrost_graph=bfGraph)
        vSetAttrDataType = partial(vSetAttrDataTypeTemp, bifrost_graph=bfGraph)
        vConnect = partial(vConnectTemp, bifrost_graph=bfGraph)
        vInput = partial(vInputTemp, bifrost_graph=bfGraph)
        vOutput = partial(vOutputTemp, bifrost_graph=bfGraph)
        
        rename(bfGraph.getParent(), bfGraph.replace('BIFShape', 'BIF'))
        bfGraph_trans = bfGraph.getParent()
        mesh = PyNode(mesh)
        
        #input 
        vInput("mesh", "Object", option ="pathinfo={path="+bfGraph.fullPath().replace('|', '/')+";setOperation=+;active=true}")
        mesh.outMesh>>bfGraph.mesh
        
        if not objExists('raycast_GRP'):
            grp = group(em=1, n='raycast_GRP')
            shoot_grp = group(em=1, n='raycast_shoot_GRP', p=grp)
            hit_grp = group(em=1, n='raycast_hit_GRP', p=grp)
            grp.inheritsTransform.set(0)
        else:
            grp = PyNode('raycast_GRP')
            shoot_grp = PyNode('raycast_shoot_GRP')
            hit_grp = PyNode('raycast_hit_GRP')
        
        for i, loc in enumerate(locs):
            if not loc.name().endswith('_shoot_LOC'):
                rename(loc, loc+'_shoot_LOC')
            vector_loc = spaceLocator(n=loc.replace('LOC', 'castVector_LOC'))
            vector_loc.t.set(castVector)
            vector_loc.v.set(0)
            parent(vector_loc, loc, r=1)

            #input/output
            vInput(f"inPoint_{str(i)}", "Math::float3")
            vInput(f"inPointCastVector_{str(i)}", "Math::float3")
            vOutput(f"hitPoint_{str(i)}", "Math::float3")

            #raycast_node
            raycast_vnn = vAddNode("BifrostGraph,Geometry::Query,get_raycast_locations")
            vSetAttr(f"{raycast_vnn}.use_cutoff_distance", 0)

            #raycast_connect
            vConnect("input.mesh", f"{raycast_vnn}.geometry")
            vConnect(f"input.inPoint_{str(i)}", f"{raycast_vnn}.positions")
            vConnect(f"input.inPointCastVector_{str(i)}", f"{raycast_vnn}.directions")

            #sample_property
            sample_vnn = vAddNode("BifrostGraph,Geometry::Query,sample_property")
            vSetAttrDataType(f"{sample_vnn}.default", "Math::float3")
            pm.vnnPort(bfGraph, f"/{sample_vnn}.locations", 0, 1, set=2)

            #sample_connect
            pm.vnnNode(bfGraph, f"/{sample_vnn}", createInputPort=["locations.locations", "auto"])
            vConnect(f"{raycast_vnn}.locations", f"{sample_vnn}.locations.locations")
            vConnect("input.mesh", f"{sample_vnn}.geometry")

            #array
            array_vnn = vAddNode("BifrostGraph,Core::Array,get_from_array")
            vConnect(f"{sample_vnn}.sampled_data", f"{array_vnn}.array")
            vConnect(f"{array_vnn}.value", f"output.hitPoint_{str(i)}")


            #inPoint_#
            loc.getShape().worldPosition[0].worldPosition>>PyNode(f"{bfGraph}.inPoint_{str(i)}")

            #inPointCastVector_#
            sub = createNode('plusMinusAverage', n= loc.replace('LOC', 'vector_PMA'))
            sub.operation.set(2)
            vector_loc.getShape().worldPosition[0].worldPosition>>sub.input3D[0]
            loc.getShape().worldPosition[0].worldPosition>>sub.input3D[1]
            sub.output3D>>PyNode(f"{bfGraph}.inPointCastVector_{str(i)}")

            #hit_locator
            hit_loc = spaceLocator(n=loc.replace('LOC', 'hit_LOC'))
            PyNode(f"{bfGraph}.hitPoint_{str(i)}")>>hit_loc.t
            
            #orient
            if orient:
                dmx = bc.nodeCreate(loc, 'decomposeMatrix')
                loc.worldMatrix>>dmx.inputMatrix
                dmx.outputRotate>>hit_loc.r
            
            parent(hit_loc, hit_grp)
            parent(loc, shoot_grp)
            
        parent(bfGraph_trans, grp)
        parent(mesh, grp)    

    return grp
