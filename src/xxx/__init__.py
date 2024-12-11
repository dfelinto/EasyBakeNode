import bpy
from .operators import (BakeTreeRun,
                        BakeSettingsPresetsOps,
                        SaveAsBakePresets,
                        MarkPropAsParams,
                        DeletePropFromParams,
                        DeleteBakePreset,
                        BakeTreePresetsOps,
                        PrefBakeSettingsPresetsOps,
                        )
from .panels import AIBakeTree, BakeTreePanel, BakeSettingPresets, PrefBakeSettingPresets, MatPanel, draw_node_prop
from .properties import BakeTreeProps, BakeParam
from .preference import AddonPreference


def register():
    bpy.utils.register_class(BakeTreeRun)
    bpy.utils.register_class(BakeSettingsPresetsOps)
    bpy.utils.register_class(SaveAsBakePresets)
    bpy.utils.register_class(MarkPropAsParams)
    bpy.utils.register_class(DeletePropFromParams)
    bpy.utils.register_class(DeleteBakePreset)
    bpy.utils.register_class(BakeTreePresetsOps)
    bpy.utils.register_class(PrefBakeSettingsPresetsOps)
    bpy.utils.register_class(AIBakeTree)
    bpy.utils.register_class(BakeTreePanel)
    bpy.utils.register_class(BakeSettingPresets)
    bpy.utils.register_class(PrefBakeSettingPresets)
    bpy.utils.register_class(MatPanel)
    bpy.utils.register_class(BakeTreeProps)
    bpy.utils.register_class(BakeParam)
    bpy.utils.register_class(AddonPreference)
    bpy.types.UI_MT_button_context_menu.append(draw_node_prop)
    bpy.types.WindowManager.bake_tree = bpy.props.PointerProperty(type=BakeTreeProps)
    bpy.types.Material.bake_params = bpy.props.CollectionProperty(type=BakeParam)


def unregister():
    del bpy.types.WindowManager.bake_tree
    bpy.types.UI_MT_button_context_menu.remove(draw_node_prop)
    bpy.utils.unregister_class(AddonPreference)
    bpy.utils.unregister_class(BakeTreeProps)
    bpy.utils.unregister_class(MatPanel)
    bpy.utils.unregister_class(PrefBakeSettingsPresetsOps)
    bpy.utils.unregister_class(BakeSettingPresets)
    bpy.utils.unregister_class(BakeTreePanel)
    bpy.utils.unregister_class(AIBakeTree)
    bpy.utils.unregister_class(PrefBakeSettingsPresetsOps)
    bpy.utils.unregister_class(BakeTreePresetsOps)
    bpy.utils.unregister_class(DeleteBakePreset)
    bpy.utils.unregister_class(DeletePropFromParams)
    bpy.utils.unregister_class(MarkPropAsParams)
    bpy.utils.unregister_class(SaveAsBakePresets)
    bpy.utils.unregister_class(BakeSettingsPresetsOps)
    bpy.utils.unregister_class(BakeTreeRun)
