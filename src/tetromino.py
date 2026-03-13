"""俄罗斯方块形状定义模块"""

import random
import copy
from typing import List, Tuple, Optional

from .config import TETROMINO_COLORS


# 7种经典方块的形状定义（使用4x4矩阵）
# 每个形状包含其所有旋转状态
SHAPES = {
    'I': [
        [[0, 0, 0, 0],
         [1, 1, 1, 1],
         [0, 0, 0, 0],
         [0, 0, 0, 0]],
        [[0, 0, 1, 0],
         [0, 0, 1, 0],
         [0, 0, 1, 0],
         [0, 0, 1, 0]],
        [[0, 0, 0, 0],
         [0, 0, 0, 0],
         [1, 1, 1, 1],
         [0, 0, 0, 0]],
        [[0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0]],
    ],
    'O': [
        [[1, 1],
         [1, 1]],
    ],
    'T': [
        [[0, 1, 0],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 1],
         [0, 1, 0]],
        [[0, 0, 0],
         [1, 1, 1],
         [0, 1, 0]],
        [[0, 1, 0],
         [1, 1, 0],
         [0, 1, 0]],
    ],
    'S': [
        [[0, 1, 1],
         [1, 1, 0],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 1],
         [0, 0, 1]],
        [[0, 0, 0],
         [0, 1, 1],
         [1, 1, 0]],
        [[1, 0, 0],
         [1, 1, 0],
         [0, 1, 0]],
    ],
    'Z': [
        [[1, 1, 0],
         [0, 1, 1],
         [0, 0, 0]],
        [[0, 0, 1],
         [0, 1, 1],
         [0, 1, 0]],
        [[0, 0, 0],
         [1, 1, 0],
         [0, 1, 1]],
        [[0, 1, 0],
         [1, 1, 0],
         [1, 0, 0]],
    ],
    'J': [
        [[1, 0, 0],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 1],
         [0, 1, 0],
         [0, 1, 0]],
        [[0, 0, 0],
         [1, 1, 1],
         [0, 0, 1]],
        [[0, 1, 0],
         [0, 1, 0],
         [1, 1, 0]],
    ],
    'L': [
        [[0, 0, 1],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 0],
         [0, 1, 1]],
        [[0, 0, 0],
         [1, 1, 1],
         [1, 0, 0]],
        [[1, 1, 0],
         [0, 1, 0],
         [0, 1, 0]],
    ],
}


class Tetromino:
    """俄罗斯方块类"""

    def __init__(self, shape_type: Optional[str] = None):
        """
        初始化一个方块

        Args:
            shape_type: 方块类型，如果为None则随机生成
        """
        if shape_type is None:
            shape_type = random.choice(list(SHAPES.keys()))

        self.shape_type = shape_type
        self.shapes = SHAPES[shape_type]
        self.rotation = 0
        self.color = TETROMINO_COLORS[shape_type]
        self.x = 0
        self.y = 0

    def get_shape(self) -> List[List[int]]:
        """获取当前旋转状态的形状"""
        return self.shapes[self.rotation]

    def rotate(self, clockwise: bool = True) -> 'Tetromino':
        """
        旋转方块

        Args:
            clockwise: 是否顺时针旋转

        Returns:
            新的旋转后的方块（不修改当前方块）
        """
        new_tetromino = copy.deepcopy(self)
        if clockwise:
            new_tetromino.rotation = (self.rotation + 1) % len(self.shapes)
        else:
            new_tetromino.rotation = (self.rotation - 1) % len(self.shapes)
        return new_tetromino

    def move(self, dx: int, dy: int) -> 'Tetromino':
        """
        移动方块

        Args:
            dx: x方向偏移
            dy: y方向偏移

        Returns:
            新的移动后的方块（不修改当前方块）
        """
        new_tetromino = copy.deepcopy(self)
        new_tetromino.x += dx
        new_tetromino.y += dy
        return new_tetromino

    def get_positions(self) -> List[Tuple[int, int]]:
        """
        获取方块在当前位置的所有格子坐标

        Returns:
            格子坐标列表 (x, y)
        """
        shape = self.get_shape()
        positions = []
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    positions.append((self.x + col_idx, self.y + row_idx))
        return positions

    def get_bounding_box(self) -> Tuple[int, int, int, int]:
        """
        获取方块的边界框

        Returns:
            (min_x, min_y, max_x, max_y)
        """
        positions = self.get_positions()
        if not positions:
            return (0, 0, 0, 0)
        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]
        return (min(xs), min(ys), max(xs), max(ys))

    def __repr__(self) -> str:
        return f"Tetromino({self.shape_type}, rotation={self.rotation}, pos=({self.x}, {self.y}))"


class TetrominoQueue:
    """方块队列，用于生成和预览下一个方块"""

    def __init__(self, preview_count: int = 1):
        """
        初始化方块队列

        Args:
            preview_count: 预览方块数量
        """
        self.preview_count = preview_count
        self.queue = []
        self._refill()

    def _refill(self):
        """补充队列"""
        while len(self.queue) < self.preview_count + 1:
            # 生成7-bag：确保每7个方块包含所有类型
            bag = [Tetromino(t) for t in SHAPES.keys()]
            random.shuffle(bag)
            self.queue.extend(bag)

    def get_next(self) -> Tetromino:
        """获取下一个方块"""
        self._refill()
        return self.queue.pop(0)

    def peek_next(self, index: int = 0) -> Tetromino:
        """
        预览指定位置的方块

        Args:
            index: 预览索引（0表示下一个）

        Returns:
            指定位置的方块
        """
        self._refill()
        return self.queue[index]

    def get_preview(self) -> List[Tetromino]:
        """获取所有预览方块"""
        self._refill()
        return self.queue[:self.preview_count]
