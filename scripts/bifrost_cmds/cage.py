'''
import bifrost_cmds.cage as cage
import sys, imp

imp.reload(cage)
cage.convertToCageMesh(selected()[0], detailSize=0.1, faceCount=5000)
'''
import pymel.core as pm
from pymel.core import *
from dataclasses import dataclass

def convertToCageMesh(mesh=None, detailSize=0.1, faceCount=5000):
    if not pm.pluginInfo('bifrostGraph', q=True, loaded=True):
        pm.loadPlugin('bifrostGraph')
    
    # It takes long time and produce not good result when below 0.01 value for the detail size

    # Build bifrost graph node
    bfGraph = pm.createNode('bifrostGraphShape')

    pm.vnnNode(bfGraph, '/input', createOutputPort=('inMesh', 'Object'))
    pm.vnnNode(bfGraph, '/output', createInputPort=('outMeshes', 'array<Object>'))

    pm.vnnCompound(bfGraph, '/', addNode='BifrostGraph,Geometry::Converters,mesh_to_volume')
    pm.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('volume_mode', '1'))
    pm.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('store_level_set', '1'))
    pm.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('store_fog_density', '0'))
    pm.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('resolution_mode', '0'))
    pm.vnnNode(bfGraph, '/mesh_to_volume', setPortDefaultValues=('detail_size', str(detailSize)))
    pm.vnnCompound(bfGraph, '/', addNode='BifrostGraph,Geometry::Converters,volume_to_mesh')
    pm.vnnNode(bfGraph, '/volume_to_mesh', createInputPort=('volumes.volume', 'auto'))

    pm.vnnConnect(bfGraph, '/input.inMesh', '/mesh_to_volume.mesh')
    pm.vnnConnect(bfGraph, '/mesh_to_volume.volume', '/volume_to_mesh.volumes.volume')
    pm.vnnConnect(bfGraph, '/volume_to_mesh.meshes', '/output.outMeshes')

    # Convert to cage mesh
    mesh = PyNode(mesh)
    skinCageName = '{}_cage'.format(mesh.name())
    mesh = pm.duplicate(mesh)[0]

    bfGeoToMaya = pm.createNode('bifrostGeoToMaya')
    cageMesh = pm.createNode('mesh')
    del_node = cageMesh.getParent()

    mesh.outMesh >> bfGraph.inMesh
    bfGraph.outMeshes >> bfGeoToMaya.bifrostGeo
    bfGeoToMaya.mayaMesh[0] >> cageMesh.inMesh

    pm.delete(cageMesh, ch=True)
    pm.delete(bfGraph.getParent())
    pm.delete(mesh)

    # Clean up cage mesh
    try:
        meshes = pm.polySeparate(cageMesh, ch=False)

        @dataclass
        class meshWithVolume:
            mesh :str
            volume :float

        sort_list = []
        
        # Find cage mesh in separated meshes
        for mesh in meshes:
            bb = mesh.boundingBox()
            volumeArea = bb.width() * bb.height() * bb.depth()
            sort_list.append(meshWithVolume(mesh, volumeArea))

        sorted_list = sorted(sort_list, key = lambda x:x.volume)
        final_cageMesh = sorted_list[-1].mesh
        delete_list = [x.mesh for x in sorted_list]
        delete_list.remove(delete_list[-1])
        
        pm.parent(final_cageMesh, w=True)
        pm.delete(delete_list)
        final_cageMesh.rename(skinCageName)
    except:
        pass

    pm.hyperShade(final_cageMesh, assign='lambert1')
    delete(del_node)
    # Retopologize
    pm.polyRetopo(
        final_cageMesh,
        ch=True,
        replaceOriginal=True,
        preserveHardEdges=True,
        topologyRegularity=1.0,
        faceUniformity=0.0,
        anisotropy=0.75,
        targetFaceCountTolerance=10,
        targetFaceCount=faceCount
    )
    delete(final_cageMesh, ch=1)