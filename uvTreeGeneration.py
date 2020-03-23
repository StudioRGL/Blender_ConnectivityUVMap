# Generates uvs for a mesh based on connectivity, useful for tree structures

# TODO: sort vertices by x position before we do anything?

import bpy, bmesh
from mathutils import Vector
MAX_ITERATIONS = 999

class TreeNode:
    """ used for building connectivity information"""
    u = None
    v = None
    vertex = None
    parent = None
    leftNeighbour = None
    rightNeighbour = None
    children = []
    
    def __init__(self, vertex):
        self.vertex = vertex
    
    def uRange(self):
        """returns the area between the left and right neighbours"""
        if self.leftNeighbour is None:
            uMin = 0
        else:
            uMin = (self.leftNeighbour.u + self.u) / 2

        if self.rightNeighbour is None:
            uMax = 1
        else:
            uMax = (self.u + self.rightNeighbour.u) / 2
        
        return [uMin, uMax]


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
    unconnectedVerts = set(bm.verts)-set(selectedVerts)
    parentDict = {} # stores the parent vert of each connected vert # TODO: remove this, it's now in TreeNode
    
    # build the first row of 'tree nodes'
    firstGeneration = []
    for i in range(len(selectedVerts)):
        newTreeNode = TreeNode(selectedVerts[i])
        firstGeneration.append(newTreeNode)
    generations = [firstGeneration] # create the generations list, we're gonna add more as we go along

    # while we have unselected vertices (only works for the first island! so do until we don't have new vertices)
    while (finished is False) and (iterations < MAX_ITERATIONS):
        print('generation', len(generations), ', ', len(unconnectedVerts),'/',len(bm.verts), 'remaining' )
        # for all unconnected vertices:
        newGeneration = []

        for node in generations[-1]: # do the most recent generation
            vert = node.vertex
            edges = vert.link_edges
            for edge in edges:
                for edgeVert in edge.verts:
                    # if it's a new one
                    if edgeVert in unconnectedVerts:
                        # ok, we found a connected one
                        newTreeNode = TreeNode(edgeVert)
                        newTreeNode.parent = node  # this is the only property we need to set right now
                        node.children.append(newTreeNode)  # ok, just to make life easy gonna go both ways
                        newGeneration.append(newTreeNode)
                        unconnectedVerts.remove(edgeVert)
                        # TODO: we could make sure that we're connecting via the shortest route, but that's an optimization for later....

        if len(newGeneration) > 0:
            generations.append(newGeneration)
        else:
            # didn't find anything new, I guess we're finished
            finished = True

        iterations += 1 # keep a counter

    print('finished traversing network, ', len(unconnectedVerts), 'vertices left over')
    
    return generations


def analyseTree(generations):
    """Once we've been through the mesh and got connection info, let's figure out what it all means"""

    # let's do this generation by generation
    for i in range(len(generations)):
        generation = generations[i]

        if i == 0:  # first generation only!
            # evenly distribute u across the full width 0-1
            for j in range(len(generation)):
                currentNode = generation[j]
                currentNode.u = (i+1)/(len(generation)+1)
                currentNode.v = 0  # it's a root node
                if j > 0:
                    # for all except the leftmost one, set left neighbour
                    currentNode.leftNeighbour = generation[j-1]  # it will be the most recently-added one!
                    currentNode.leftNeighbour.rightNeighbour = currentNode  # link it up...
        else: # for all generations except the root one
            parentGeneration = generations[i-1]

            # alright, we already know everything about the parent generation, including which children each parent has
            for parent in parentGeneration:
                uRange = parent.uRange()
                for iChild in range(len(parent.children)):
                    child = parent.children[iChild]
                    uRatio = (iChild+1)/(len(parent.children)+1)
                    child.u = (uRange[0] * uRatio) + (uRange[1]*(1-uRatio)) # lerp from side to side
                    child.v = j/len(generations)  # TODO: make this distance-based later! right now it just sets v to be the generation




def writeUVs(generations, bm):
    """just write the uvs hey"""
    # ok, now we have the 'generations', we can do useful stuff with them.

    uv_layer = bm.loops.layers.uv.new('connectivity_UV')
    # color_layer = bm.loops.layers.color.new('connectivity_RGB')

    uvDict = {} # store the uv as a list of 2 vectors, with vert as the key

    
    #connectedVertices = [] # gonna be one for each vertex
    #for v in bm.verts:
    #    connectedVertices.append()
    

    # naive version
    # TODO: add distance calculation?
    # for iGeneration in range(len(generations)):
    #    generation = generations[iGeneration]
    #    for iVert in range(len(generation)):
    #        vert = generation[iVert]
    #        uvDict[vert] =  Vector((0, (iGeneration+1)/(len(generations)+1)))

    # branch-aware version:

    # for each generation
    for iGeneration in range(len(generations)):
        generation = generations[iGeneration]
        
        # generate the uvs step by step

        if iGeneration == 0: 
            # special case for the 'roots' of the tree
            pass
        else:
            # only do this if we're NOT on the first generation
            parentGeneration = generations[iGeneration-1]
            
            childCount = {} # from the previous generation, key is vertex, value is child count
            uRange = {} # the u space available (from halfway point to each neighbour)

            for iParentVert in range(len(parentGeneration)):
                parentVert = parentGeneration[iParentVert]
                childCount[parentVert] = 0 # initialize as 'no children'
                # turn to the left, turn to the right....
                uMin = 0
                uMax = 1
                #if parentVert > 0:

                uRange[parentVert] = [uMin, uMax]


            # go through all the verts counting how many come from each parent vert
            for iVert in range(len(generation)):
                vert = generation[iVert]
                parent = parentDict[vert]
                childCount[parent] += 1  # increment the child count of the parent

            # ok, now we know how many branches come off each parent, let's work out our uvs
    
    # for each parent
    # find the uv range occupied by the parent (the halfway point between the left and right neighbours, or 0 or 1)
    # for each child of the parent
    # lay out within that range


    # now go thru all faces and actually *write* the uvs
    for face in bm.faces:
        for loop in face.loops:
            if loop.vert in uvDict:
                uv = uvDict[loop.vert]
            else:
                uv = Vector((-1, -1))
            loop[uv_layer].uv = uv


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

    generations = analyseMesh(bm, selectedVerts)  # run analysis loop on mesh

    analyseTree(generations) # run analysis loop on tree (this edits the 'generation' array's data)

    print('analysed tree')

    # writeUVs(generations, bm)  # write the data to the uvs
    
    # Finish up
    bm.to_mesh(mesh)  # write the bmesh back to the mesh
    bm.free()  # free and prevent further access



# run code!
generateConnectivityUVs()
print ('Completed program.')