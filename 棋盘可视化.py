import chess_defs
import game_engine
import pygame
import sys


#格子大小
CELL_SIZE = 55
now_round=2

board=game_engine.init_board()


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
chess_place=[
             [chess_defs.PieceType.MAGE,chess_defs.PieceType.COMMANDER,chess_defs.PieceType.HUNTER],
             [chess_defs.PieceType.ARCHER,chess_defs.PieceType.ASSASSIN,chess_defs.PieceType.ARCHER],
             [chess_defs.PieceType.KNIGHT,chess_defs.PieceType.SHIELD,chess_defs.PieceType.KNIGHT]
             ]


for i in range(3):
    for j in range(3):
        if chess_place[i][j] != chess_defs.PieceType.ASSASSIN:
            stealth=None
        else:
            stealth=10
        board[j+7][i]=chess_defs.Block(terrain=chess_defs.Terrain.PLAIN,
                                       piece=chess_defs.Piece(owner=chess_defs.Owner.A,
                                                              type=chess_place[i][j],
                                                              viewed=False,
                                                              stealth=stealth
                                                              ),
                                       trap_owner=chess_defs.TrapOwner.NONE
                                       )


for i in range(3):
    for j in range(3):
        if chess_place[i][j] != chess_defs.PieceType.ASSASSIN:
            stealth=None
        else:
            stealth=10
        board[j+7][i+14]=chess_defs.Block(terrain=chess_defs.Terrain.PLAIN,
                                       piece=chess_defs.Piece(owner=chess_defs.Owner.B,
                                                              type=chess_place[2-i][j],
                                                              viewed=False,
                                                              stealth=stealth
                                                              ),
                                       trap_owner=chess_defs.TrapOwner.NONE
                                       )

board[7][13]=chess_defs.Block(terrain=chess_defs.Terrain.PLAIN,
                                       piece=chess_defs.Piece(owner=chess_defs.Owner.A,
                                                              type=chess_defs.PieceType.COMMANDER,
                                                              viewed=False,
                                                              stealth=4
                                                              ),
                                       trap_owner=chess_defs.TrapOwner.NONE
                                       )


viewer=chess_defs.Owner.A #定义观察者
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
                if block.piece.owner == viewer or block.piece.viewed: #只显示自己的或已翻面的棋子
                    screen.blit(Icons[block.piece.owner][block.piece.type],
                                (x * CELL_SIZE + 3, y * CELL_SIZE + 3))
                else:
                    screen.blit(Icons[block.piece.owner][chess_defs.PieceType.UNKNOWN],
                                (x * CELL_SIZE + 3, y * CELL_SIZE + 3))


    for i in game_engine.get_valid_moves(board, (7, 13), chess_defs.Owner.A, 1):
        for x, y in i:
            pygame.draw.rect(screen, (255, 255, 255),
                             (x * CELL_SIZE + 1, y * CELL_SIZE + 1, CELL_SIZE - 1, CELL_SIZE - 1))

    pygame.display.flip()
    clock.tick(60)

# 退出
pygame.quit()
sys.exit()