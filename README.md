# Blender_ConnectivityUVMap
Generates "Flowing" UVs based on a mesh's connectivity, tested in Blender 2.82 MacOS, should (hopefully?) work in 2.8+ on all platforms.

## Usage: ##

1. Select a mesh in Blender
1. Go into **Edit Mode**
1. Select the vertices you want your UVs to flow out from
1. Go back into **Object Mode**
1. Copy-paste the contents of `uvTreeGeneration.py` into a script editor
1. You can change the settings by modifying the `# USER CONFIGURABLE VARIABLES` near the top:
   * UNUSED_UV = Vector((-999, -999))
    The UV value assigned to UVs that don't get reached by the UV flow (for example, if they're above the start point and you have direction set to 'downwards'. It's recommended to delete unreached UVs because you can get fringing otherwise, but if you set this far away the fringes might be too small to see.
   * ANALYSIS_MODE = AnalysisMode.OMNIDIRECTIONAL
   Choose from AnalysisMode.UPWARDS, AnalysisMode.DOWNWARDS, or AnalysisMode.OMNIDIRECTIONAL for UVs that flow down (like a river), up (like a tree) or outwards (like ice patches)
   * HEIGHT_COMPARISON_THRESHOLD = 0.1
   On upwards or downwards mode, how much to allow vertices that are 'almost' up or 'almost' down (in worldspace units)
   * MAX_ITERATIONS = 999
   Crash protection hopefully :-) If it doesn't entirely complete, raise this as high as you need
1. Hit 'Run Script' and you should be good to go :-)
