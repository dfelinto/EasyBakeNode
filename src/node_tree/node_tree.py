from __future__ import annotations
from bpy.types import NodeTree
from nodeitems_utils import NodeCategory, NodeItem
from contextlib import contextmanager
from threading import Lock, Thread
from .executor import TaskExecutor
from .common import TreeCtx
import bpy
import traceback

TREE_NAME = "BakeNodes"
TREE_TYPE = "BakeNodeTree"
TREE_TCTX = "BakeNodes"

CTX_LOCK = Lock()


class TNodeCategory(NodeCategory):

    @classmethod
    def poll(cls, context):
        return getattr(context.space_data, "tree_type", None) == TREE_TYPE


class TNodeItem(NodeItem):
    translation_context = TREE_TCTX

    # def draw(self, nodeitem, layout, context):
    #     col = layout.column()
    #     props = col.operator("node.add_node", text=self.label, text_ctxt=TREE_TCTX)
    #     props.type = self.nodetype
    #     props.use_transform = True


class TNodeTree(NodeTree):
    bl_idname = TREE_TYPE
    bl_label = "Bake Nodes"
    bl_icon = "NODETREE"

    freeze: bpy.props.BoolProperty(default=False, description="冻结 更新")

    initialized: bpy.props.BoolProperty(default=False, description="初始化")
    is_running: bpy.props.BoolProperty(default=False, description="正在运行")

    def initialize(self):
        if self.initialized:
            return
        self.initialized = True
        if self.nodes.__len__() > 0:
            return
        from .nodes import Bake, BakeSetting, Pass, SingleMesh, SaveToImage
        _bake = self.nodes.new(Bake.__name__)
        _bake_setting = self.nodes.new(BakeSetting.__name__)
        _pass = self.nodes.new(Pass.__name__)
        _single_mesh = self.nodes.new(SingleMesh.__name__)
        _save_to_image = self.nodes.new(SaveToImage.__name__)

        _pass.location = -340, 230
        _bake_setting.location = -340, -100
        _single_mesh.location = -340, -300
        _save_to_image.location = 340, 120

        self.links.new(_pass.outputs[0], _bake.inputs[0])
        self.links.new(_bake_setting.outputs[0], _bake.inputs[1])
        self.links.new(_single_mesh.outputs[0], _bake.inputs[2])
        self.links.new(_bake.outputs[0], _save_to_image.inputs[0])
        self.deselect_all()

    def initialize_ai(self):
        if self.initialized:
            return
        self.initialized = True
        if self.nodes.__len__() > 0:
            return
        from .nodes import Bake, BakeSetting, Pass, SingleMesh, AITexPreview
        _bake = self.nodes.new(Bake.__name__)
        _bake_setting = self.nodes.new(BakeSetting.__name__)
        _pass = self.nodes.new(Pass.__name__)
        _pass.name = "Pass"
        _pass.bake_passes = {"EMIT", }

        _single_mesh = self.nodes.new(SingleMesh.__name__)
        _single_mesh.name = "Mesh_Copy"
        _ai_tex_prev = self.nodes.new(AITexPreview.__name__)

        _pass.location = -340, 230
        _bake_setting.location = -340, -100
        _single_mesh.location = -340, -300
        _ai_tex_prev.location = 340, 120

        self.links.new(_pass.outputs[0], _bake.inputs[0])
        self.links.new(_bake_setting.outputs[0], _bake.inputs[1])
        self.links.new(_single_mesh.outputs[0], _bake.inputs[2])
        self.links.new(_bake.outputs[0], _ai_tex_prev.inputs[0])
        self.deselect_all()

    def deselect_all(self):
        for n in self.nodes:
            n.select = False

    def update(self):
        return

    @contextmanager
    def with_freeze(self):
        self.freeze = True
        try:
            yield
        except BaseException:
            traceback.print_exc()
        self.freeze = False

    def execute(self):
        from .executor import TaskExecutor
        task = self.dump()
        TaskExecutor.submit_task(task)

    @classmethod
    def execute_task(cls, executor: TaskExecutor, tasks):
        from .nodes import NodeBase
        for task_name, task in tasks.items():
            task: TreeCtx = TreeCtx().load(task)
            executor.set_current_tree(task_name)
            executor.clear_prefix()
            executor.warn("%s [Config]:", task_name)
            executor.push_log_prefix("\t| ")
            for cfg in task:
                executor.warn("%s: %s", cfg, task[cfg])
            res = {}
            executor.pop_log_prefix()
            executor.info("%s [Running]:", task_name)
            executor.push_log_prefix("\t| ")
            nodes = task.get("ExecutionQueue", [])
            for i, (nlabel, nname) in enumerate(nodes):
                bp = NodeBase.get_node_cls(nlabel)
                bp.nname = nname
                executor.update_tree_process(i / len(nodes))
                executor.set_exe_node(nname)
                res = bp.execute(executor, task, **res)

    def dump(self):
        ctx = TreeCtx()
        ctx["Tree"] = self
        for node in self.get_outputs():
            # 从输出节点开始
            self.reset_node()
            ctx[node.name] = TreeCtx()
            try:
                node.dump(ctx[node.name])
            except BaseException:
                # TODO 记录错误
                traceback.print_exc()
        return ctx

    def reset_node(self):
        for node in self.get_tnodes():
            node.is_dumped = False

    def get_tnodes(self) -> list[bpy.types.Node]:
        return [n for n in self.nodes if hasattr(n, "is_dumped")]

    def get_outputs(self) -> list[bpy.types.Node]:
        return [n for n in self.nodes if getattr(n, "is_output", False)]


def update_node_editor():
    try:
        import bpy
        for area in bpy.context.screen.areas:
            if area.ui_type != TREE_TYPE:
                continue
            area.tag_redraw()
    except Exception:
        ...
    return 0.1


bpy.app.timers.register(update_node_editor, persistent=True)
