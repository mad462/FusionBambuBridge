# FusionBambuBridge

[English](./README.md) | [简体中文](./README.zh-CN.md)

FusionBambuBridge 是一个面向 Windows 的 Fusion 360 插件，专门服务于下面这条工作流：

1. 在 Fusion 中选择一个或多个 body 或 component。
2. 在 Fusion 工具栏中运行 `Bambu Bridge` 命令。
3. 导出一个临时 `3MF` 文件。
4. 自动在 Bambu Studio 中打开该文件。

这个插件的目标，是尽量贴近 Fusion 原生 3D Print 的使用体验，同时直接对接 Bambu Studio。

## 当前状态

- 已具备 Add-In manifest 和入口文件。
- 已在 Fusion Design 工作区中完成工具栏命令注册。
- 已支持将多选几何合并导出为一个临时 `3MF`。
- 导出后会自动拉起 Bambu Studio。
- 每次导出后会自动清理导出用的临时 staging 对象。

## 项目结构

```text
FusionBambuBridge/
  FusionBambuBridge.manifest
  FusionBambuBridge.py
  lib/
    config.py
    commands/
    services/
  docs/
  scripts/
  tests/
```

## 安装到 Fusion

推荐直接用 Fusion 自己的安装入口：

1. 在 Fusion 里按 `Shift+S` 打开 `脚本和附加模块` 窗口。
2. 切到 `附加模块` 标签页。
3. 点击左上角的 `+` 按钮。
4. 选择 `来自设备的脚本或附加模块`。
5. 在本机上选中 `FusionBambuBridge` 文件夹。
6. 运行 `FusionBambuBridge`。
7. 之后就可以在 Design 工作区工具栏里使用 `Bambu Bridge` 按钮。

如果你是开发时反复同步，也可以继续使用 [`scripts/copy-to-fusion.ps1`](./scripts/copy-to-fusion.ps1)。

## 开发说明

- 默认导出格式是 `3MF`，因为它最适合多对象切片工作流。
- Bambu Studio 的路径解析被单独放在一个模块里，后续可以很容易替换成注册表检测、设置面板或自定义路径。
- 多选导出时会在 Fusion 内部创建一个临时组件作为 staging 目标，导出完成后会自动删除。

## 下一步建议

1. 增加一个更完整的 Fusion 命令对话框，用于路径覆盖和导出模式控制。
2. 增加可编辑的设置存储，例如 Bambu Studio 路径和临时导出目录。
3. 继续补强 Fusion 里一些特殊选择场景下的边界处理。
4. 再把命令交互细节打磨得更像 Fusion 原生 3D Print 工作流。

## 参考

- [docs/architecture.md](./docs/architecture.md)
- [docs/usage.md](./docs/usage.md)
- [docs/contributing.md](./docs/contributing.md)
- [docs/references.md](./docs/references.md)
