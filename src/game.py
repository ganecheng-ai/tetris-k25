"""游戏核心逻辑模块"""

import time
from enum import Enum, auto
from typing import Optional, Callable

from config import (
    INITIAL_FALL_SPEED, MIN_FALL_SPEED, SPEED_INCREMENT,
    SCORE_TABLE, GRID_WIDTH
)
from tetromino import Tetromino, TetrominoQueue
from board import Board
from logger import get_logger

logger = get_logger('game')


class GameState(Enum):
    """游戏状态枚举"""
    READY = auto()      # 准备中
    PLAYING = auto()    # 游戏中
    PAUSED = auto()     # 暂停
    GAME_OVER = auto()  # 游戏结束


class Game:
    """游戏核心类"""

    def __init__(self):
        """初始化游戏"""
        self.board = Board()
        self.queue = TetrominoQueue(preview_count=1)
        self.current_tetromino: Optional[Tetromino] = None
        self.ghost_tetromino: Optional[Tetromino] = None

        # 游戏状态
        self.state = GameState.READY

        # 游戏数据
        self.score = 0
        self.lines = 0
        self.level = 1
        self.combo = -1  # -1表示没有combo，第一次消行后变为0

        # 时间控制
        self.last_fall_time = 0
        self.lock_delay = 500  # 锁定延迟（毫秒）
        self.lock_timer = 0
        self.lock_resets = 0
        self.max_lock_resets = 15

        # 回调函数
        self.on_line_clear: Optional[Callable[[int], None]] = None
        self.on_game_over: Optional[Callable[[], None]] = None
        self.on_score_change: Optional[Callable[[int], None]] = None
        self.on_level_up: Optional[Callable[[int], None]] = None

        logger.info("游戏初始化完成")

    def reset(self):
        """重置游戏"""
        self.board.reset()
        self.queue = TetrominoQueue(preview_count=1)
        self.current_tetromino = None
        self.ghost_tetromino = None
        self.state = GameState.READY
        self.score = 0
        self.lines = 0
        self.level = 1
        self.combo = -1
        self.last_fall_time = 0
        self.lock_timer = 0
        self.lock_resets = 0
        logger.info("游戏已重置")

    def start(self):
        """开始游戏"""
        if self.state in (GameState.READY, GameState.GAME_OVER):
            self.reset()
            self.state = GameState.PLAYING
            self._spawn_tetromino()
            self.last_fall_time = time.time() * 1000
            logger.info("游戏开始")

    def pause(self):
        """暂停/继续游戏"""
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
            logger.info("游戏暂停")
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING
            self.last_fall_time = time.time() * 1000
            logger.info("游戏继续")

    def get_fall_speed(self) -> int:
        """获取当前下落速度（毫秒）"""
        speed = INITIAL_FALL_SPEED - (self.level - 1) * SPEED_INCREMENT
        return max(speed, MIN_FALL_SPEED)

    def _spawn_tetromino(self) -> bool:
        """
        生成新方块

        Returns:
            是否成功生成
        """
        self.current_tetromino = self.queue.get_next()
        # 初始位置：居中顶部
        self.current_tetromino.x = (GRID_WIDTH - 4) // 2
        self.current_tetromino.y = -2

        # 检查是否可以放置
        if not self.board.is_valid_position(self.current_tetromino):
            self._game_over()
            return False

        self._update_ghost()
        self.lock_timer = 0
        self.lock_resets = 0
        logger.debug(f"生成新方块: {self.current_tetromino}")
        return True

    def _update_ghost(self):
        """更新影子位置"""
        if self.current_tetromino:
            self.ghost_tetromino = self.board.get_ghost_position(self.current_tetromino)

    def _lock_tetromino(self):
        """锁定当前方块"""
        if not self.current_tetromino:
            return

        # 放置方块
        self.board.place_tetromino(self.current_tetromino)
        logger.debug(f"方块已锁定: {self.current_tetromino}")

        # 清除行
        lines_cleared = self.board.clear_lines()
        if lines_cleared > 0:
            self._handle_line_clear(lines_cleared)
        else:
            self.combo = -1

        # 生成新方块
        self._spawn_tetromino()

    def _handle_line_clear(self, lines_cleared: int):
        """处理消行"""
        # 计算分数
        base_score = SCORE_TABLE.get(lines_cleared, 0)
        self.combo += 1
        combo_bonus = self.combo * 50 if self.combo > 0 else 0
        total_score = base_score + combo_bonus
        self.score += total_score * self.level

        # 更新行数
        self.lines += lines_cleared

        # 检查升级
        new_level = self.lines // 10 + 1
        if new_level > self.level:
            self.level = new_level
            logger.info(f"升级！当前等级: {self.level}")
            if self.on_level_up:
                self.on_level_up(self.level)

        logger.info(f"消除 {lines_cleared} 行，当前分数: {self.score}，连击: {self.combo}")

        # 回调
        if self.on_line_clear:
            self.on_line_clear(lines_cleared)
        if self.on_score_change:
            self.on_score_change(self.score)

    def _game_over(self):
        """游戏结束"""
        self.state = GameState.GAME_OVER
        logger.info(f"游戏结束！最终分数: {self.score}")
        if self.on_game_over:
            self.on_game_over()

    def update(self, current_time: Optional[float] = None):
        """
        更新游戏状态

        Args:
            current_time: 当前时间（毫秒），如果为None则自动获取
        """
        if self.state != GameState.PLAYING:
            return

        if current_time is None:
            current_time = time.time() * 1000

        # 自动下落
        fall_speed = self.get_fall_speed()
        if current_time - self.last_fall_time >= fall_speed:
            self.move_down()
            self.last_fall_time = current_time

    def move_left(self) -> bool:
        """
        向左移动

        Returns:
            是否成功移动
        """
        if self.state != GameState.PLAYING or not self.current_tetromino:
            return False

        new_tetromino = self.current_tetromino.move(-1, 0)
        if self.board.is_valid_position(new_tetromino):
            self.current_tetromino = new_tetromino
            self._update_ghost()
            return True
        return False

    def move_right(self) -> bool:
        """
        向右移动

        Returns:
            是否成功移动
        """
        if self.state != GameState.PLAYING or not self.current_tetromino:
            return False

        new_tetromino = self.current_tetromino.move(1, 0)
        if self.board.is_valid_position(new_tetromino):
            self.current_tetromino = new_tetromino
            self._update_ghost()
            return True
        return False

    def move_down(self) -> bool:
        """
        向下移动（软降）

        Returns:
            是否成功移动
        """
        if self.state != GameState.PLAYING or not self.current_tetromino:
            return False

        new_tetromino = self.current_tetromino.move(0, 1)
        if self.board.is_valid_position(new_tetromino):
            self.current_tetromino = new_tetromino
            self._update_ghost()
            return True
        # 无法下落，锁定方块
        self._lock_tetromino()
        return False

    def hard_drop(self) -> int:
        """
        硬降（直接落下）

        Returns:
            落下的距离
        """
        if self.state != GameState.PLAYING or not self.current_tetromino:
            return 0

        if self.ghost_tetromino:
            distance = self.ghost_tetromino.y - self.current_tetromino.y
            self.current_tetromino = self.ghost_tetromino
            self._lock_tetromino()
            return distance
        return 0

    def rotate(self, clockwise: bool = True) -> bool:
        """
        旋转方块

        Args:
            clockwise: 是否顺时针旋转

        Returns:
            是否成功旋转
        """
        if self.state != GameState.PLAYING or not self.current_tetromino:
            return False

        # 基本旋转
        new_tetromino = self.current_tetromino.rotate(clockwise)

        # 如果基本旋转失败，尝试踢墙（SRS规则简化版）
        if not self.board.is_valid_position(new_tetromino):
            # 尝试左右移动
            for dx in [-1, 1, -2, 2]:
                kicked = new_tetromino.move(dx, 0)
                if self.board.is_valid_position(kicked):
                    new_tetromino = kicked
                    break
            else:
                # 尝试向上（针对I型方块）
                kicked = new_tetromino.move(0, -1)
                if self.board.is_valid_position(kicked):
                    new_tetromino = kicked
                else:
                    return False

        self.current_tetromino = new_tetromino
        self._update_ghost()

        # 锁定延迟重置
        if self.lock_resets < self.max_lock_resets:
            self.lock_timer = 0
            self.lock_resets += 1

        return True

    def hold(self) -> bool:
        """
        暂存方块（Hold功能）

        Returns:
            是否成功暂存
        """
        # 简化版本暂不支持hold功能
        return False

    def get_game_data(self) -> dict:
        """
        获取游戏数据

        Returns:
            游戏数据字典
        """
        return {
            'score': self.score,
            'lines': self.lines,
            'level': self.level,
            'combo': self.combo if self.combo >= 0 else 0,
            'state': self.state.name,
            'fall_speed': self.get_fall_speed(),
        }
