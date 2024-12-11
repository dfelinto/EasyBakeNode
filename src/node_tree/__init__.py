import bpy
from nodeitems_utils import register_node_categories, unregister_node_categories
from .node_sockets import SocketBase
from .nodes import NodeBase, CustomPass, SingleMeshConfig, MeshConfig
from .node_tree import TREE_NAME, TNodeTree, TNodeCategory, TNodeItem
from .executor import TaskExecutor
from .handler import hanlder_reg, hanlder_unreg

node_clss = [nc for nc in NodeBase.__subclasses__() if nc.__name__ != "CustomPass"]
clss = [TNodeTree, SingleMeshConfig, MeshConfig, *SocketBase.__subclasses__(), *node_clss]

cls_reg, cls_unreg = bpy.utils.register_classes_factory(clss)


def compile_node_categories():
    cat: dict[str, list[TNodeItem]] = {}
    for n in NodeBase.__subclasses__():
        if n.exclude:
            continue
        if n.category not in cat:
            cat[n.category] = []
        cat[n.category].append(TNodeItem(n.__name__))
    return [TNodeCategory(k, k, items=v) for k, v in cat.items()]


def register():
    cls_reg()
    CustomPass.reg()
    cat = compile_node_categories()
    register_node_categories(TREE_NAME, cat)
    hanlder_reg()


def unregister():
    hanlder_unreg()
    unregister_node_categories(TREE_NAME)
    cls_unreg()
    CustomPass.unreg()
