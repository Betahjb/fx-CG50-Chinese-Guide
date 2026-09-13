# Mario 风格横版平台教学 Demo

`mario_cg50_v3.py` 是面向 fx-CG50 + PythonExtra 的实机教学 Demo。画面由代码绘制，不需要额外图片、音乐或 ROM 文件。

## 运行条件

- Casio fx-CG50
- 已安装 PythonExtra
- PythonExtra 环境可导入 `gint`
- 384 × 216 屏幕

标准 PC Python 没有 `gint` 模块，因此不能直接运行该文件。电脑端可以进行语法检查与源码阅读，完整运行需要 PythonExtra 实机环境。

## 安装与运行

1. 把 `PythonExtra.g3a` 复制到 fx-CG50 存储根目录。
2. 把 `mario_cg50_v3.py` 复制到 PythonExtra 可以访问的位置。
3. 安全弹出计算器并断开 USB。
4. 打开 `PythonExtra`，进入 `FILES`。
5. 选择 `mario_cg50_v3.py`，按 `EXE` 运行。

如果这是你第一次使用 PythonExtra，建议先运行 [`../key-test/keytest_v2.py`](../key-test/keytest_v2.py)。

## 按键

| 按键 | 功能 |
|---|---|
| 左 / 右 | 移动 |
| SHIFT | 加速；Fire 状态按下时发射 |
| EXE | 跳跃，按住可跳得更高 |
| 下 | Super / Fire 状态蹲下 |
| EXIT | 退出 |

## 可以学习什么

- Tile Map 与可见区域绘制
- 固定时间步物理更新
- 碰撞检测与世界坐标
- Camera 滚屏
- Small / Super / Fire 状态机
- 敌人、道具与火球逻辑
- 面向受限设备的整数化与绘制优化

这是技术教学和实验代码，不追求对任何商业游戏的逐像素复刻，也不包含商业游戏 ROM、原版音频或提取素材。
