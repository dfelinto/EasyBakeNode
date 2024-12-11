from typing import Set
from pathlib import Path
from bpy.types import Context, Event
from ...utils.logger import logger
from ..node_tree.node_tree import TREE_TYPE, TNodeTree
from ..node_tree.executor import TaskExecutor
import bpy
import json
OPS_CTX = "BakeNodeOps"


class BakeTreeRun(bpy.types.Operator):
    bl_idname = "bake_tree.run"
    bl_description = "Run Bake"
    bl_label = "Run Bake"
    bl_translation_context = OPS_CTX

    @classmethod
    def poll(cls, context: Context) -> bool:
        space = context.space_data
        return space.type == "NODE_EDITOR" and space.tree_type == TREE_TYPE

    def invoke(self, context: Context, event: Event) -> Set[int] | Set[str]:
        return self.execute(context)

    def execute(self, context):
        tree: TNodeTree = context.space_data.edit_tree
        if not tree:
            return {"CANCELLED"}
        task = tree.dump()
        TaskExecutor.submit_task(task)
        return {"FINISHED"}


class BakeSettingsPresetsOps(bpy.types.Operator):
    bl_idname = "bake_tree.bake_settings_presets"
    bl_label = "Bake Settings Presets"
    bl_description = "Bake Settings Presets"
    bl_translation_context = OPS_CTX

    resolution: bpy.props.IntVectorProperty(name="Resolution", size=2, default=(1024, 1024))

    def execute(self, context: Context):
        node = bpy.context.node
        node.resolution = self.resolution
        return {"FINISHED"}


class PrefBakeSettingsPresetsOps(bpy.types.Operator):
    bl_idname = "bake_tree.pref_bake_settings_presets"
    bl_label = "Bake Settings Presets"
    bl_description = "Bake Settings Presets"
    bl_translation_context = OPS_CTX

    resolution: bpy.props.IntVectorProperty(name="Resolution", size=2, default=(1024, 1024))

    def execute(self, context: Context):
        from .preference import get_pref
        get_pref().default_bake_resolution = self.resolution
        return {"FINISHED"}


class SaveAsBakePresets(bpy.types.Operator):
    bl_idname = "bake_tree.save_as_bake_presets"
    bl_label = "Save As Bake Presets"
    bl_description = "Save As Bake Presets"
    bl_translation_context = OPS_CTX

    def get_preset_dir(self):
        p = Path(__file__).parent.parent.joinpath("node_tree/advanced")
        p.mkdir(exist_ok=True)
        return p

    def invoke(self, context: Context, event: Event):
        wm = bpy.context.window_manager
        mtl = bpy.context.material
        if not mtl:
            self.report({"ERROR"}, "No material selected")
            return {"CANCELLED"}
        tree_prop = wm.bake_tree
        preset_name = tree_prop.mat_preset_save_name
        if tree_prop.mat_name_as_save_name:
            preset_name = mtl.name
        presets_dir = self.get_preset_dir()
        config = presets_dir.joinpath(preset_name).with_suffix(".json")
        # 如果config存在则弹出确认覆盖提示
        if config.exists():
            return wm.invoke_confirm(self, event)
        return self.execute(context)

    def draw(self, context: Context):
        # 如果config存在则弹出确认覆盖提示
        layout = self.layout
        layout.label(text="Preset already exists, overwrite?")

    def execute(self, context: Context):
        mtl = bpy.context.material
        if not mtl:
            self.report({"ERROR"}, "No material selected")
            return {"CANCELLED"}
        tree_prop = context.window_manager.bake_tree
        preset_name = tree_prop.mat_preset_save_name
        if tree_prop.mat_name_as_save_name:
            preset_name = mtl.name
        description = tree_prop.mat_preset_description
        if not preset_name:
            self.report({"ERROR"}, "No preset name")
            return {"CANCELLED"}
        old_mtl_name = mtl.name
        mtl.name = old_mtl_name + "_bak"
        copy_mtl = mtl.copy()
        copy_mtl.name = preset_name
        presets_dir = self.get_preset_dir()
        blend_path = presets_dir.joinpath(preset_name).with_suffix(".blend")
        bpy.data.libraries.write(blend_path.as_posix(), {copy_mtl}, fake_user=True)
        params = {}
        for pname, prop in mtl.bake_params.items():
            params[pname] = prop.dump()
        config = {
            "Name": preset_name,
            "Material": copy_mtl.name,
            "Run": "run.py",
            "BakeType": bpy.context.scene.cycles.bake_pass,
            "Params": params,
            "Description": description
        }
        bpy.data.materials.remove(copy_mtl)
        mtl.name = old_mtl_name
        config_path = presets_dir.joinpath(preset_name).with_suffix(".json")
        config_path.write_text(json.dumps(config, indent=4, ensure_ascii=False))
        from ..node_tree.nodes import CustomPass
        CustomPass.reload_node()
        return {"FINISHED"}


