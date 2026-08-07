import chess_defs
import pygame
import sys
from random import randint
CELL_SIZE = 55

#创建一个 17x17 的空棋盘
board: list[list[chess_defs.Block]] = [
    [chess_defs.Block(terrain=chess_defs.Terrain.PLAIN,
                      piece=None,
                      trap_owner=chess_defs.TrapOwner.NONE)
        for _ in range(17)]
    for _ in range(17)
]

# 初始化
pygame.init()
screen = pygame.display.set_mode((CELL_SIZE*17, CELL_SIZE*17))
pygame.display.set_caption("17x17 网格")
clock = pygame.time.Clock()

#地形颜色
ColorsTerrain={
            chess_defs.Terrain.PLAIN:(218, 215, 170),
            chess_defs.Terrain.GRASS:(86, 124, 27),
            chess_defs.Terrain.RIVER:(156, 178, 206),
            chess_defs.Terrain.BRIDGE:(100, 55, 25)
        }

#棋子颜色
Icons={ow:{
            pt : pygame.transform.scale(
                pygame.image.load(f"./chessIco/{ow.value}/{pt.value}.png").convert(),
                (CELL_SIZE-5, CELL_SIZE-5)
            )
            for pt in chess_defs.PieceType
            }
       for ow in chess_defs.Owner
}

#放置棋子
for ow in chess_defs.Owner:
    for pt in chess_defs.PieceType:
        board[ow.value][pt.value] = chess_defs.Block(terrain=chess_defs.Terrain(randint(0,3)),
                                       piece=chess_defs.Piece(owner=ow,
                                                              type=pt),
                                       trap_owner=chess_defs.TrapOwner.NONE
                                       )

#绘制过程
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

    #绘制棋盘
    for x in range(17):
        for y in range(17):
            block = board[x][y]
            #绘制地形
            pygame.draw.rect(screen, ColorsTerrain[block.terrain],
                             (x * CELL_SIZE + 1, y * CELL_SIZE + 1, CELL_SIZE - 1, CELL_SIZE - 1))
            #绘制棋子
            if block.piece is not None:
                screen.blit(Icons[block.piece.owner][block.piece.type],
                            (x * CELL_SIZE + 3, y * CELL_SIZE + 3))

    pygame.display.flip()
    clock.tick(60)

# 退出
pygame.quit()
sys.exit()