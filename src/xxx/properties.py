import bpy
import json

pctx = "BakeNodeProp"

common_kwargs = {"translation_context": pctx}
if bpy.app.version < (4, 0, 0):
    common_kwargs = {}


class BakeTreeProps(bpy.types.PropertyGroup):
    tnum: bpy.props.IntProperty(name="Task Count", min=0, default=0, **common_kwargs)
    etask: bpy.props.StringProperty(name="Exe Task", default="", **common_kwargs)
    enode: bpy.props.StringProperty(name="Exe Node", default="", **common_kwargs)
    etask_p: bpy.props.FloatProperty(name="Task Progress",
                                     default=0.0,
                                     min=0,
                                     max=100,
                                     subtype="PERCENTAGE",
                                     **common_kwargs)
    enode_p: bpy.props.FloatProperty(name="Node Progress",
                                     default=0.0,
                                     min=0,
                                     max=100,
                                     subtype="PERCENTAGE",
                                     **common_kwargs)
    mat_preset_save_name: bpy.props.StringProperty(name="SaveName", default="", **common_kwargs)
    mat_name_as_save_name: bpy.props.BoolProperty(name="UseMatName", default=True, **common_kwargs)
    mat_preset_description: bpy.props.StringProperty(name="BakeTypeDescription", default="", **common_kwargs)

    _presets = []

    def preset_items(self, context):
        presets = []
        from .operators import BakeTreePresetsOps
        preset_path = BakeTreePresetsOps.get_preset_dir()
        for f in preset_path.glob("*.blend"):
            presets.append((f.as_posix(), f.stem, "", 0))
        self._presets.clear()
        self._presets.extend(presets)
        return self._presets
    preset: bpy.props.EnumProperty(items=preset_items)
    preset_save_name: bpy.props.StringProperty(name="SaveName", default="", **common_kwargs)


class BakeParam(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", default="", **common_kwargs)
    dname: bpy.props.StringProperty(name="Display Name", default="", **common_kwargs)
    vname: bpy.props.StringProperty(name="Value Name", default="", **common_kwargs)
    node: bpy.props.StringProperty(name="Node", default="", **common_kwargs)
    data_path: bpy.props.StringProperty(name="DataPath", default="", **common_kwargs)
    type: bpy.props.EnumProperty(name="Type",
                                 items=[
                                     ("BOOLEAN", "Bool", "", 0),
                                     ("INT", "Int", "", 1),
                                     ("FLOAT", "Float", "", 2),
                                     ("COLOR", "Color", "", 3),
                                     ("VECTOR", "Vector", "", 4),
                                     ("RGBA", "RGBA", "", 5),
                                     ("VALUE", "Value", "", 6),
                                 ],
                                 **common_kwargs)
    config: bpy.props.StringProperty(name="Config", default="{}", **common_kwargs)

    def dump(self):
        data = {
            "name": self.vname,
            "display_name": self.dname,
            "node": self.node,
            "data_path": self.data_path,
            "type": self.type,
            **json.loads(self.config)
        }
        return data
