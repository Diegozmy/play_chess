import chess_defs
import pygame
import sys

CELL_SIZE = 30

#创建一个 17x17 的空棋盘
board: list[list[chess_defs.Block]] = [
    [chess_defs.Block(terrain=chess_defs.Terrain.PLAIN, piece=None) for _ in range(17)]
    for _ in range(17)
]

# 初始化
pygame.init()
screen = pygame.display.set_mode((CELL_SIZE*17, CELL_SIZE*17))
pygame.display.set_caption("17x17 网格")
clock = pygame.time.Clock()

font = pygame.font.Font("Segoe UI Symbol.ttf", 24)


def draw_character(row, col, char, color):
    """在指定格子中心绘制字符"""
    # 计算格子左上角像素坐标
    x = col * CELL_SIZE
    y = row * CELL_SIZE

    # 渲染字符为 Surface（抗锯齿=True）
    text_surface = font.render(char, True, color)
    # 获取矩形区域并居中
    text_rect = text_surface.get_rect()
    text_rect.center = (x + CELL_SIZE // 2, y + CELL_SIZE // 2)
    # 贴到屏幕上
    screen.blit(text_surface, text_rect)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    #填充背景
    screen.fill((255,255,255))

    #画网格线
    for i in range(18):
        pos = i * CELL_SIZE
        pygame.draw.line(screen, (0,0,0), (pos, 0), (pos, CELL_SIZE*17))
        pygame.draw.line(screen, (0,0,0), (0, pos), (CELL_SIZE*17, pos))

    x,y=0,0
    pygame.draw.rect(screen, (255,0,0), (x*CELL_SIZE+1, y*CELL_SIZE+1, CELL_SIZE-1, CELL_SIZE-1))
    draw_character(0,0,"♞",(255,255,255))
    pygame.display.flip()
    clock.tick(60)

# 退出
pygame.quit()
sys.exit()