"""游戏配置模块"""

import os

# 游戏窗口配置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
WINDOW_TITLE = "俄罗斯方块 - Tetris"

# 游戏区域配置
GRID_WIDTH = 10      # 游戏区域宽度（格子数）
GRID_HEIGHT = 20     # 游戏区域高度（格子数）
CELL_SIZE = 30       # 每个格子的大小（像素）

# 游戏区域位置（居中）
BOARD_OFFSET_X = (WINDOW_WIDTH - GRID_WIDTH * CELL_SIZE) // 2
BOARD_OFFSET_Y = (WINDOW_HEIGHT - GRID_HEIGHT * CELL_SIZE) // 2

# 颜色定义
COLORS = {
    'background': (20, 20, 20),
    'board_background': (30, 30, 30),
    'board_border': (100, 100, 100),
    'grid_line': (50, 50, 50),
    'text': (255, 255, 255),
    'text_highlight': (255, 220, 100),
    'button': (80, 80, 80),
    'button_hover': (120, 120, 120),
}

# 方块颜色（7种经典方块）
TETROMINO_COLORS = {
    'I': (0, 255, 255),      # 青色
    'O': (255, 255, 0),      # 黄色
    'T': (128, 0, 128),      # 紫色
    'S': (0, 255, 0),        # 绿色
    'Z': (255, 0, 0),        # 红色
    'J': (0, 0, 255),        # 蓝色
    'L': (255, 165, 0),      # 橙色
}

# 游戏速度配置（毫秒）
INITIAL_FALL_SPEED = 1000  # 初始下落速度
MIN_FALL_SPEED = 100       # 最快速度
SPEED_INCREMENT = 50       # 每级增加的速度

# 分数配置
SCORE_TABLE = {
    1: 100,   # 消除1行
    2: 300,   # 消除2行
    3: 500,   # 消除3行
    4: 800,   # 消除4行（Tetris）
}

# 日志配置
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'tetris.log')
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# 字体配置
FONT_SIZE_SMALL = 18
FONT_SIZE_NORMAL = 24
FONT_SIZE_LARGE = 36
FONT_SIZE_TITLE = 48

# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)
