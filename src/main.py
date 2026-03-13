"""俄罗斯方块游戏主入口"""

import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

from game import Game, GameState
from renderer import Renderer
from input_handler import InputHandler
from logger import setup_logger, get_logger
from config import LOG_FILE


def main():
    """主函数"""
    # 初始化日志系统
    logger = setup_logger()
    logger.info("=" * 50)
    logger.info("俄罗斯方块游戏启动")
    logger.info(f"日志文件: {LOG_FILE}")

    try:
        # 初始化游戏组件
        game = Game()
        renderer = Renderer()
        input_handler = InputHandler()

        # 设置初始按键绑定
        input_handler.setup_menu_bindings(game)

        running = True
        clock = pygame.time.Clock()

        logger.info("游戏主循环开始")

        while running:
            # 处理事件
            dt = clock.tick(60)  # 返回毫秒

            # 处理输入
            if input_handler.process_events():
                running = False
                break

            # 更新输入状态（处理连续按键）
            input_handler.update(dt)

            # 更新游戏状态
            if game.state == GameState.PLAYING:
                game.update()

                # 检查游戏状态变化
                if game.state == GameState.GAME_OVER:
                    logger.info("游戏结束，切换到菜单按键绑定")
                    input_handler.setup_menu_bindings(game)

            elif game.state == GameState.READY:
                # 等待按键开始
                pass

            # 渲染画面
            renderer.render(game)

        logger.info("游戏主循环结束")

    except Exception as e:
        logger.exception(f"游戏发生错误: {e}")
        raise

    finally:
        # 清理资源
        if 'renderer' in locals():
            renderer.quit()
        logger.info("游戏退出")
        pygame.quit()
        sys.exit(0)


if __name__ == '__main__':
    main()
