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


def generateConnectivityUVs():
    """do the whole thing"""
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


    # prepare to run loop
    finished = False
    iterations = 0
    generations = [selectedVerts] # set the selected verts to be the first generation
    unconnectedVerts = set(bm.verts)-set(selectedVerts)

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
                    # if it's connected to any existing vertex
                    if edgeVert in unconnectedVerts:
                        print (edgeVert.index, 'is connected')
                        newGeneration.append(edgeVert)
                        unconnectedVerts.remove(edgeVert)
                        # TODO: we could make sure that we're connecting via the shortest route, but that's an optimization for later....

        if len(newGeneration) > 0:
            generations.append(newGeneration)
        else:
            # didn't find anything new, I guess we're finished
            finished = True

        iterations += 1 # keep a counter

    print('finished traversing network, ', len(unconnectedVerts), 'vertices left over')

    # ok, now we have the 'generations', we can set them. TODO: Should set parent really! OR can we just guess from the order?
    uv_layer = bm.loops.layers.uv.new('connectivity_UV')
    # color_layer = bm.loops.layers.color.new('connectivity_RGB')

    # zero everything
    # for vert in bm.verts:
    #    vert.link_loops[0][uv_layer].uv = Vector((-1,-1))

    uvDict = {}

    for iGeneration in range(len(generations)):
        generation = generations[iGeneration]
        for iVert in range(len(generation)):
            vert = generation[iVert]
            # vert.link_loops[0][uv_layer].uv = Vector((iVert/len(generation), iGeneration/len(generations)))
            # vert.link_loops[0][color_layer] = Vector((iVert/len(generation), iGeneration/len(generations), 0, 1))
            uvDict[vert] =  Vector((iVert/len(generation), iGeneration/len(generations)))
            print ('setting vert ', vert.index, 'to UV', Vector((iVert/len(generation), iGeneration/len(generations))))
            # UVMap

    # now go thru all faces
    for face in bm.faces:
        for loop in face.loops:
            uv = uvDict[loop.vert]
            loop[uv_layer].uv = uv


    # Finish up, write the bmesh back to the mesh
    bm.to_mesh(mesh)
    bm.free()  # free and prevent further access
    


    pass



# run code!
generateConnectivityUVs()
print ('Completed program.')