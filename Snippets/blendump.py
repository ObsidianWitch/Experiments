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

    # Facilitates debugging by storing a path alongside its data.
    @dataclass
    class ToEncode:
        path: Path
        data: typing.Any

    # Dumps a blendfile into a json representation. The goal was to version
    # blendfiles with git and be able to diff between them with this script.
    # Unfortunately, the result is way too verbose to be useful.
    class BlendEncoder(json.JSONEncoder):
        def default(self, obj):
            print(obj) # DEBUG

            if isinstance(obj, ToEncode):
                if isinstance(obj.data, bpy.types.NodeSocket):
                    return obj.__repr__() # TODO

                elif (isinstance(obj.data, bpy.types.Screen)
                    or isinstance(obj.data, bpy.types.WindowManager)
                    or isinstance(obj.data, bpy.types.WorkSpace)
                    or isinstance(obj.data, bpy.types.Depsgraph)
                ):
                    return '<SKIPPED>'

                elif isinstance(obj.data, bpy.types.bpy_struct):
                    return {
                        name: ToEncode(obj.path / str(name), getattr(obj.data, name))
                        for name in dir(obj.data)
                        if not name.startswith('__')
                           and not callable(getattr(obj.data, name))
                           and name not in ('bl_rna', 'rna_type', 'id_data', 'original')
                    }

                elif isinstance(obj.data, bpy.types.bpy_prop_collection):
                    return { k: ToEncode(obj.path / str(k), v) for k, v in obj.data.items() }

            else:
                return super().default(obj)

    print(json.dumps(ToEncode(Path('/bpy/data'), D), cls=BlendEncoder, check_circular=True, sort_keys=True, indent=2))
