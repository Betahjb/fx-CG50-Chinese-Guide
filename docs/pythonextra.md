# PythonExtra：在 fx-CG50 上运行自己的 Python

## 1. PythonExtra 是什么？

PythonExtra 是一个第三方 `.g3a` Add-in。它在 fx-CG50 上提供 MicroPython 运行环境，并暴露适合图形、键盘和实时交互的接口。

项目地址：

<https://github.com/tangenty42/PythonExtra>

这意味着：

```text
PythonExtra.g3a
    ↓
MicroPython Runtime
    ↓
your_program.py
```

所以 PythonExtra 并不是“另一种文件格式”，它本身就是通过 `.g3a` Add-in 机制进入计算器的。

---

## 2. Windows 10 安装步骤

### Step 1：下载 PythonExtra

进入项目 Releases 或项目说明页，下载适合 fx-CG50 的 `.g3a`。

### Step 2：USB 连接 fx-CG50

1. 使用支持数据传输的 USB 线；
2. 连接 Windows 10 电脑；
3. 在计算器连接界面选择 USB Flash；
4. Windows 应出现一个新的可移动存储盘。

### Step 3：复制 `.g3a`

把 `PythonExtra.g3a` 放到计算器存储内存根目录。

示意：

```text
fx-CG50 storage/
├── PythonExtra.g3a
├── @MainMem/
└── ...
```

安全弹出并断开连接后，回到主菜单，应能看到 PythonExtra 图标。

---

## 3. 放入自己的 Python 脚本

把脚本，例如：

```text
keytest_v2.py
mario_cg50_v3.py
```

复制到计算器可以被 PythonExtra 浏览的位置。实机上进入：

```text
PythonExtra
   ↓
FILES
   ↓
选择 .py
   ↓
EXE
```

即可运行。

---

## 4. 为什么适合小游戏？

相比只做基础教学的 Python 环境，小游戏通常需要：

- 实时读取按键状态；
- 同时检测多个按键；
- 高频刷新屏幕；
- 快速画矩形、像素、文字和 Sprite；
- 基于毫秒的计时；
- 自己管理游戏循环。

PythonExtra + `gint` 接口能更直接地完成这些任务。

---

## 5. 实机验证：三键同时输入

我们在 fx-CG50 上实际验证过：

```text
RIGHT + SHIFT + EXE
```

可以同时检测。

推荐逐键读取：

```python
import gint

right = gint.keydown(gint.KEY_RIGHT)
run   = gint.keydown(gint.KEY_SHIFT)
jump  = gint.keydown(gint.KEY_EXE)

if right and run and jump:
    # simultaneous input
    pass
```

某些 PythonExtra 构建下，类似：

```python
gint.keydown_all([ ... ])
```

可能出现：

```text
TypeError: can't convert list to int
```

因此示例代码采用独立 `keydown()` 调用，兼容性更稳。

---

## 6. PythonExtra 不等于 PC Python

一个常见误区是：

```text
PC 上 pygame 可以跑
        ↓
复制到 CG50 也应该能跑
```

实际上不成立。

`pygame` 是 PC 平台的图形/输入库；fx-CG50 上没有完整 pygame。若移植 pygame 小游戏，需要把平台层替换：

```text
pygame.display   → gint 绘图
pygame.key       → gint.keydown
pygame.time      → MicroPython time
pygame image     → 自己的 Sprite/像素数据
```

游戏算法本身，如地图、碰撞、AI、状态机，则通常可以保留较多。

---

## 7. 什么时候该从 Python 转向 C？

如果遇到这些现象，可以考虑原生 C：

- 全屏刷新明显变慢；
- 同屏 Sprite/敌人太多；
- 需要稳定高帧率；
- 图形绘制调用过多；
- 想做独立主菜单 Add-in；
- 想深入学习 fxSDK/gint。

一个非常实用的路线是：

> PythonExtra 做玩法原型 → 验证完成 → C + fxSDK/gint 做最终版。
