import bpy
import sys
import argparse
import numpy as np
import platform
import traceback
import json
from mathutils import Vector
from multiprocessing import shared_memory, resource_tracker
from ast import literal_eval as eval
from pathlib import Path
sys.path.append(Path(__file__).parent.as_posix())
from common import TreeCtx

ONE = Vector((1, 1, 1))


def find_from_node(socket: bpy.types.NodeSocket) -> bpy.types.Node:
    if not socket.is_linked:
        return None
    node: bpy.types.Node = socket.links[0].from_node
    if node.bl_idname != "NodeReroute":
        return node
    return find_from_node(node.inputs[0])


def init_scene(sce: bpy.types.Scene):
    sce.render.image_settings.file_format = "PNG"
    sce.render.image_settings.color_depth = "16"
    sce.render.image_settings.color_mode = "RGBA"
    sce.render.image_settings.compression = 100
    sce.render.use_overwrite = True


def write_to_shm(sm_name, img: bpy.types.Image):
    if not sm_name:
        return
    try:
        sm = shared_memory.SharedMemory(name=sm_name, create=False)
        pixels = np.ndarray((*img.size, img.channels), dtype=np.float32, buffer=sm.buf)
        img.pixels.foreach_get(pixels.ravel())
        if platform.system() != "Windows":
            resource_tracker.unregister(sm._name, "shared_memory")
        sm.close()
    except Exception as e:
        sys.stdout.write(f"Failed to get shared memory: {e}")
        sys.stdout.flush()


def create_img_node(name, res, mat: bpy.types.Material):
    img: bpy.types.Image = bpy.data.images.new(name=name,
                                               width=res[0],
                                               height=res[1],
                                               alpha=True)
    img_node = mat.node_tree.nodes.new("ShaderNodeTexImage")
    img_node.image = img
    img_node.select = True
    mat.node_tree.nodes.active = img_node
    return img_node


def prepare_pbr_mat(nt, lhs_node, rhs_inp, bake_pass):
    if not lhs_node:
        return
    if lhs_node.bl_idname == "ShaderNodeBsdfPrincipled":
        lhs_inp = lhs_node.inputs[bake_pass]
        fdv_type = lhs_inp.type
        tdv_type = rhs_inp.type
        if lhs_inp.is_linked:
            nt.links.new(lhs_inp.links[0].from_socket, rhs_inp)
        elif (tdv_type, fdv_type) == ("VALUE", "VECTOR"):
            rhs_inp.default_value = lhs_inp.default_value[0]
        elif (tdv_type, fdv_type) == ("RGBA", "VECTOR"):
            rhs_inp.default_value[:3] = lhs_inp.default_value
        elif (tdv_type, fdv_type) == ("VALUE", "RGBA"):
            rhs_inp.default_value = lhs_inp.default_value[0]
        elif (tdv_type, fdv_type) == ("RGBA", "VALUE"):
            rhs_inp.default_value[:3] = ONE * lhs_inp.default_value
        else:
            try:
                rhs_inp.default_value = lhs_inp.default_value
            except Exception as e:
                sys.stdout.write(f"[WARN]: {rhs_inp.name} <- {lhs_inp.name}\n")
                sys.stdout.write(f"[WARN]: {e}\n")
    elif lhs_node.bl_idname in {"ShaderNodeMixShader", "ShaderNodeAddShader"}:
        mix_rgb = nt.nodes.new("ShaderNodeMixRGB")
        mix_rgb.location = lhs_node.location
        mix_rgb.location.y -= lhs_node.height

        mix_rgb.blend_type = "MIX"
        if lhs_node.bl_idname == "ShaderNodeMixShader":
            lhs_inp = lhs_node.inputs[0]
            mix_rgb.inputs[0].default_value = lhs_inp.default_value
            if lhs_inp.is_linked:
                nt.links.new(lhs_inp.links[0].from_socket, mix_rgb.inputs[0])
            fnode1 = find_from_node(lhs_node.inputs[1])
            fnode2 = find_from_node(lhs_node.inputs[2])
        elif lhs_node.bl_idname == "ShaderNodeAddShader":
            mix_rgb.blend_type = "ADD"
            fnode1 = find_from_node(lhs_node.inputs[0])
            fnode2 = find_from_node(lhs_node.inputs[1])

        prepare_pbr_mat(nt, fnode1, mix_rgb.inputs[1], bake_pass)
        prepare_pbr_mat(nt, fnode2, mix_rgb.inputs[2], bake_pass)
        nt.links.new(mix_rgb.outputs[0], rhs_inp)


