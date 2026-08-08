import chess_defs
import pygame
import sys
from collections import deque


#格子大小
CELL_SIZE = 55
now_round=2

#地形数据
cols_with_rivers = [0,1,2,4,5,6,10,11,12,14,15,16]
rivers=[(row,col) for col in cols_with_rivers for row in range(7,10)]
cols_with_bridges = [3,7,8,9,13]
bridges=[(row,col) for col in cols_with_bridges for row in range(7,10)]
grasses = [(row,col) for col in cols_with_rivers for row in [6,10]]
grasses.extend([(row,col) for col in [1,5,11,15] for row in [5,11]])
grasses.extend([(row, col) for col in [6,10] for row in [0,1,2,16,15,14]])
grasses.extend([(row, col) for col in [7,8,9] for row in [3,13]])

#决定初始地形
def determine_terrain(pos:tuple[int, int])->chess_defs.Terrain:
    if pos in grasses:
        return chess_defs.Terrain.GRASS
    if pos in rivers:
        return chess_defs.Terrain.RIVER
    if pos in bridges:
        return chess_defs.Terrain.BRIDGE
    return chess_defs.Terrain.PLAIN


#创建一个 17x17 的空棋盘
board: list[list[chess_defs.Block]] = [
    [chess_defs.Block(terrain=determine_terrain((x,y)),
                      piece=None,
                      trap_owner=chess_defs.TrapOwner.NONE)
        for x in range(17)]
    for y in range(17)
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

board[0][2]=chess_defs.Block(terrain=chess_defs.Terrain.PLAIN,
                                       piece=chess_defs.Piece(owner=chess_defs.Owner.A,
                                                              type=chess_defs.PieceType.ASSASSIN,
                                                              viewed=False,
                                                              stealth=1
                                                              ),
                                       trap_owner=chess_defs.TrapOwner.NONE
                                       )







#获取可行移动
directions=[(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1),(1,0),(1,1)]
def get_valid_moves(pos:tuple[int,int],viewer:chess_defs.Owner) -> set[tuple[int,int]] | None:
    piece=board[pos[0]][pos[1]].piece
    result: set[tuple[int, int]] = set()
    if not piece:
        return None
    if piece.owner != viewer:
        return None
    if piece.type == chess_defs.PieceType.KNIGHT:
        steps=9
        for direction in directions:
            end_pos=pos
            for _ in range(steps):
                end_pos = (end_pos[0] + direction[0], end_pos[1] + direction[1])
                if end_pos[0] < 0 or end_pos[0] > 16 or end_pos[1] < 0 or end_pos[1] > 16:
                    break # 目标不在棋盘内
                if now_round==1 and board[end_pos[0]][end_pos[1]].terrain == chess_defs.Terrain.BRIDGE:
                    break # 第一回合不能上桥
                if board[end_pos[0]][end_pos[1]].terrain == chess_defs.Terrain.RIVER:
                    break # 不能进河流
                end_piece = board[end_pos[0]][end_pos[1]].piece
                if end_piece is not None:
                    if end_piece.owner == viewer:
                        break # 不能吃自己的棋子
                    else:
                        result.add(end_pos) # 吃掉对方棋子
                        break # 然后停下
                result.add(end_pos)
        return result

    if piece.type == chess_defs.PieceType.ASSASSIN:
        steps = 4
        q = deque()
        visited = set()
        init_state = (pos, steps, piece.stealth)  # (当前位置, 剩余步数, 剩余潜伏值)
        q.append(init_state)
        visited.add(init_state)

        while q:
            end_pos, remain_moves, remain_stealth = q.popleft()

            if remain_moves == 0 and remain_stealth == 0:
                continue

            for direction in directions:

                new_pos = (end_pos[0] + direction[0], end_pos[1] + direction[1])

                # 边界检查
                if new_pos[0] < 0 or new_pos[0] > 16 or new_pos[1] < 0 or new_pos[1] > 16:
                    continue

                target_block = board[new_pos[0]][new_pos[1]]
                terrain = target_block.terrain
                if terrain == chess_defs.Terrain.RIVER:
                    continue
                if now_round == 1 and terrain == chess_defs.Terrain.BRIDGE:
                    continue

                target_piece = target_block.piece
                if target_piece is not None and target_piece.owner == viewer:
                    continue
                if target_piece is not None and target_piece.owner != viewer:
                    result.add(new_pos)
                    continue

                if remain_moves > 0 or board[end_pos[0]][end_pos[1]].terrain == chess_defs.Terrain.GRASS and remain_stealth > 0:
                    result.add(new_pos)
                else:
                    continue

                if remain_moves > 0:
                    new_state = (new_pos, remain_moves - 1, remain_stealth)
                    if new_state not in visited:
                        visited.add(new_state)
                        q.append(new_state)

                if board[end_pos[0]][end_pos[1]].terrain == chess_defs.Terrain.GRASS and remain_stealth > 0:
                    new_state = (new_pos, remain_moves, remain_stealth - 1)
                    if new_state not in visited:
                        visited.add(new_state)
                        q.append(new_state)

        return result







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


    for x,y in get_valid_moves((0, 2), chess_defs.Owner.A):
        pygame.draw.rect(screen, (255,255,255),
                                 (x * CELL_SIZE + 1, y * CELL_SIZE + 1, CELL_SIZE - 1, CELL_SIZE - 1))

    pygame.display.flip()
    clock.tick(60)

# 退出
pygame.quit()
sys.exit()