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

board[0][0]=chess_defs.Block(terrain=chess_defs.Terrain.RIVER,
                             piece=chess_defs.Piece(owner=chess_defs.Owner.A,
                                                    type=chess_defs.PieceType.COMMANDER))


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

    y=0
    colors=[(218, 215, 170),
            (86, 124, 27),
            (156, 178, 206),
            (109, 55, 25)]

    for x in range(17):
        for y in range(17):
            #绘制地形
            pygame.draw.rect(screen, colors[board[x][y].terrain.value], (x * CELL_SIZE + 1, y * CELL_SIZE + 1, CELL_SIZE - 1, CELL_SIZE - 1))
            #绘制棋子

    pygame.display.flip()
    clock.tick(60)

# 退出
pygame.quit()
sys.exit()