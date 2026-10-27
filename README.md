# PyGame 游戏开发实训

> Python + Pygame 课程作业合集，从命令行小游戏到两个完整图形游戏。

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.x-2C2D72?style=flat)
![status](https://img.shields.io/badge/status-coursework-lightgrey)

## 内容

| 目录 | 内容 | 入口 |
| --- | --- | --- |
| `work1/` | 命令行井字棋：函数拆分、输入校验、胜负判断 | `python work1/test1_1.py` |
| `work2/` | 键盘事件与角色移动练习 | `python work2/dragon_practice.py` |
| `work3/` | 贪吃蛇：方向键控制、碰撞检测、计分 | `python work3/snake_practice.py` |
| `work4/` | 乒乓球：挡板控制、球体反弹 | `python work4/pong_practice.py` |
| `work5/` | Flappy Bird：重力、障碍物生成、状态管理 | `python work5/flappy_bird_practice.py` |
| `Final/` | 赛车躲避完整小游戏 | `python Final/car_racer.py` |
| `final2/` | 横版射击平台游戏 Shooter Platformer | `python final2/main.py` |
| `demo/` | 第三方 Pygame 参考项目，仅用于学习 | 见各自目录 |

## 项目结构

```text
PyGame/
├── work1/        # 命令行井字棋
├── work2/        # 键盘控制练习
├── work3/        # 贪吃蛇
├── work4/        # 乒乓球
├── work5/        # Flappy Bird
├── Final/        # 赛车躲避
├── final2/       # 横版射击平台游戏
└── demo/         # 第三方参考项目
```

## 环境要求

- Python 3.10+
- Pygame 2.x

```bash
pip install pygame
```

## 运行

进入对应目录后运行入口文件：

```bash
python work3/snake_practice.py
```

- `work1` 按提示输入坐标（如 `0,1`）
- `work3` 使用方向键控制
- `work4` 使用上下方向键控制挡板
- `Final` 使用方向键控制赛车，`Esc` 退出
- 其余游戏按窗口内提示操作

## 技术栈 / 学习点

- Python、Pygame
- 游戏循环、事件处理、精灵与碰撞检测
- 资源加载、动画、状态机、计分与结束条件

## 说明

- 本仓库为课程作业与练习合集，不是生产项目。
- `demo/` 内为第三方开源示例，版权归原作者，仅作学习参考。
