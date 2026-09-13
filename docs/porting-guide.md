# 从 GitHub 到 fx-CG50：开源小游戏移植指南

这篇文档讲的是 **port / 移植**，不是“把一个游戏文件点一下就转换成 fx-CG50 版本”。

真正的移植，核心是：

> 保留平台无关的游戏逻辑，替换平台相关的显示、输入、时间、音频和文件系统接口。

---

## 1. 先判断原项目属于哪一类

### A. Python / pygame 项目

这类最适合先移植到 PythonExtra。

常见替换关系：

```text
pygame.display       → gint 绘图
pygame.key           → gint.keydown()
pygame.time.Clock    → MicroPython time / 自己的 fixed timestep
pygame Surface       → 自己的 Sprite 数据
pygame mixer         → 视情况省略或改写
```

通常可尽量保留：

- 关卡数据
- Tile Map
- 碰撞规则
- 速度和重力参数
- 敌人 AI
- 游戏状态机
- 道具逻辑

### B. C / C++ 项目

如果项目本身就把核心逻辑和平台层分开，会更适合移植为原生 `.g3a`。

```text
Open-source C/C++ game
        ↓
保留 core/gameplay
        ↓
替换 SDL / GLFW / OS API
        ↓
gint 显示、键盘、Timer
        ↓
fxSDK + sh-elf-gcc
        ↓
game.g3a
```

### C. FC / NES ROM

如果拿到的是：

```text
xxx.nes
```

那不是普通源码，而是游戏 ROM。

直接运行 ROM，本质上需要 NES 模拟器，需要模拟或实现包括：

- 6502 CPU 行为
- PPU 图形系统
- 内存映射
- 手柄输入
- Mapper
- 音频 APU（若需要）

这和“移植一个开源小游戏源码”完全不是一个难度等级。

---

## 2. 推荐的移植顺序

不要一上来挑大型游戏。建议：

```text
几十到几百行小游戏
    ↓
单屏游戏
    ↓
简单滚屏
    ↓
Tile 地图
    ↓
多敌人 / 道具
    ↓
再尝试更完整的开源项目
```

适合入门的项目特征：

- 2D；
- 无复杂音频依赖；
- 资源较少；
- 没有大量浮点计算；
- 平台层集中；
- License 清楚；
- 不依赖网络。

---

## 3. 一个好的工程拆分

为了以后同时支持 PC / fx-CG50，可以把代码拆成：

```text
core/
  physics
  collision
  world
  enemies
  game_state

platform_pc/
  pygame input
  pygame rendering

platform_cg50/
  gint input
  gint rendering
```

这样平台无关逻辑不需要写两遍。

Mario 教学 Demo 就采用了类似思想：游戏规则尽量独立，输入和渲染适配 fx-CG50。

---

## 4. fx-CG50 上尤其需要注意什么

### 屏幕

fx-CG50 屏幕为 384×216。移植来自 PC 的游戏时，不要假设任意窗口尺寸都能直接映射。

### 绘制成本

PythonExtra 下，大量逐像素调用可能很慢。优先考虑：

- Tile；
- 矩形块；
- run-length Sprite；
- 只绘制可见区域；
- 减少重复文字绘制；
- 避免无意义的全地图遍历。

### 时间步

不要把物理速度直接绑定到 while 循环次数。

更稳妥的做法：

```text
固定物理步长
+ 渲染循环
+ 必要时 catch-up
```

### 输入

游戏需要区分：

- `held`：按键持续按住；
- `pressed edge`：这一帧刚刚按下。

例如：

- 持续按 SHIFT = 助跑；
- SHIFT 的按下沿 = 发射一次；
- EXE 的按下沿 = 开始跳跃；
- EXE held = 控制高跳持续时间。

---

## 5. 从 Python 原型迁移到 C

Python：

```python
if right:
    vx += accel
x += vx
```

C 中对应逻辑通常非常直观：

```c
if(right)
    vx += accel;
x += vx;
```

最需要重写的不是游戏规则，而是：

- Python 对象 / list / class；
- `gint` Python 包装接口；
- 动态资源；
- 平台时间函数；
- Sprite 数据表示；
- 内存管理。

因此非常适合采用：

> **Python 先做原型，C 再做最终版。**

---

## 6. License 和版权

开源移植前必须先看项目的 `LICENSE`。

常见 License：

- MIT
- BSD
- Apache-2.0
- GPL

要注意：

```text
代码开源
≠ 美术素材开源
≠ 音乐开源
≠ ROM 可以传播
≠ 商标和角色形象变成公有领域
```

如果只是学习，最好优先选择：

- 原创开源小游戏；
- 素材和代码许可证都明确；
- 不依赖商业 ROM；
- 能够替换为自绘图形。

---

## 7. 适合继续做的 Demo

这个仓库未来可以逐步加入：

1. 移动方块；
2. Pong；
3. Snake；
4. Breakout；
5. 单屏平台游戏；
6. Tile 横版游戏；
7. 一个小型原创 `.g3a` C 游戏。

这些例子比直接丢一个大型项目更适合初学者理解平台。
