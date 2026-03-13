# 俄罗斯方块 (Tetris)

[![Build](https://github.com/ganecheng-ai/tetris-k25/actions/workflows/build.yml/badge.svg)](https://github.com/ganecheng-ai/tetris-k25/actions/workflows/build.yml)

一个使用 Python 开发的精美俄罗斯方块游戏，支持简体中文界面。

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Pygame](https://img.shields.io/badge/pygame-2.5+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## 功能特点

- **经典玩法**: 完整的俄罗斯方块游戏逻辑，包含7种经典方块
- **精美界面**: 使用 Pygame 渲染，支持方块影子预览、连击显示
- **中文支持**: 完整的简体中文界面
- **流畅操作**: 支持 DAS（Delayed Auto Shift）连续移动
- **日志系统**: 完整的日志记录，方便问题排查
- **跨平台**: 支持 Windows、Linux、macOS

## 操作说明

| 按键 | 功能 |
|------|------|
| `←` | 左移 |
| `→` | 右移 |
| `↑` | 旋转 |
| `↓` | 加速下落（软降）|
| `空格` | 直接落下（硬降）|
| `P` | 暂停/继续 |
| `R` | 重新开始 |
| `ESC` | 退出游戏 |

## 安装与运行

### 从源码运行

1. 克隆仓库
```bash
git clone https://github.com/ganecheng-ai/tetris-k25.git
cd tetris-k25
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行游戏
```bash
cd src
python main.py
```

### 下载预编译版本

从 [Releases](https://github.com/ganecheng-ai/tetris-k25/releases) 页面下载对应平台的可执行文件。

## 项目结构

```
tetris-k25/
├── src/
│   ├── main.py           # 游戏入口
│   ├── game.py           # 游戏核心逻辑
│   ├── tetromino.py      # 方块定义
│   ├── board.py          # 游戏面板
│   ├── renderer.py       # 渲染系统
│   ├── input_handler.py  # 输入处理
│   ├── logger.py         # 日志系统
│   └── config.py         # 配置文件
├── assets/               # 资源文件
├── .github/workflows/    # CI/CD 配置
├── requirements.txt      # Python 依赖
├── plan.md              # 开发计划
└── README.md            # 本文件
```

## 游戏截图

（待添加）

## 开发计划

详见 [plan.md](plan.md)

### 版本历史

- **v0.1.0** - 基础框架，可运行空窗口
- **v0.2.0** - 核心玩法，完整游戏逻辑
- **v0.3.0** - 精美界面，图形渲染
- **v0.4.0** - 完整交互，用户控制
- **v0.5.0** - 中文支持，本地化
- **v1.0.0** - 正式版，CI/CD，多平台发布

## 贡献

欢迎提交 Issue 和 Pull Request。

## 许可证

[MIT License](LICENSE)

## 日志

游戏运行时会自动生成日志文件到 `logs/tetris.log`，包含游戏的详细运行信息，有助于问题排查。
