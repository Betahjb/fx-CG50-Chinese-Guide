# 参考资料 / References

本页集中整理正文中涉及的官方资料、社区项目与案例来源。

## Casio 官方

- fx-CG50 产品与支持入口：<https://www.casio.com/sg/scientific-calculators/support.FX-CG50/>
- Casio 图形计算器支持/下载：<https://edu.casio.com/intl/support/downloads/>

> 说明：不同地区的 Casio 官网 URL 可能不同。若某个地区页面失效，可从 Casio Education / Support 入口重新导航。

## PythonExtra

- GitHub：<https://github.com/tangenty42/PythonExtra>

用途：在 fx-CG50 等机型上提供扩展 MicroPython 环境，适合图形、实时输入和小游戏实验。

## fxSDK

- GitHub：<https://github.com/lephe/Fx-SDK>

用途：Casio 图形计算器 Add-in 开发工具链，负责项目构建、资源转换等。

## gint

- Planet Casio Gitea：<https://gitea.planet-casio.com/Lephenixnoir/gint>

用途：面向 Casio 图形计算器的底层运行时 / 硬件接口库，可用于显示、键盘、Timer 等功能。

## GravityDuck

- 原作者 Planet Casio 页面：<https://www.planet-casio.com/Fr/programmes/programme1856-last-gravityduck-pierrotll-jeux-add-ins.html>

本仓库只把 GravityDuck 作为“现成 `.g3a` Add-in 如何安装”的案例，不重新分发游戏二进制。

## 进一步搜索关键词

如果想继续研究，可使用这些关键词：

```text
fx-CG50 add-in
fx-CG50 g3a
Casio Prizm add-in
PythonExtra fx-CG50
fxSDK Casio
Casio gint
sh-elf-gcc fx-CG50
Planet Casio fx-CG50
Cemetech fx-CG50
```

## 关于资料可信度

建议优先级：

1. Casio 官方手册 / 官方支持页；
2. fxSDK / gint / PythonExtra 项目原始仓库；
3. Planet Casio / Cemetech 等长期社区；
4. 个人博客 / 论坛转述。

对于 CPU 频率、内存布局、超频、底层寄存器等信息，社区资料很有价值，但不同硬件批次和 OS 版本可能存在差异，引用时应保留具体来源与测试条件。