def bake_pbr(config, mesh_pair, cat, bake_pass):
    ctx = config.get("ctx", {})
    bake_settings = ctx.get("BakeSettings", {})

    sce = bpy.context.scene
    sce.render.bake_samples = bake_settings.get("bake_samples", 1)
    sce.cycles.samples = bake_settings.get("samples", 1)
    init_scene(sce)
    dst, src, _uv = mesh_pair
    bpy.ops.object.select_all(action="DESELECT")

    dst_obj: bpy.types.Object = bpy.data.objects[dst]
    if _uv and _uv in dst_obj.data.uv_layers:
        dst_obj.data.uv_layers.active_index = dst_obj.data.uv_layers.find(_uv)
    else:
        old_uv_id = dst_obj.data.uv_layers.active_index
        dst_obj.data.uv_layers.active_index = bake_settings.get("uv_layer", old_uv_id)
    bpy.context.view_layer.objects.active = dst_obj
    dst_obj.select_set(True)
    act_mtl: bpy.types.Material = dst_obj.active_material
    if not act_mtl:
        return

    src_obj: bpy.types.Object = bpy.data.objects.get(src)
    if src_obj:
        src_obj.select_set(True)

    res = bake_settings.get("resolution", (512, 512))
    output = act_mtl.node_tree.get_output_node("ALL")
    if not output:
        sys.stdout.write("[ERROR]: No output node found")
        return
    inp = output.inputs[0]
    from_node: bpy.types.Node = find_from_node(inp)
    if not from_node:
        sys.stdout.write("[ERROR]: No from node found")
        return
    nt = act_mtl.node_tree
    emit = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(output.inputs[0], emit.outputs[0])
    final_bake_pass = "EMIT"
    if bake_pass == "Albedo":
        prepare_pbr_mat(nt, from_node, emit.inputs["Color"], "Base Color")
    elif bake_pass == "Metallic":
        prepare_pbr_mat(nt, from_node, emit.inputs["Color"], "Metallic")
    elif bake_pass == "Roughness":
        prepare_pbr_mat(nt, from_node, emit.inputs["Color"], "Roughness")
    elif bake_pass == "Normal":
        # prepare_pbr_mat(nt, from_node, emit.inputs["Color"], "Normal")
        final_bake_pass = "NORMAL"
    elif bake_pass == "Emission":
        ...
    elif bake_pass == "AO":
        final_bake_pass = "AO"
        sce.cycles.samples = max(sce.cycles.samples, 32)
    elif bake_pass == "IOR":
        prepare_pbr_mat(nt, from_node, emit.inputs["Strength"], "IOR")

    res = bake_settings.get("resolution", (512, 512))
    img_node = create_img_node(f"{dst}_{cat}_{bake_pass}", res, act_mtl)
    act_mtl.node_tree.nodes.active = img_node
    img_node.location = output.location
    img_node.location.y -= output.height
    emit.location = output.location
    emit.location.y += output.height
    bpy.ops.object.bake(type=final_bake_pass, save_mode="INTERNAL")
    sys.stdout.flush()
    write_to_shm(config.get("shm_name", ""), img_node.image)
    # bpy.ops.wm.save_as_mainfile(filepath="/Users/karrycharon/Desktop/Blend Project/Bake-Node-Test-Export.blend", copy=True)