class DeleteBakePreset(bpy.types.Operator):
    bl_idname = "bake_tree.delete_bake_preset"
    bl_label = "Delete Bake Preset"
    bl_description = "Delete Bake Preset"
    bl_translation_context = OPS_CTX

    preset_to_delete: bpy.props.StringProperty()

    def get_preset_dir(self):
        p = Path(__file__).parent.parent.joinpath("node_tree/advanced")
        p.mkdir(exist_ok=True)
        return p

    def execute(self, context: Context):
        p = self.get_preset_dir()
        if not p.exists():
            return {"CANCELLED"}
        for file in p.glob(f"{self.preset_to_delete}*"):
            if file.stem != self.preset_to_delete:
                continue
            try:
                file.unlink()
            except Exception:
                pass
        from ..node_tree.nodes import CustomPass
        CustomPass.reload_node()
        return {"FINISHED"}


class MarkPropAsParams(bpy.types.Operator):
    bl_idname = "bake_tree.mark_prop_as_params"
    bl_label = "Mark Prop As Params"
    bl_description = "Mark Prop As Params"
    bl_translation_context = OPS_CTX

    def execute(self, context: Context):
        node = getattr(bpy.context, "node", None)
        if not node:
            self.report({"ERROR"}, "No node selected")
            return {"CANCELLED"}
        self.mark_socket_prop()
        return {"FINISHED"}

    def mark_socket_prop(self):
        context = bpy.context
        mtl = context.material
        node = getattr(bpy.context, "node", None)
        socket = context.socket
        bpy.ops.ui.copy_data_path_button("INVOKE_DEFAULT")
        data_path = context.window_manager.clipboard

        prop_path, prop_attr = data_path.rsplit(".", 1)
        prop_from = mtl.path_resolve(prop_path)
        prop_rna = prop_from.bl_rna.properties[prop_attr]

        sel_prop = bpy.context.property
        name = socket.identifier
        if sel_prop[1] == "default_value":
            params_name = f"{node.name}:['{socket.identifier}']"
            ptype = socket.type
        else:
            params_name = f"{node.name}:['{sel_prop[1]}']"
            name = sel_prop[1]
            ptype = prop_rna.type

        param = mtl.bake_params.get(params_name)
        if params_name not in mtl.bake_params:
            param = mtl.bake_params.add()
            param.name = params_name
        param.node = node.name
        param.data_path = data_path
        param.type = ptype
        param.vname = name
        param.dname = name
        config = {}
        prop_value = getattr(prop_from, prop_attr)
        if ptype == "RGBA":
            config["default"] = prop_value[:]
        elif ptype == "VECTOR":
            config["default"] = prop_value[:]
        else:
            config["default"] = prop_value

        if ptype in {"INT", "FLOAT"}:
            config["min"] = prop_rna.soft_min
            config["max"] = prop_rna.soft_max
            config["step"] = prop_rna.step
        param.config = json.dumps(config, indent=4, ensure_ascii=False)


