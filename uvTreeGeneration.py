# Generates uvs for a mesh based on connectivity, useful for tree structures


import bpy, bmesh
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
            connectionInfo = {} # this will store vertex, distance pairs
            for edge in edges:
                for edgeVert in edge.verts:
                    if edgeVert in unconnectedVerts:
                        print (edgeVert)
                        newGeneration.append(edgeVert)
                        unconnectedVerts.remove(edgeVert)
                        # TODO: we could make sure that we're connecting via the shortest route, but that's an optimization for later....


            pass
        # if it's connected to any existing vertex
        # find the closest one
        iterations += 1 # keep a counter
        finished = True





    # Finish up, write the bmesh back to the mesh
    bm.to_mesh(mesh)
    bm.free()  # free and prevent further access
    


    pass



# run code!
generateConnectivityUVs()
print ('Completed program.')