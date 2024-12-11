from bpy.types import Context, Node, NodeSocket, UILayout


class SocketBase(NodeSocket):
    ...


class Pass(SocketBase):
    bl_idname = "Pass"

    def draw(self, context: Context, layout: UILayout, node: Node, text: str):
        layout.label(text=text)

    def draw_color(self, context: Context, node: Node) -> list[float]:
        return (1, 0, 0, 1)


class SaveSetting(SocketBase):
    bl_idname = "SaveSetting"

    def draw(self, context: Context, layout: UILayout, node: Node, text: str):
        layout.label(text=text)

    def draw_color(self, context: Context, node: Node) -> list[float]:
        return (0, .5, 0, 1)


class BakeSetting(SocketBase):
    bl_idname = "BakeSetting"

    def draw(self, context: Context, layout: UILayout, node: Node, text: str):
        layout.label(text=text)

    def draw_color(self, context: Context, node: Node) -> list[float]:
        return (0, .5, 1, 1)


class Mesh(SocketBase):
    bl_idname = "Mesh"

    def draw(self, context: Context, layout: UILayout, node: Node, text: str):
        layout.label(text=text)

    def draw_color(self, context: Context, node: Node) -> list[float]:
        return (1, .5, 0, 1)


class Image(SocketBase):
    bl_idname = "Image"

    def draw(self, context: Context, layout: UILayout, node: Node, text: str):
        layout.label(text=text)

    def draw_color(self, context: Context, node: Node) -> list[float]:
        return (1, 1, 0, 1)