class DeletePropFromParams(bpy.types.Operator):
    bl_idname = "bake_tree.delete_prop_from_params"
    bl_label = "Delete Prop From Params"
    bl_description = "Delete Prop From Params"
    bl_translation_context = OPS_CTX

    action: bpy.props.EnumProperty(name="Action",
                                   items=(
                                       ("ONE", "One", ""),
                                       ("ALL", "All", ""),
                                   ),
                                   default="ONE",
                                   )
    prop_to_del: bpy.props.StringProperty(default="", name="Prop To Del")

    def execute(self, context: Context):
        mtl = bpy.context.material
        if self.action == "ALL":
            mtl.bake_params.clear()
            return {"FINISHED"}
        it = mtl.bake_params.find(self.prop_to_del)
        if it == -1:
            self.report({"ERROR"}, "Prop not found")
            return {"CANCELLED"}
        mtl.bake_params.remove(it)
        return {"FINISHED"}


class BakeTreePresetsOps(bpy.types.Operator):
    bl_idname = "bake_tree.bake_tree_presets_ops"
    bl_label = "Bake Tree Presets Operators"
    bl_translation_context = OPS_CTX

    action: bpy.props.EnumProperty(name="Action",
                                   items=(
                                       ("SAVE", "Save", ""),
                                       ("DEL", "Delete", ""),
                                       ("LOAD", "Load", ""),
                                   ),
                                   default="SAVE",
                                   )

    def draw(self, context: Context):
        layout = self.layout
        if self.action == "SAVE":
            layout.label(text="Preset Already Exists, Overwrite?")
        elif self.action == "DEL":
            layout.label(text="Delete Preset?")

    def invoke(self, context: Context, event: Event):
        preset_dir = self.get_preset_dir()
        if self.action == "SAVE":
            tree: TNodeTree = context.space_data.edit_tree
            if not tree:
                return {"CANCELLED"}
            save_name = context.window_manager.bake_tree.preset_save_name
            if not save_name:
                self.report({"ERROR"}, "Preset Name is Empty")
                return {"CANCELLED"}
            save_path = preset_dir.joinpath(save_name).with_suffix(".blend")
            if save_path.exists():
                return context.window_manager.invoke_props_dialog(self, width=200)
        elif self.action == "DEL":
            return context.window_manager.invoke_props_dialog(self, width=200)
        return self.execute(context)

    def execute(self, context: Context):
        if self.action == "SAVE":
            self.save_preset()
        elif self.action == "DEL":
            self.del_preset()
        elif self.action == "LOAD":
            self.load_preset()
        self.action = "SAVE"
        return {"FINISHED"}

    def save_preset(self):
        tree: TNodeTree = bpy.context.space_data.edit_tree
        if not tree:
            return {"CANCELLED"}
        save_name = bpy.context.window_manager.bake_tree.preset_save_name
        preset_dir = self.get_preset_dir()
        save_path = preset_dir.joinpath(save_name).with_suffix(".blend")
        save_path.unlink(missing_ok=True)
        bpy.data.libraries.write(save_path.as_posix(), {tree})

    def del_preset(self):
        if not bpy.context.window_manager.bake_tree.preset:
            self.report({"ERROR"}, "Preset is Empty")
            return
        del_path = Path(bpy.context.window_manager.bake_tree.preset)
        if del_path.is_file():
            del_path.unlink(missing_ok=True)

    def load_preset(self):
        load_path = Path(bpy.context.window_manager.bake_tree.preset)
        if not load_path.exists():
            self.report({"ERROR"}, "Preset not found")
            return {"CANCELLED"}
        old_trees = set(bpy.data.node_groups)
        with bpy.data.libraries.load(load_path.as_posix()) as (df, dt):
            dt.node_groups = df.node_groups[:]
        new_trees = set(bpy.data.node_groups) - old_trees
        if not new_trees:
            self.report({"ERROR"}, "No node trees found in preset")
            return
        tree = new_trees.pop()
        if tree.bl_idname == TREE_TYPE:
            bpy.context.space_data.node_tree = tree
        else:
            self.report({"ERROR"}, "Preset is not a bake tree")

    @staticmethod
    def get_preset_dir() -> Path:
        p = Path(__file__).parent.parent.parent.joinpath("presets/tree")
        p.mkdir(parents=True, exist_ok=True)
        return p
