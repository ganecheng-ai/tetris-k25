"""游戏面板模块"""

from typing import List, Tuple, Optional

from .config import GRID_WIDTH, GRID_HEIGHT
from .tetromino import Tetromino


class Board:
    """游戏面板类"""

    def __init__(self):
        """初始化游戏面板"""
        self.width = GRID_WIDTH
        self.height = GRID_HEIGHT
        # 使用二维列表存储格子状态，None表示空，否则存储颜色
        self.grid: List[List[Optional[Tuple[int, int, int]]]] = [
            [None for _ in range(self.width)] for _ in range(self.height)
        ]

    def reset(self):
        """重置游戏面板"""
        self.grid = [
            [None for _ in range(self.width)] for _ in range(self.height)
        ]

    def is_valid_position(self, tetromino: Tetromino) -> bool:
        """
        检查方块位置是否有效

        Args:
            tetromino: 要检查的方块

        Returns:
            位置是否有效
        """
        for x, y in tetromino.get_positions():
            # 检查边界
            if x < 0 or x >= self.width or y >= self.height:
                return False
            # 检查是否与其他方块重叠（注意y可能为负数，此时不算重叠）
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True

    def place_tetromino(self, tetromino: Tetromino) -> bool:
        """
        将方块放置到面板上

        Args:
            tetromino: 要放置的方块

        Returns:
            是否成功放置
        """
        for x, y in tetromino.get_positions():
            if y >= 0:  # 只放置可见部分
                if x < 0 or x >= self.width or y >= self.height:
                    return False
                if self.grid[y][x] is not None:
                    return False
                self.grid[y][x] = tetromino.color
        return True

    def clear_lines(self) -> int:
        """
        清除已完成的行

        Returns:
            清除的行数
        """
        lines_cleared = 0
        row = self.height - 1
        while row >= 0:
            # 检查当前行是否已满
            if all(cell is not None for cell in self.grid[row]):
                # 删除当前行
                del self.grid[row]
                # 在顶部添加新空行
                self.grid.insert(0, [None for _ in range(self.width)])
                lines_cleared += 1
                # 继续检查同一行（因为上面的行下移了）
            else:
                row -= 1
        return lines_cleared

    def get_cell(self, x: int, y: int) -> Optional[Tuple[int, int, int]]:
        """
        获取指定位置的格子颜色

        Args:
            x: x坐标
            y: y坐标

        Returns:
            格子颜色，如果为空则返回None
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None

    def get_ghost_position(self, tetromino: Tetromino) -> Tetromino:
        """
        计算方块的影子位置（直接落下后的位置）

        Args:
            tetromino: 当前方块

        Returns:
            影子位置的方块
        """
        ghost = tetromino
        while True:
            next_ghost = ghost.move(0, 1)
            if self.is_valid_position(next_ghost):
                ghost = next_ghost
            else:
                break
        return ghost

    def is_game_over(self) -> bool:
        """
        检查游戏是否结束

        Returns:
            游戏是否结束
        """
        # 检查最上面几行是否有方块
        for row in self.grid[:2]:
            for cell in row:
                if cell is not None:
                    return True
        return False

    def get_column_heights(self) -> List[int]:
        """
        获取每列的高度（用于AI或统计）

        Returns:
            每列的高度列表
        """
        heights = []
        for x in range(self.width):
            height = 0
            for y in range(self.height):
                if self.grid[y][x] is not None:
                    height = self.height - y
                    break
            heights.append(height)
        return heights

    def get_holes_count(self) -> int:
        """
        获取空洞数量（用于统计）

        Returns:
            空洞数量
        """
        holes = 0
        for x in range(self.width):
            found_block = False
            for y in range(self.height):
                if self.grid[y][x] is not None:
                    found_block = True
                elif found_block:
                    holes += 1
        return holes

    def __repr__(self) -> str:
        lines = []
        for row in self.grid:
            line = ''.join(['#' if cell else '.' for cell in row])
            lines.append(line)
        return '\n'.join(lines)
