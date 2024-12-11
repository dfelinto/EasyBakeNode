import bpy


def get_package() -> str:
    return ".".join(__package__.split(".")[:-2])


class AddonPreference(bpy.types.AddonPreferences):
    bl_idname = get_package()
    bl_translation_context = "BakeNodePref"

    def update_default_bake_resolution(self, context):
        # 保持为32的倍数
        dbrx = (self.default_bake_resolution[0] // 32) * 32
        dbry = (self.default_bake_resolution[1] // 32) * 32
        if dbrx != self.default_bake_resolution[0]:
            self.default_bake_resolution[0] = dbrx
        if dbry != self.default_bake_resolution[1]:
            self.default_bake_resolution[1] = dbry

    default_bake_resolution: bpy.props.IntVectorProperty(name="Default Bake Resolution",
                                                         size=2,
                                                         step=32,
                                                         default=(512, 512),
                                                         min=32,
                                                         max=16384,
                                                         update=update_default_bake_resolution,
                                                         translation_context="BakeNodePref")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "default_bake_resolution")


def get_pref() -> AddonPreference:
    return bpy.context.preferences.addons[get_package()].preferences
