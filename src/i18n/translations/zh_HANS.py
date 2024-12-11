# formt: (t, translate_t, ctx) if not ctx => default "*"
TREE_TCTX = "BakeNodes"
NODE_TCTX = "BakeNode"
PROP_CTX = "BakeNodeProp"
PANEL_CTX = "BakeNodePanel"
OPS_CTX = "BakeNodeOps"
PREF_CTX = "BakeNodePref"

translations = (
    ("Default Bake Resolution", "默认烘焙分辨率", PREF_CTX),
    ("Easy Bake Node", "简易烘焙节点"),
    ("Bake Nodes", "烘焙节点"),
    ("Bake Setting", "烘焙设置"),
    ("Core", "核心"),
    # 烘焙分类
    ("Bake", "烘焙",),
    ("Bake", "烘焙", TREE_TCTX),
    ("ImageCombine", "图片组合",),
    ("ImageCombine", "图片组合", TREE_TCTX),
    # 通道分类
    ("BlenderPass", "Blender通道",),
    ("BlenderPass", "Blender通道", TREE_TCTX),
    ("PBRPass", "PBR通道",),
    ("PBRPass", "PBR通道", TREE_TCTX),
    ("CustomPass", "自定义通道"),
    ("CustomPass", "自定义通道", TREE_TCTX),
    # 设置分类
    ("BakeSetting", "烘焙设置"),
    ("BakeSetting", "烘焙设置", TREE_TCTX),
    # 网格分类
    ("SingleMesh", "网格(自烘焙)",),
    ("SingleMesh", "网格(自烘焙)", TREE_TCTX),
    ("Mesh", "网格(高低模)",),
    ("Mesh", "网格(高低模)", TREE_TCTX),
    ("SceneMeshes", "网格(场景)",),
    ("SceneMeshes", "网格(场景)", TREE_TCTX),
    ("CollectionMeshes", "网格(集合)",),
    ("CollectionMeshes", "网格(集合)", TREE_TCTX),
    # 输出分类
    ("AITexPreview", "AI纹理预览",),
    ("AITexPreview", "AI纹理预览", TREE_TCTX),
    ("SaveToImage", "保存到图片"),
    ("SaveToImage", "保存到图片", TREE_TCTX),
    ("SaveToMat", "保存到材质"),
    ("SaveToMat", "保存到材质", TREE_TCTX),
    # 其他
    ("bake_pass", "烘焙通道"),
    ("source", "源物体", NODE_TCTX),
    ("target", "目标物体", NODE_TCTX),
    ("Name Format:", "名称格式:", NODE_TCTX),
    ("Name Example:", "名称样例:", NODE_TCTX),
    ("Seperator", "分隔符", NODE_TCTX),
    ("obj_name", "物体", NODE_TCTX),
    ("bake_cat", "分类", NODE_TCTX),
    ("bake_pass", "烘焙通道", NODE_TCTX),
    ("resolution", "分辨率", NODE_TCTX),
    ("yy", "年", NODE_TCTX),
    ("mm", "月", NODE_TCTX),
    ("dd", "日", NODE_TCTX),
    ("h", "时", NODE_TCTX),
    ("m", "分", NODE_TCTX),
    ("s", "秒", NODE_TCTX),
    ("Cat1DispName", "分类1", TREE_TCTX),
    ("Node1", "节点1", TREE_TCTX),
    ("Task Count", "任务数量", PROP_CTX),
    ("Exe Task", "执行任务", PROP_CTX),
    ("Task Progress", "任务进度", PROP_CTX),
    ("Exe Node", "执行节点", PROP_CTX),
    ("SaveName", "保存名", PROP_CTX),
    ("UseMatName", "使用材质名", PROP_CTX),
    ("BakeTypeDescription", "描述", PROP_CTX),
    ("Node Progress", "节点进度", PROP_CTX),
    ("Save", "保存", OPS_CTX),
    ("Load", "加载", OPS_CTX),
    ("Delete", "删除", OPS_CTX),
    ("Run Bake", "执行烘焙", OPS_CTX),
    ("Save As Bake Presets", "保存为烘焙类型", OPS_CTX),
    ("Mark Prop As Params", "标记为烘焙参数", OPS_CTX),
    ("Delete Prop From Params", "从烘焙参数移除", OPS_CTX),
    ("Bake Settings Presets", "烘焙预设", PANEL_CTX),
    ("Bake Params", "导出参数", PANEL_CTX),
    ("Bake Settings Presets", "烘焙预设", OPS_CTX),
)
