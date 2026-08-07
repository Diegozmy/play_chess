import chess_defs
import pygame
import sys

CELL_SIZE = 55

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

board[0][0]=chess_defs.Block(terrain=chess_defs.Terrain.PLAIN,
                             piece=chess_defs.Piece(owner=chess_defs.Owner.B,
                                                    type=chess_defs.PieceType.KNIGHT))

Colors={
            chess_defs.Terrain.PLAIN:(218, 215, 170),
            chess_defs.Terrain.GRASS:(86, 124, 27),
            chess_defs.Terrain.RIVER:(156, 178, 206),
            chess_defs.Terrain.BRIDGE:(100, 55, 25)
        }

Icons={
    chess_defs.Owner.A:[pygame.transform.scale(pygame.image.load(f"./chessIco/-1/{i}.PNG").convert(), (CELL_SIZE-5, CELL_SIZE-5))
                        for i in range(1,9)],
    chess_defs.Owner.B:[pygame.transform.scale(pygame.image.load(f"./chessIco/1/{i}.PNG").convert(), (CELL_SIZE-5, CELL_SIZE-5))
                        for i in range(1,9)]
}

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


    for x in range(17):
        for y in range(17):
            #绘制地形
            pygame.draw.rect(screen, Colors[board[x][y].terrain],
                             (x * CELL_SIZE + 1, y * CELL_SIZE + 1, CELL_SIZE - 1, CELL_SIZE - 1))
            #绘制棋子
            if board[x][y].piece is not None:
                screen.blit(Icons[board[x][y].piece.owner][board[x][y].piece.type.value - 1],
                            (x * CELL_SIZE + 3, y * CELL_SIZE + 3))

    pygame.display.flip()
    clock.tick(60)

# 退出
pygame.quit()
sys.exit()