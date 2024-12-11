import bpy
from .node_tree import TREE_TYPE

owner = object()


def checker():
    for tree in bpy.data.node_groups:
        if tree.bl_idname != TREE_TYPE:
            continue
        tree.initialize()


@bpy.app.handlers.persistent
def reg_checker(_):
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.SpaceNodeEditor, "node_tree"),
        owner=owner,
        args=(),
        notify=checker,
        options={"PERSISTENT"},
    )


def hanlder_reg():
    bpy.app.handlers.load_post.append(reg_checker)


def hanlder_unreg():
    bpy.app.handlers.load_post.remove(reg_checker)
    bpy.msgbus.clear_by_owner(owner)
