#!/usr/bin/env python3

import sys, os

if 'bpy' not in sys.modules:
    assert len(sys.argv) == 2
    os.execlp('blender', 'blender', '--background', sys.argv[1], '--python', sys.argv[0])
else:
    from pathlib import Path
    import json, typing
    from dataclasses import dataclass
    import bpy, mathutils

    C = bpy.context
    D = bpy.data

    # Dumps a blendfile into a json representation. This representation can then
    # be used to diff between two versions of a blendfile, which is useful when
    # combined with a VCS. Unfortunately, the result is way too verbose to be
    # useful.
    class BlendEncoder(json.JSONEncoder):
        def default(self, obj):
            if any(isinstance(obj, t) for t in (
                    bpy.types.Screen, bpy.types.WindowManager, bpy.types.WorkSpace,
                    bpy.types.Depsgraph, bpy.types.ImagePreview, bpy.types.Brush,
                    bpy.types.Collection, bpy.types.Image, bpy.types.FreestyleLineStyle,
                    bpy.types.ShaderNodeTree
            )):
                return '<SKIPPED>'

            elif isinstance(obj, bpy.types.bpy_struct):
                return {
                    k: getattr(obj, k) for k in dir(obj)
                    if not k.startswith('__')
                        and not k.startswith('bl_')
                        and not k.startswith('rna_')
                        and not k.startswith('users_')
                        and not callable(getattr(obj, k))
                        and k not in ('id_data', 'original', 'brushes')
                }

            elif isinstance(obj, bpy.types.bpy_prop_collection):
                return obj.items()

            elif (isinstance(obj, bpy.types.bpy_prop_array)
                or isinstance(obj, set)
            ):
                return list(obj)

            elif (isinstance(obj, mathutils.Color)
                or isinstance(obj, mathutils.Vector)
                or isinstance(obj, mathutils.Matrix)
                or isinstance(obj, mathutils.Euler)
                or isinstance(obj, mathutils.Quaternion)
                or isinstance(obj, range)
            ):
                return str(obj)

            else:
                return super().default(obj)

    json.dump(D, sys.stdout, cls=BlendEncoder, indent=2, sort_keys=True)
