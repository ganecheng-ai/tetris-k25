"""输入处理模块"""

import pygame
from typing import Callable, Dict

from logger import get_logger

logger = get_logger('input')


class InputHandler:
    """输入处理器"""

    def __init__(self):
        """初始化输入处理器"""
        self.key_bindings: Dict[int, Callable] = {}
        self.key_pressed: Dict[int, bool] = {}
        self.key_repeat_delay = 150  # 按键重复延迟（毫秒）
        self.key_repeat_interval = 50  # 按键重复间隔（毫秒）
        self.key_timers: Dict[int, float] = {}

        # 方向键特殊处理
        self.das_delay = 167  # Delayed Auto Shift 延迟
        self.das_timer = 0
        self.last_direction_key = None

        logger.info("输入处理器初始化完成")

    def bind_key(self, key: int, callback: Callable, continuous: bool = False):
        """
        绑定按键

        Args:
            key: pygame按键常量
            callback: 回调函数
            continuous: 是否支持连续触发
        """
        self.key_bindings[key] = {
            'callback': callback,
            'continuous': continuous
        }
        self.key_pressed[key] = False
        self.key_timers[key] = 0

    def unbind_key(self, key: int):
        """解绑按键"""
        if key in self.key_bindings:
            del self.key_bindings[key]
            del self.key_pressed[key]
            del self.key_timers[key]

    def clear_bindings(self):
        """清除所有按键绑定"""
        self.key_bindings.clear()
        self.key_pressed.clear()
        self.key_timers.clear()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        处理单个事件

        Args:
            event: pygame事件

        Returns:
            是否处理了退出事件
        """
        if event.type == pygame.QUIT:
            return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True

            if event.key in self.key_bindings:
                binding = self.key_bindings[event.key]
                self.key_pressed[event.key] = True
                self.key_timers[event.key] = 0
                binding['callback']()

                # 记录方向键
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    self.last_direction_key = event.key
                    self.das_timer = 0

        elif event.type == pygame.KEYUP:
            if event.key in self.key_pressed:
                self.key_pressed[event.key] = False
                self.key_timers[event.key] = 0

                # 清除方向键记录
                if event.key == self.last_direction_key:
                    self.last_direction_key = None

        return False

    def update(self, dt: float):
        """
        更新输入状态（处理连续按键）

        Args:
            dt: 帧时间（毫秒）
        """
        # 处理DAS（Delayed Auto Shift）
        if self.last_direction_key in (pygame.K_LEFT, pygame.K_RIGHT):
            self.das_timer += dt
            if self.das_timer >= self.das_delay:
                # DAS激活后，按间隔重复触发
                interval_triggered = False
                trigger_threshold = self.das_delay + self.key_repeat_interval
                while self.das_timer >= trigger_threshold:
                    self.das_timer -= self.key_repeat_interval
                    interval_triggered = True

                if (interval_triggered
                        and self.last_direction_key in self.key_bindings):
                    self.key_bindings[self.last_direction_key]['callback']()

        # 处理其他连续按键
        for key, binding in self.key_bindings.items():
            if not binding['continuous']:
                continue

            if self.key_pressed.get(key, False):
                self.key_timers[key] += dt

                # 软降连续触发
                if key == pygame.K_DOWN:
                    if self.key_timers[key] >= self.key_repeat_delay:
                        self.key_timers[key] = 0
                        binding['callback']()

    def process_events(self) -> bool:
        """
        处理所有待处理的事件

        Returns:
            是否收到退出事件
        """
        for event in pygame.event.get():
            if self.handle_event(event):
                return True
        return False

    def setup_game_bindings(self, game):
        """
        设置游戏按键绑定

        Args:
            game: 游戏实例
        """
        self.clear_bindings()

        # 左移
        self.bind_key(pygame.K_LEFT, game.move_left)
        # 右移
        self.bind_key(pygame.K_RIGHT, game.move_right)
        # 软降（连续触发）
        self.bind_key(pygame.K_DOWN, game.move_down, continuous=True)
        # 旋转
        self.bind_key(pygame.K_UP, lambda: game.rotate(clockwise=True))
        # 硬降
        self.bind_key(pygame.K_SPACE, game.hard_drop)
        # 暂停
        self.bind_key(pygame.K_p, game.pause)
        # 重新开始
        self.bind_key(pygame.K_r, game.start)

        logger.info("游戏按键绑定已设置")

    def setup_menu_bindings(self, game):
        """
        设置菜单按键绑定

        Args:
            game: 游戏实例
        """
        self.clear_bindings()

        # 开始游戏
        def start_game():
            game.start()
            self.setup_game_bindings(game)

        # 绑定所有按键开始游戏
        for key in range(pygame.K_a, pygame.K_z + 1):
            self.bind_key(key, start_game)
        for key in range(pygame.K_0, pygame.K_9 + 1):
            self.bind_key(key, start_game)
        # 绑定方向键
        self.bind_key(pygame.K_LEFT, start_game)
        self.bind_key(pygame.K_RIGHT, start_game)
        self.bind_key(pygame.K_UP, start_game)
        self.bind_key(pygame.K_DOWN, start_game)
        self.bind_key(pygame.K_SPACE, start_game)
        self.bind_key(pygame.K_RETURN, start_game)
        self.bind_key(pygame.K_KP_ENTER, start_game)

        logger.info("菜单按键绑定已设置")
