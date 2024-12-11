# Ref: https://github.com/franMarz/TexTools-Blender
import bpy
import sys
import json
import bmesh
from mathutils import Color
from pathlib import Path


class _Run:
    elementsCount = 0

    def __init__(self, config, mesh_pair, cat, bake_pass, run_params=None) -> None:
        self.load_run_params(run_params)
        self.prepare(config, mesh_pair, cat, bake_pass)

    def prepare(self, config, mesh_pair, cat, bake_pass):
        preset_path = Path(__file__).parent.joinpath("advanced")
        cpath = preset_path.joinpath(bake_pass).with_suffix(".json")
        if not cpath.exists():
            sys.stdout.write(f"[ERROR]: {cpath} not found")
            return
        jconfig = json.loads(cpath.read_text())
        name = jconfig.get("Name", bake_pass)
        mtl_name = jconfig.get("Material", name)
        # params = jconfig.get("Params", {})
        act_mtl: bpy.types.Material = bpy.data.materials[mtl_name]
        dst, src, _uv = mesh_pair
        dst_obj: bpy.types.Object = bpy.data.objects.get(dst)
        src_obj: bpy.types.Object = bpy.data.objects.get(src)
        self.assign_vertex_color(dst_obj)
        self.setup_vertex_color_id_element(dst_obj)

    def load_run_params(self, run_params):
        if not run_params:
            return
        if not isinstance(run_params, dict):
            return
        _Run.elementsCount = run_params.get("elementsCount", 0)

    def clear(self):
        run_params = json.dumps({"elementsCount": _Run.elementsCount})
        sys.stderr.write(f"[RUN_PARAMS]: {run_params}")
        sys.stderr.flush()

    def __del__(self):
        self.clear()

    def assign_vertex_color(self, obj: bpy.types.Object):
        if len(obj.data.vertex_colors) > 0:
            vclsNames = [vcl.name for vcl in obj.data.vertex_colors]
            if 'TexTools_temp' in vclsNames:
                obj.data.vertex_colors['TexTools_temp'].active = True
                obj.data.vertex_colors['TexTools_temp'].active_render = True
            else:
                obj.data.vertex_colors.new(name='TexTools_temp')
                obj.data.vertex_colors['TexTools_temp'].active = True
                obj.data.vertex_colors['TexTools_temp'].active_render = True
        else:
            obj.data.vertex_colors.new(name='TexTools_temp')
            obj.data.vertex_colors['TexTools_temp'].active = True
            obj.data.vertex_colors['TexTools_temp'].active_render = True

    def setup_vertex_color_id_element(self, obj: bpy.types.Object):
        if not obj:
            return
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(state=True, view_layer=None)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

        bm = bmesh.from_edit_mesh(obj.data)

        if bpy.app.version >= (3, 4):
            colorLayerIndex = obj.data.attributes.active_color_index
            colorLayer = bm.loops.layers.color[colorLayerIndex]
        else:
            colorLayer = bm.loops.layers.color.active

        # Collect elements
        processed = set([])
        groups = []
        for face in bm.faces:
            if face not in processed:
                bpy.ops.mesh.select_all(action='DESELECT')
                face.select = True
                bpy.ops.mesh.select_linked(delimit={'NORMAL'})
                linked = [face for face in bm.faces if face.select]

                for link in linked:
                    processed.add(link)
                groups.append(linked)
        # Color each groupn
        for i in range(0, len(groups)):
            color = self.get_color_id(_Run.elementsCount + i, 256, jitter=True)
            color = self.safe_color(color)
            for face in groups[i]:
                for loop in face.loops:
                    loop[colorLayer] = color

        _Run.elementsCount += len(groups)

        obj.data.update()
        bpy.ops.object.mode_set(mode='OBJECT')

    def get_color_id(self, index, count, jitter=False) -> Color:
        # Get unique color
        color = Color()
        indexList = [0, 171, 64, 213, 32, 96, 160, 224, 16, 48, 80, 112, 144, 176, 208, 240, 8, 24, 40, 56, 72, 88, 104,
                     120, 136, 152, 168, 184, 200, 216, 232, 248, 4, 12, 20, 28, 36, 44, 52, 60, 68, 76, 84, 92, 100, 108, 116, 124,
                     132, 140, 148, 156, 164, 172, 180, 188, 196, 204, 212, 220, 228, 236, 244, 252, 2, 6, 10, 14, 18, 22, 26, 30, 34,
                     38, 42, 46, 50, 54, 58, 62, 66, 70, 74, 78, 82, 86, 90, 94, 98, 102, 106, 110, 114, 118, 122, 126, 130, 134, 138,
                     142, 146, 150, 154, 158, 162, 166, 170, 174, 178, 182, 186, 190, 194, 198, 202, 206, 210, 214, 218, 222, 226, 230,
                     234, 238, 242, 246, 250, 254, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43,
                     45, 47, 49, 51, 53, 55, 57, 59, 61, 63, 65, 67, 69, 71, 73, 75, 77, 79, 81, 83, 85, 87, 89, 91, 93, 95, 97, 99, 101,
                     103, 105, 107, 109, 111, 113, 115, 117, 119, 121, 123, 125, 127, 129, 131, 133, 135, 137, 139, 141, 143, 145, 147,
                     149, 151, 153, 155, 157, 159, 161, 163, 165, 167, 169, 128, 173, 175, 177, 179, 181, 183, 185, 187, 189, 191, 193,
                     195, 197, 199, 201, 203, 205, 207, 209, 211, 192, 215, 217, 219, 221, 223, 225, 227, 229, 231, 233, 235, 237, 239,
                     241, 243, 245, 247, 249, 251, 253, 255]

        i = 0
        if index > 255:
            while index > 255:
                index -= 256
                i += 1

        if jitter:
            color.hsv = ((indexList[index] + 1 / (2**i)) / 256), 0.9, 1.0
        else:
            color.hsv = (index / (count)), 0.9, 1.0

        return color

    def safe_color(self, color):
        if len(color) == 3:
            if bpy.app.version > (2, 80, 0):
                # Newer blender versions use RGBA
                return *color[:3], 1
            else:
                return color
        elif len(color) == 4:
            if bpy.app.version > (2, 80, 0):
                # Newer blender versions use RGBA
                return color
            else:
                return color[:3]
        return color
