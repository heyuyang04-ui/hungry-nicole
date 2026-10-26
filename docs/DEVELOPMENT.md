# 开发与测试

当前可运行产品为 Seedance 妮可源码版。使用 Python 3.12 和 `requirements.txt`，运行入口为 `python run.py`。安装素材后默认加载 `outputs/妮可桌宠素材`，不需要白龙资源。素材 ZIP 和逐文件 SHA-256 固定在 `app/nicole_assets.json`。

`app` 中保留上游运行时模块；根目录旧 Windows 构建辅助脚本用于兼容研究，不是本次已经验证的安装器生产方式。当前发布源码与素材包，不声称完成 Windows 打包验收。

## 离线检查

```bash
python -m compileall -q app tools run.py
PYTHONPATH=app:tools QT_QPA_PLATFORM=offscreen python -m unittest app.test_pet_care app.test_token_calendar tools.test_nicole_seedance tools.test_install_nicole_assets -q
PYTHONPATH=app QT_QPA_PLATFORM=offscreen python -m unittest app.test_action_audio -q
```

安装素材后另运行 `app.test_pet_care_ui`，测试食物菜单、库存及播放绑定。`QCoreApplication` 音频测试与 `QApplication` UI 测试分开进程执行。

macOS 原生窗口验收包括切换其他应用、保持后台显示和不抢焦点；聊天与设置只有用户主动打开时才激活。不要在状态刷新、动画帧或定时器内调用 `activateWindow` / `requestActivate`。

## 发布

动画与 WAV 放 GitHub Release；Git 仅保存源码、文档、静态角色预览与校验清单。不得提交参考图、原视频、密钥、任务回执、个人截图、数据库或本机配置。更新仓库固定为 `heyuyang04-ui/hungry-nicole`，不使用上游的资源发布工作流。

新生成的动画必须经过逐帧机械检查和实际播放验收；不能仅凭帧数或解码成功批准视觉效果。

## README 动态图鉴

运行 `python tools/build_readme_gallery.py` 从已安装素材生成 `build/readme-gallery/`。脚本先核对源动画与发布清单的 SHA-256，再输出 200×200 动态 WebP、分类接触表、时长校验报告及 `gallery.md`；保留全部帧和原时长。说明中的喂食入口必须与运行时一致，`feed` 仅作备用展示。

检查接触表及浏览器播放后，将 `preview-nicole-*.webp` 作为独立附件上传到 `v0.10.0-seedance` Release，并用 `gallery.md` 更新 README 的「动态动作图鉴」。不要覆盖正式素材 ZIP 或把生成动画提交到 Git。README 更新还需检查 GitHub 实际图片加载及动画播放。