def bake_advanced(config, mesh_pair, cat, bake_pass):
    ctx = config.get("ctx", {})
    preset_path = Path(__file__).parent.joinpath("advanced")
    cpath = preset_path.joinpath(bake_pass).with_suffix(".json")
    if not cpath.exists():
        sys.stdout.write(f"[ERROR]: {cpath} not found")
        return
    # 配置解析
    jconfig = json.loads(cpath.read_text())
    {'Name': 'Position', 'Material': 'Position', 'Run': 'run.py', 'BakeType': 'EMIT', 'Params': {}, 'Description': ''}
    name = jconfig.get("Name", bake_pass)
    mtl_name = jconfig.get("Material", name)
    final_bake_pass = jconfig.get("BakeType", "EMIT")
    params = jconfig.get("Params", {})

    # load阶段
    blend = preset_path.joinpath(f"{name}.blend").as_posix()
    with bpy.data.libraries.load(blend) as (df, dt):
        if not df.materials:
            sys.stderr.write("[ERROR]: No materials found")
            return
        if mtl_name not in df.materials:
            mtl_name = df.materials[0]
        dt.materials = [mtl_name]
    act_mtl = bpy.data.materials[mtl_name]

    # 参数设置阶段
    def value_set(obj, path: str, value) -> None:
        p, path_attr = obj, path
        if "." in path_attr:
            path_prop, path_attr = path.rsplit(".", 1)
            p = obj.path_resolve(path_prop)
        setattr(p, path_attr, value)
    bake_params_set = ctx.get("AdvancedBakeParams", {})
    bake_params = bake_params_set.get(bake_pass, {})
    for pname, pvalue in bake_params.items():
        data_path = params.get(pname, {}).get("data_path", "")
        value_set(act_mtl, data_path, pvalue)

    # prepare阶段
    script_name = jconfig.get("Run", "")
    run_py = preset_path.joinpath(script_name)
    if script_name and run_py.exists():
        exec(run_py.read_text(), globals())
        _Run = globals().get("_Run")
        try:
            _Run(config, mesh_pair, cat, bake_pass, config.get("run_params", {}))
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write(f"[ERROR]: {e}")
            sys.stderr.flush()
    # bpy.ops.wm.save_as_mainfile(filepath="/Users/karrycharon/Desktop/Blend Project/Bake-Node-Test-Export.blend", copy=True)
    # bake阶段
    bake_settings = ctx.get("BakeSettings", {})
    dst, src, _uv = mesh_pair
    dst_obj: bpy.types.Object = bpy.data.objects[dst]
    if _uv and _uv in dst_obj.data.uv_layers:
        dst_obj.data.uv_layers.active_index = dst_obj.data.uv_layers.find(_uv)
    else:
        old_uv_id = dst_obj.data.uv_layers.active_index
        dst_obj.data.uv_layers.active_index = bake_settings.get("uv_layer", old_uv_id)
    bpy.context.view_layer.objects.active = dst_obj
    dst_obj.select_set(True)
    if not act_mtl:
        return
    dst_obj.active_material = act_mtl
    for i in range(len(dst_obj.data.materials)):
        dst_obj.data.materials[i] = act_mtl
    src_obj: bpy.types.Object = bpy.data.objects.get(src)
    if src_obj:
        src_obj.select_set(True)

    res = bake_settings.get("resolution", (512, 512))
    img_node = create_img_node(f"{dst}_{cat}_{bake_pass}", res, act_mtl)
    act_mtl.node_tree.nodes.active = img_node
    bpy.ops.object.bake(type=final_bake_pass, save_mode="INTERNAL")
    sys.stdout.flush()
    write_to_shm(config.get("shm_name", ""), img_node.image)


def bake_internal(config, mesh_pair, cat, bake_pass):
    ctx = config.get("ctx", {})
    bake_settings = ctx.get("BakeSettings", {})

    sce = bpy.context.scene
    sce.render.bake_samples = bake_settings.get("bake_samples", 1)
    sce.cycles.samples = bake_settings.get("samples", 1)
    if bake_pass in {"AO", "DIFFUSE", "GLOSSY"}:
        sce.cycles.samples = max(sce.cycles.samples, 32)
    init_scene(sce)

    dst, src, _uv = mesh_pair
    bpy.ops.object.select_all(action="DESELECT")

    dst_obj: bpy.types.Object = bpy.data.objects[dst]
    if _uv and _uv in dst_obj.data.uv_layers:
        dst_obj.data.uv_layers.active_index = dst_obj.data.uv_layers.find(_uv)
    else:
        old_uv_id = dst_obj.data.uv_layers.active_index
        dst_obj.data.uv_layers.active_index = bake_settings.get("uv_layer", old_uv_id)
    bpy.context.view_layer.objects.active = dst_obj
    dst_obj.select_set(True)
    act_mtl: bpy.types.Material = dst_obj.active_material
    if not act_mtl:
        return

    src_obj: bpy.types.Object = bpy.data.objects.get(src)
    if src_obj:
        src_obj.select_set(True)

    res = bake_settings.get("resolution", (512, 512))
    img_node = create_img_node(f"{dst}_{cat}_{bake_pass}", res, act_mtl)
    act_mtl.node_tree.nodes.active = img_node
    output = act_mtl.node_tree.get_output_node("ALL")
    if not output:
        sys.stdout.write("[ERROR]: No output node found")
        return
    img_node.location = output.location
    img_node.location.y -= output.height
    bpy.ops.object.bake(type=bake_pass, save_mode="INTERNAL")
    sys.stdout.flush()
    write_to_shm(config.get("shm_name", ""), img_node.image)


def bake(config):
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.device = "GPU"
    config = TreeCtx().load(config)
    bake_params = config.get("bake_params", [])
    if not bake_params:
        return
    mesh_pair, cat, bake_pass = bake_params
    if cat == "PBR":
        bake_pbr(config, mesh_pair, cat, bake_pass)
    elif cat == "Advanced":
        bake_advanced(config, mesh_pair, cat, bake_pass)
    else:
        bake_internal(config, mesh_pair, cat, bake_pass)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("-bnc", dest="config", type=str, default="{}")
    args = parser.parse_args(argv)
    config = args.config
    while isinstance(config, str):
        config = eval(config)
    try:
        bake(config)
    except Exception:
        sys.stdout.flush()
        trace_info = traceback.format_exc()
        sys.stdout.write(f"[ERROR]: {trace_info}\n")
        sys.stdout.flush()
