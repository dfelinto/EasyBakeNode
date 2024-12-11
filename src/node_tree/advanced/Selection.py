# Ref: https://github.com/franMarz/TexTools-Blender
import bpy
import sys
import json
import bmesh
from mathutils import Color
from pathlib import Path


class _Run:
    def __init__(self, config, mesh_pair, cat, bake_pass, run_params=None) -> None:
        self.load_run_params(run_params)
        self.prepare(config, mesh_pair, cat, bake_pass)

    def prepare(self, config, mesh_pair, cat, bake_pass):
        dst = mesh_pair[0]
        dst_obj: bpy.types.Object = bpy.data.objects.get(dst)
        self.assign_vertex_color(dst_obj)
        self.setup_vertex_color_selection(dst_obj)

    def load_run_params(self, run_params):
        pass

    def clear(self):
        pass

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

    def setup_vertex_color_selection(self, obj: bpy.types.Object):
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(state=True, view_layer=None)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
        colorLayer = bm.loops.layers.color.active
        color_map = [self.safe_color((0, 0, 0, 1)), self.safe_color((1, 1, 1, 1))]
        for face in bm.faces:
            color = color_map[face.select]
            for loop in face.loops:
                loop[colorLayer] = color
        obj.data.update()
        bpy.ops.object.mode_set(mode='OBJECT')

    def safe_color(self, color) -> tuple:
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
