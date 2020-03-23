# Blender_ConnectivityUVMap
Generates "Flowing" UVs based on a mesh's connectivity, tested in Blender 2.82 MacOS, should (hopefully?) work in 2.8+ on all platforms.

## Usage: ##

1. Select a mesh in Blender
1. Go into *Edit Mode*
1. Select the vertices you want your UVs to flow out from
1. Go back into *Object Mode*
1. Copy-paste the contents of `uvTreeGeneration.py` into a script editor
1. You can change the settings by modifying the `# USER CONFIGURABLE VARIABLES` near the top:
  * UNUSED_UV = Vector((-999, -999))
    The UV value assigned to UVs that don't get reached by the UV flow (for example, if they're above the start point and you have direction set to 'downwards'. It's recommended to delete unreached UVs because you can get fringing otherwise, but if you set this far away the fringes might be too small to see.
  * ANALYSIS_MODE = AnalysisMode.OMNIDIRECTIONAL # from AnalysisMode.UPWARDS, AnalysisMode.DOWNWARDS,   AnalysisMode.OMNIDIRECTIONAL
  * HEIGHT_COMPARISON_THRESHOLD = 0.1 # if it's only a teeny bit up or down, do we still allow it?
  * MAX_ITERATIONS = 999 # crash protection hopefully :-) In practise takes about 300 max
1.
