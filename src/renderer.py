"""渲染系统模块"""

import pygame
from typing import Tuple

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    GRID_WIDTH, GRID_HEIGHT, CELL_SIZE,
    BOARD_OFFSET_X, BOARD_OFFSET_Y,
    COLORS, FONT_SIZE_SMALL, FONT_SIZE_NORMAL, FONT_SIZE_LARGE, FONT_SIZE_TITLE
)
from logger import get_logger
from game import GameState

logger = get_logger('renderer')


class Renderer:
    """游戏渲染器"""

    def __init__(self):
        """初始化渲染器"""
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.fps = 60

        # 加载字体
        self._init_fonts()

        # 缓存
        self._cell_surfaces = {}

        logger.info("渲染器初始化完成")

    def _init_fonts(self):
        """初始化字体"""
        self.fonts = {}

        # 尝试加载系统字体
        font_names = [
            'simhei', 'microsoftyahei', 'simsun', 'wqy-zenhei',
            'wenquanyi zen hei', 'droid sans fallback',
            'noto sans cjk sc', 'source han sans sc',
            'arial', 'helvetica', 'sans-serif'
        ]

        for size_name, size in [
            ('small', FONT_SIZE_SMALL),
            ('normal', FONT_SIZE_NORMAL),
            ('large', FONT_SIZE_LARGE),
            ('title', FONT_SIZE_TITLE)
        ]:
            font = None
            for name in font_names:
                try:
                    font = pygame.font.SysFont(name, size)
                    # 测试是否支持中文
                    if font.render(
                        '测试', True, (255, 255, 255)
                    ).get_width() > 0:
                        break
                except Exception:
                    continue

            if font is None:
                font = pygame.font.Font(None, size)

            self.fonts[size_name] = font

        logger.info("字体初始化完成")

    def _get_cell_surface(self, color: Tuple[int, int, int]) -> pygame.Surface:
        """获取或创建格子表面"""
        if color not in self._cell_surfaces:
            surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
            # 主色块（稍小一点，留出边框）
            rect_size = (CELL_SIZE - 2, CELL_SIZE - 2)
            pygame.draw.rect(surface, color, (1, 1) + rect_size)
            # 高光
            highlight = tuple(min(255, c + 40) for c in color)
            pygame.draw.rect(surface, highlight, (1, 1, CELL_SIZE - 2, 3))
            # 阴影
            shadow = tuple(max(0, c - 40) for c in color)
            shadow_rect = (1, CELL_SIZE - 4, CELL_SIZE - 2, 3)
            pygame.draw.rect(surface, shadow, shadow_rect)
            self._cell_surfaces[color] = surface
        return self._cell_surfaces[color]

    def clear(self):
        """清空屏幕"""
        self.screen.fill(COLORS['background'])

    def flip(self):
        """刷新屏幕"""
        pygame.display.flip()

    def tick(self) -> float:
        """
        控制帧率

        Returns:
            上一帧耗时（秒）
        """
        return self.clock.tick(self.fps) / 1000.0

    def draw_board(self, game):
        """绘制游戏面板"""
        # 面板背景
        board_rect = pygame.Rect(
            BOARD_OFFSET_X - 2,
            BOARD_OFFSET_Y - 2,
            GRID_WIDTH * CELL_SIZE + 4,
            GRID_HEIGHT * CELL_SIZE + 4
        )
        pygame.draw.rect(self.screen, COLORS['board_border'], board_rect, 2)

        # 内部背景
        inner_rect = pygame.Rect(
            BOARD_OFFSET_X,
            BOARD_OFFSET_Y,
            GRID_WIDTH * CELL_SIZE,
            GRID_HEIGHT * CELL_SIZE
        )
        pygame.draw.rect(self.screen, COLORS['board_background'], inner_rect)

        # 网格线
        for i in range(GRID_WIDTH + 1):
            x = BOARD_OFFSET_X + i * CELL_SIZE
            pygame.draw.line(
                self.screen, COLORS['grid_line'],
                (x, BOARD_OFFSET_Y),
                (x, BOARD_OFFSET_Y + GRID_HEIGHT * CELL_SIZE)
            )
        for i in range(GRID_HEIGHT + 1):
            y = BOARD_OFFSET_Y + i * CELL_SIZE
            pygame.draw.line(
                self.screen, COLORS['grid_line'],
                (BOARD_OFFSET_X, y),
                (BOARD_OFFSET_X + GRID_WIDTH * CELL_SIZE, y)
            )

        # 绘制已放置的方块
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = game.board.get_cell(x, y)
                if color:
                    self._draw_cell(x, y, color)

    def _draw_cell(
        self, x: int, y: int,
        color: Tuple[int, int, int], alpha: int = 255
    ):
        """绘制单个格子"""
        cell_x = BOARD_OFFSET_X + x * CELL_SIZE
        cell_y = BOARD_OFFSET_Y + y * CELL_SIZE

        surface = self._get_cell_surface(color)
        if alpha < 255:
            # 创建透明副本
            surface = surface.copy()
            surface.set_alpha(alpha)
        self.screen.blit(surface, (cell_x, cell_y))

    def draw_tetromino(self, game):
        """绘制当前方块"""
        if game.current_tetromino:
            color = game.current_tetromino.color
            for x, y in game.current_tetromino.get_positions():
                if y >= 0:
                    self._draw_cell(x, y, color)

    def draw_ghost(self, game):
        """绘制方块影子"""
        if game.ghost_tetromino and game.current_tetromino:
            color = game.ghost_tetromino.color
            # 降低透明度
            ghost_color = tuple(min(255, c + 60) for c in color)
            for x, y in game.ghost_tetromino.get_positions():
                if y >= 0:
                    # 绘制半透明格子
                    cell_x = BOARD_OFFSET_X + x * CELL_SIZE
                    cell_y = BOARD_OFFSET_Y + y * CELL_SIZE
                    ghost_surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
                    ghost_surface.fill(ghost_color)
                    ghost_surface.set_alpha(80)
                    self.screen.blit(ghost_surface, (cell_x, cell_y))
                    # 绘制边框
                    pygame.draw.rect(
                        self.screen, ghost_color,
                        (cell_x, cell_y, CELL_SIZE, CELL_SIZE), 1
                    )

    def draw_preview(self, game):
        """绘制下一个方块预览"""
        # 预览区域位置
        preview_x = BOARD_OFFSET_X + GRID_WIDTH * CELL_SIZE + 30
        preview_y = BOARD_OFFSET_Y + 20

        # 标题
        self.draw_text('下一个', preview_x, preview_y, 'normal', COLORS['text'])

        # 预览区域背景
        preview_rect = pygame.Rect(preview_x, preview_y + 30, 100, 100)
        pygame.draw.rect(self.screen, COLORS['board_background'], preview_rect)
        pygame.draw.rect(self.screen, COLORS['board_border'], preview_rect, 2)

        # 绘制下一个方块
        next_tetromino = game.queue.peek_next()
        if next_tetromino:
            shape = next_tetromino.get_shape()
            color = next_tetromino.color
            offset_x = preview_x + 50 - len(shape[0]) * CELL_SIZE // 2
            offset_y = preview_y + 80 - len(shape) * CELL_SIZE // 2

            for row_idx, row in enumerate(shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        cell_rect = pygame.Rect(
                            offset_x + col_idx * CELL_SIZE,
                            offset_y + row_idx * CELL_SIZE,
                            CELL_SIZE - 1, CELL_SIZE - 1
                        )
                        pygame.draw.rect(self.screen, color, cell_rect)

    def draw_info(self, game):
        """绘制游戏信息"""
        info_x = 30
        info_y = BOARD_OFFSET_Y + 20

        # 游戏标题
        self.draw_text(
            '俄罗斯方块', info_x, info_y - 60,
            'title', COLORS['text_highlight']
        )

        # 分数
        self.draw_text(
            f'分数: {game.score}', info_x, info_y,
            'large', COLORS['text']
        )

        # 等级
        self.draw_text(
            f'等级: {game.level}', info_x, info_y + 50,
            'normal', COLORS['text']
        )

        # 消除行数
        self.draw_text(
            f'行数: {game.lines}', info_x, info_y + 80,
            'normal', COLORS['text']
        )

        # 连击
        if game.combo >= 0:
            combo_text = f'连击: x{game.combo + 1}'
            self.draw_text(
                combo_text, info_x, info_y + 110,
                'normal', COLORS['text_highlight']
            )

    def draw_controls(self):
        """绘制操作说明"""
        controls_x = 30
        controls_y = BOARD_OFFSET_Y + 250

        controls = [
            '操作说明:',
            '← →  左右移动',
            '↑     旋转',
            '↓     加速下落',
            '空格  直接落下',
            'P     暂停',
            'R     重新开始',
            'ESC   退出',
        ]

        for i, text in enumerate(controls):
            size = 'normal' if i == 0 else 'small'
            color = COLORS['text_highlight'] if i == 0 else COLORS['text']
            self.draw_text(text, controls_x, controls_y + i * 25, size, color)

    def draw_pause_overlay(self):
        """绘制暂停遮罩"""
        # 半透明遮罩
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # 暂停文字
        self.draw_text(
            '游戏暂停', WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30,
            'title', COLORS['text_highlight'], center=True
        )
        self.draw_text(
            '按 P 继续', WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30,
            'normal', COLORS['text'], center=True
        )

    def draw_game_over_overlay(self, game):
        """绘制游戏结束遮罩"""
        # 半透明遮罩
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # 游戏结束文字
        self.draw_text(
            '游戏结束', WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60,
            'title', (255, 80, 80), center=True
        )
        self.draw_text(
            f'最终分数: {game.score}', WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2,
            'large', COLORS['text'], center=True
        )
        self.draw_text(
            '按 R 重新开始', WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50,
            'normal', COLORS['text_highlight'], center=True
        )
        self.draw_text(
            '按 ESC 退出', WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80,
            'normal', COLORS['text'], center=True
        )

    def draw_start_screen(self):
        """绘制开始界面"""
        self.screen.fill(COLORS['background'])

        # 标题
        self.draw_text(
            '俄罗斯方块', WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100,
            'title', COLORS['text_highlight'], center=True
        )

        # 副标题
        self.draw_text(
            'TETRIS', WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40,
            'large', COLORS['text'], center=True
        )

        # 开始提示
        self.draw_text(
            '按任意键开始游戏', WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50,
            'normal', COLORS['text_highlight'], center=True
        )

        self.draw_controls()

    def draw_text(
        self, text: str, x: int, y: int, size: str = 'normal',
        color: Tuple[int, int, int] = COLORS['text'],
        center: bool = False
    ):
        """
        绘制文字

        Args:
            text: 文字内容
            x: x坐标
            y: y坐标
            size: 字体大小 ('small', 'normal', 'large', 'title')
            color: 颜色
            center: 是否居中
        """
        font = self.fonts.get(size, self.fonts['normal'])
        surface = font.render(text, True, color)

        if center:
            x -= surface.get_width() // 2
            y -= surface.get_height() // 2

        self.screen.blit(surface, (x, y))

    def render(self, game):
        """渲染完整游戏画面"""
        self.clear()

        if game.state == GameState.READY:
            self.draw_start_screen()
        else:
            self.draw_board(game)
            self.draw_ghost(game)
            self.draw_tetromino(game)
            self.draw_preview(game)
            self.draw_info(game)
            self.draw_controls()

            if game.state == GameState.PAUSED:
                self.draw_pause_overlay()
            elif game.state == GameState.GAME_OVER:
                self.draw_game_over_overlay(game)

        self.flip()

    def quit(self):
        """退出渲染器"""
        pygame.quit()
        logger.info("渲染器已关闭")
