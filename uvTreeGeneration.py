# Generates uvs for a mesh based on connectivity, useful for tree structures


import bpy, bmesh
from mathutils import Vector
MAX_ITERATIONS = 999

class ConnectedVertex:
    """ used for building connectivity information"""
    
    def __init__(self):
        self.data = []



def getMesh():
    """gets the selected mesh"""

    # make sure we're in OBJECT mode
    #print(bpy.context.area.type)VIEW_3D
    #bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
    selectedObjects = bpy.context.selected_objects

    # sanity checks
    if bpy.context.mode != 'OBJECT':
        raise(Exception("You need to be in OBJECT mode!"))
    if len(selectedObjects) is not 1:
        raise(Exception("Please select exactly 1 object!"))
    selectedObject = selectedObjects[0]
    if selectedObject.data not in bpy.data.meshes.values():
        raise(Exception("Selected object is not a mesh!"))

    mesh = selectedObject.data
    return mesh


def analyseMesh(bm, selectedVerts):
    """goes through the mesh generating connectivity information"""
    finished = False
    iterations = 0
    generations = [selectedVerts] # set the selected verts to be the first generation
    unconnectedVerts = set(bm.verts)-set(selectedVerts)
    rootDict = {} # stores the root of each connected vert
    
    # give each starting point a different root ID
    for i in range(len(generations[0])):
        vert = generations[0][i]
        rootDict[vert] = (i+1)/(len(generations[0])+1)

    # starts from the selected vertex
    # while we have unselected vertices (only works for the first island! so do until we don't have new vertices)
    while (finished is False) and (iterations < MAX_ITERATIONS):
        print('generation', len(generations), ', ', len(unconnectedVerts),'/',len(bm.verts), 'remaining' )
        # for all unconnected vertices:
        newGeneration = []

        for vert in generations[-1]: # do the most recent generation
            edges = vert.link_edges
            connectionInfo = {} # TODO: this will store vertex, distance pairs
            for edge in edges:
                for edgeVert in edge.verts:
                    # if it's a new one
                    if edgeVert in unconnectedVerts:
                        # print (edgeVert.index, 'is connected')
                        newGeneration.append(edgeVert)
                        unconnectedVerts.remove(edgeVert)
                        rootDict[edgeVert] = rootDict[vert] # just copy the root value from the parent
                        # TODO: we could make sure that we're connecting via the shortest route, but that's an optimization for later....

        if len(newGeneration) > 0:
            generations.append(newGeneration)
        else:
            # didn't find anything new, I guess we're finished
            finished = True

        iterations += 1 # keep a counter

    print('finished traversing network, ', len(unconnectedVerts), 'vertices left over')
    return [rootDict, generations]


def generateConnectivityUVs():
    """the main function that does everything"""

    mesh = getMesh() # get the selected mesh

    # ok, we got the mesh, let's get the bmesh (from https://docs.blender.org/api/current/bmesh.html)
    # Get a BMesh representation
    bm = bmesh.new()   # create an empty BMesh
    bm.from_mesh(mesh)   # fill it in from a Mesh
    bm.verts.ensure_lookup_table() # make everything ok

    # get selected verts
    selectedVerts = []
    for vert in bm.verts:
        if vert.select:
            selectedVerts.append(vert)
    
    # ok, we got the selected verts
    print (len(selectedVerts), '/', len(bm.verts), 'vert(s) selected')

    # run analysis loop
    rootDict, generations = analyseMesh(bm, selectedVerts)

    # ok, now we have the 'generations', we can set them. TODO: Should set parent really! OR can we just guess from the order?
    uv_layer = bm.loops.layers.uv.new('connectivity_UV')
    # color_layer = bm.loops.layers.color.new('connectivity_RGB')

    uvDict = {}

    for iGeneration in range(len(generations)):
        generation = generations[iGeneration]
        for iVert in range(len(generation)):
            vert = generation[iVert]
            uvDict[vert] =  Vector((rootDict[vert], (iGeneration+1)/(len(generations)+1)))
            # UVMap

    # now go thru all faces
    for face in bm.faces:
        for loop in face.loops:
            if loop.vert in uvDict:
                uv = uvDict[loop.vert]
            else:
                uv = Vector((-1, -1))
            loop[uv_layer].uv = uv


    # Finish up, write the bmesh back to the mesh
    bm.to_mesh(mesh)
    bm.free()  # free and prevent further access



# run code!
generateConnectivityUVs()
print ('Completed program.')