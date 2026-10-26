# 饥饿的妮可 · Hungry Nicole

一只陪你写代码、会饿、可以喂面包的粉发猫娘桌宠。

基于 **[Wunsch2048/codex-bailong-desktop-pet](https://github.com/Wunsch2048/codex-bailong-desktop-pet)** 二次开发，保留上游 Codex 状态联动、任务完成提醒、Token 图表、托盘和聊天面板。在此基础上新增妮可角色、饱腹度、Token 面包奖励和互动声音。

![妮可 Seedance 动作预览](docs/media/nicole-seedance.png)

[查看全部 27 段动态动作与介绍](#动态动作图鉴)

## 这一版有什么

| 功能 | 行为 |
| --- | --- |
| 妮可内置角色 | 默认启动就是妮可；全部动画来自 Seedance 连续视频，不使用独立生图拼接 |
| 连贯动画 | 720×720 透明 WebP，按源视频时间轴采样为 24fps，保持 1 倍速；包含 27 段素材、3,987 帧 |
| 互动声音 | 包含 19 段 WAV；主动互动且开启声音、1 倍速时播放，自动动作保持安静 |
| 饱腹度 | 初始 100%，每满 5 分钟减少 1%，关闭程序和休眠期间也计时 |
| 饥饿提醒 | 降至 30% 显示「主人～ 我好饿～」，同一轮饥饿不重复提醒 |
| Token 换面包 | 功能启用后，每累计 1,000,000 个可读取的本机 Codex token 获得一个面包，余数保留 |
| 固定喂食动作 | 右键 → 食物 → 面包；成功扣除面包后恢复 30 个百分点，并仅播放固定的「偷吃面包」动作 |
| 本地保存 | 饱腹度、库存和奖励进度保存在本机 SQLite；重启、重复刷新不重复发奖 |
| macOS 置顶修复 | 切换到 Codex 后保持显示；状态刷新不抢输入焦点，主动打开聊天/设置仍可输入 |

满饱或没有面包时不消耗库存、不播放喂食动画。「偷吃面包」不会出现在随机互动或手动动作菜单中。另一个 `feed` 视频仅保留为备用制作素材，不参与运行时播放。

## 下载与启动

当前提供 **源码 + 已验证素材包**，推荐 Python 3.12。已在 macOS Apple Silicon 进行源码启动与原生窗口测试；本次没有发布经过验证的 Windows EXE 或 macOS `.app` 安装器。

```bash
git clone https://github.com/heyuyang04-ui/hungry-nicole.git
cd hungry-nicole
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python tools/install_nicole_assets.py
python run.py
```

Windows PowerShell 用 `py -3.12 -m venv .venv` 创建环境，之后使用 `.\.venv\Scripts\python.exe` 代替上述 `python`，无需激活环境。Windows 功能兼容性仍需实机验证。

素材下载自 [本项目 Release](https://github.com/heyuyang04-ui/hungry-nicole/releases/tag/v0.10.0-seedance)，安装工具先检查 ZIP 和每个文件的 SHA-256，再替换素材。也可手动下载后运行：

```bash
python tools/install_nicole_assets.py --archive /path/to/nicole-seedance-assets-v0.10.0.zip
```

已有完整素材不必重复安装。退出后重新运行 `python run.py` 即可；`python run.py --quit` 可关闭当前妮可进程。

首次启动默认关闭自主走动、随机动作和自动更新；需要时可在设置中打开。内置更新地址已隔离为本项目，不会下载白龙仓库的程序覆盖妮可。

## 使用说明

- **一起玩游戏**：右键妮可或托盘 → 妮可陪我玩游戏，打开 https://magicneko.com/game-case 。
- **妮可主页**：首次运行时，胶囊左侧地球按钮默认打开 https://magicneko.com/ 。已有用户可在设置中将「胶囊左侧快捷功能」选为「妮可主页」。
- **吃饭提醒**：默认每天本地时间 11:40、17:20 显示「主人～吃饭了喵～」。在设置 → 闲聊与台词中修改午餐、晚餐时间或关闭提醒；无需开启自动台词。文字气泡显示 12 秒，不展开面板、不播放声音。需保持程序运行；隐藏、编辑或高优先级通知期间最多延后 5 分钟，超过后不补发。同一时段当天重启也不重复提醒。
- **食物**：右键妮可或托盘 → 食物，查看饱腹度、面包和奖励进度。只累计启用后的有效用量，不补发历史奖励；无需 API Key。
- **声音**：设置 → 人物与动作，开启主动互动声音并使用 1 倍速。切换动作、隐藏、退出或关闭声音会停止播放；无音轨的动作保持静音。
- **聊天**：从妮可面板进入聊天，可自行配置服务。运行桌宠、发放面包不需要生视频 API Key。
- **数据隔离**：`run.py` 为本项目使用独立数据目录，保留内部兼容目录名 `BailongEnhanced`；不读取白龙安装目录的配置。macOS 位于 `~/Library/Application Support/HungryNicole/`，Windows 位于 `%LOCALAPPDATA%/HungryNicole/`。可用 `NICOLE_STATE_HOME` 指定其他目录。

更多规则见 [饱腹度与食物](docs/PET_CARE.md)。

## 动态动作图鉴

以下展示当前 Seedance 素材包的全部 **27 段动画**。预览按原速播放，缩小为 200×200 的无声动态 WebP，并铺浅色背景；桌宠实际使用 720×720 透明 WebP。

普通互动可从右键 → 手动动作菜单体验；工作动作随 Codex 状态联动。自动动作静音，主动互动在开启声音且 1 倍速时可播放素材音轨。预览为方便查看会重复播放，不代表桌宠会不断重复该动作。

### 日常陪伴

| | | |
| :---: | :---: | :---: |
| **待机呼吸** · `idle`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-idle.webp" width="200" height="200" alt="妮可：待机呼吸动态预览"><br>安静站立、轻轻呼吸，日常陪伴时的默认待机。 | **待机看向主人** · `idle2`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-idle2.webp" width="200" height="200" alt="妮可：待机看向主人动态预览"><br>转头看向主人，作为另一段待机表情。 | **招手打招呼** · `01`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-01.webp" width="200" height="200" alt="妮可：招手打招呼动态预览"><br>抬手招呼，向主人问好。 |
| **灵感亮起** · `04`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-04.webp" width="200" height="200" alt="妮可：灵感亮起动态预览"><br>想到好主意时，举起手指表达灵感。 | **得意叉腰** · `05`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-05.webp" width="200" height="200" alt="妮可：得意叉腰动态预览"><br>双手叉腰，露出得意的小表情。 | **亲近贴贴** · `08`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-08.webp" width="200" height="200" alt="妮可：亲近贴贴动态预览"><br>靠近主人，温柔地撒个娇。 |
| **害羞傲娇** · `09`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-09.webp" width="200" height="200" alt="妮可：害羞傲娇动态预览"><br>害羞地转头，又偷偷看回来。 | **小小生气** · `13`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-13.webp" width="200" height="200" alt="妮可：小小生气动态预览"><br>鼓起脸颊，表达一点点小脾气。 | **困倦打哈欠** · `14`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-14.webp" width="200" height="200" alt="妮可：困倦打哈欠动态预览"><br>打个哈欠，困了也继续陪着你。 |

### 互动与小魔法

| | | |
| :---: | :---: | :---: |
| **开心庆祝** · `18`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-18.webp" width="200" height="200" alt="妮可：开心庆祝动态预览"><br>开心庆祝，也用于 Codex 任务完成反馈。 | **猫爪印记** · `22`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-22.webp" width="200" height="200" alt="妮可：猫爪印记动态预览"><br>展示小小猫爪印记，送给主人。 | **吹出小星星** · `25`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-25.webp" width="200" height="200" alt="妮可：吹出小星星动态预览"><br>轻轻吹出星光，来一点小魔法。 |
| **双手比心** · `20`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-20.webp" width="200" height="200" alt="妮可：双手比心动态预览"><br>在胸前比心，表达喜欢。 | **猫咪约定** · `21`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-21.webp" width="200" height="200" alt="妮可：猫咪约定动态预览"><br>拿出约定卡片，和主人作个约定。 | **收藏小宝藏** · `24`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-24.webp" width="200" height="200" alt="妮可：收藏小宝藏动态预览"><br>打开小盒子，展示珍藏的小宝藏。 |
| **信任守护** · `26`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-26.webp" width="200" height="200" alt="妮可：信任守护动态预览"><br>温柔点头，表示自己一直陪在身边。 |  |  |

### 陪你工作

| | | |
| :---: | :---: | :---: |
| **收到任务** · `work01`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-work01.webp" width="200" height="200" alt="妮可：收到任务动态预览"><br>收到新任务，点头示意准备开始。 | **持续处理任务** · `work02`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-work02.webp" width="200" height="200" alt="妮可：持续处理任务动态预览"><br>抱着小电脑忙碌，对应执行任务。 | **整理归档** · `work03`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-work03.webp" width="200" height="200" alt="妮可：整理归档动态预览"><br>整理纸张和文件夹，对应整理、编辑或回复。 |
| **翻阅资料** · `work04`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-work04.webp" width="200" height="200" alt="妮可：翻阅资料动态预览"><br>打开书本翻阅，对应思考、搜索和阅读。 | **放大镜检查** · `work05`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-work05.webp" width="200" height="200" alt="妮可：放大镜检查动态预览"><br>拿起放大镜检查，对应验证、测试和排查。 |  |

### 桌面操作

| | | |
| :---: | :---: | :---: |
| **悬空拖拽** · `drag`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-drag.webp" width="200" height="200" alt="妮可：悬空拖拽动态预览"><br>被拖起时悬空摆动，努力保持平衡。 | **轻轻落地** · `landing`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-landing.webp" width="200" height="200" alt="妮可：轻轻落地动态预览"><br>松开拖拽后轻轻落地，重新站稳。 | **查看额度** · `quota`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-quota.webp" width="200" height="200" alt="妮可：查看额度动态预览"><br>拿出小卡片查看，用于额度回应。 |

### 饥饿与喂食

| | | |
| :---: | :---: | :---: |
| **偷吃面包** · `17`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-17.webp" width="200" height="200" alt="妮可：偷吃面包动态预览"><br>实际喂食专用：右键 → 食物 → 面包，成功扣除库存后播放，饱腹度 +30。 | **饥饿提醒** · `hungry`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-hungry.webp" width="200" height="200" alt="妮可：饥饿提醒动态预览"><br>揉揉肚子、期待投喂的表情；目前在互动动作中，30% 饥饿提醒使用文字。 | **吃面包反馈** · `feed`<br><img src="https://github.com/heyuyang04-ui/hungry-nicole/releases/download/v0.10.0-seedance/preview-nicole-feed.webp" width="200" height="200" alt="妮可：吃面包反馈动态预览"><br>备用吃面包反馈素材，仅展示；当前喂食功能固定使用「17 · 偷吃面包」。 |

## 素材创作

仓库仅保留 Seedance 路线：同一透明 base → 固定首尾绿幕图 → 连续视频 → 按时间抽帧 → 抠透明 → WebP 与 WAV。旧的 Seedream 独立逐帧生成和拼接脚本不再包含于当前版本。

- [完整动作 Prompt](docs/NICOLE_SEEDANCE_PROMPTS.md)
- [Seedance 生成、续查与后处理命令](docs/NICOLE_SEEDANCE.md)
- [测试与版本状态](docs/NICOLE_RELEASE_STATUS.md)

生成视频会消耗火山方舟额度，只有显式 `--execute` 才提交任务；密钥只读取 `ARK_API_KEY`。参考图、原视频、API 回执、数据库、日志和聊天内容不随源码发布。

工作动作保留完整视频片段，当前不宣称实现无缝中段循环。生成音色可能随动作不同；用户已确认这一批动作播放效果可用。

## 来源与许可

感谢 [Wunsch2048/codex-bailong-desktop-pet](https://github.com/Wunsch2048/codex-bailong-desktop-pet) 和更早的 [jingh12312-rgb/bailong-desktop-pet](https://github.com/jingh12312-rgb/bailong-desktop-pet)。本地改造基线为 v0.9.9 / UI87；原作者功能不标为本项目原创。

保留 [NOTICE](NOTICE.md)、[上游资料](docs/upstream/README-bailong.md) 和 `app/licenses`。上游没有覆盖整个项目的统一开源许可证，本项目不擅自标为 MIT，也不额外授予角色或第三方素材的商业使用权。原 NOTICE 中的授权确认属于上游发布者声明，不代表对新增素材的额外授权。

本项目是独立第三方桌面程序，与 OpenAI、Codex 官方无隶属关系。
