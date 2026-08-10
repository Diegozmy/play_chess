import chess_defs
from collections import deque

#初始化棋盘
def init_board()->list[list[chess_defs.Block]]:
    # 地形数据
    cols_with_rivers = [0, 1, 2, 4, 5, 6, 10, 11, 12, 14, 15, 16]
    rivers = [(row, col) for col in cols_with_rivers for row in range(7, 10)]
    cols_with_bridges = [3, 7, 8, 9, 13]
    bridges = [(row, col) for col in cols_with_bridges for row in range(7, 10)]
    grasses = [(row, col) for col in cols_with_rivers for row in [6, 10]]
    grasses.extend([(row, col) for col in [1, 5, 11, 15] for row in [5, 11]])
    grasses.extend([(row, col) for col in [6, 10] for row in [0, 1, 2, 16, 15, 14]])
    grasses.extend([(row, col) for col in [7, 8, 9] for row in [3, 13]])

    # 决定初始地形
    def determine_terrain(pos: tuple[int, int]) -> chess_defs.Terrain:
        if pos in grasses:
            return chess_defs.Terrain.GRASS
        if pos in rivers:
            return chess_defs.Terrain.RIVER
        if pos in bridges:
            return chess_defs.Terrain.BRIDGE
        return chess_defs.Terrain.PLAIN

    # 创建一个 17x17 的空棋盘
    board: list[list[chess_defs.Block]] = [
        [chess_defs.Block(terrain=determine_terrain((x, y)),
                          piece=None,
                          trap_owner=chess_defs.TrapOwner.NONE)
         for x in range(17)]
        for y in range(17)
    ]

    return board

#获取可行移动
directions=[(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1),(1,0),(1,1)]
def get_valid_moves(board:list[list[chess_defs.Block]],pos:tuple[int,int],viewer:chess_defs.Owner,now_round:int) -> list[list[tuple[int,int]]] | None:
    piece=board[pos[0]][pos[1]].piece
    result: list[list[tuple[int, int]]] = list()
    if not piece:
        return None
    if piece.owner != viewer:
        return None
    if piece.type == chess_defs.PieceType.KNIGHT:
        steps=9
        for direction in directions:
            end_pos=pos
            path=[]
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
                        path.append(end_pos) # 吃掉对方棋子
                        result.append(path.copy())
                        break # 然后停下
                path.append(end_pos)
                result.append(path.copy())
        return result

    if piece.type == chess_defs.PieceType.ASSASSIN:
        steps = 4
        q = deque()
        visited = set()
        init_state = (pos, steps, piece.stealth)  # (当前位置, 剩余步数, 剩余潜伏值)
        q.append((*init_state,[]))
        visited.add(init_state)

        while q:
            end_pos, remain_moves, remain_stealth, path = q.popleft()

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

                new_path=path+[new_pos]

                if target_piece is not None and target_piece.owner != viewer:
                    result.append(new_path)
                    continue

                if (remain_moves > 0
                        or (board[end_pos[0]][end_pos[1]].terrain == chess_defs.Terrain.GRASS
                        and remain_stealth > 0)
                    ):
                    result.append(new_path)
                else:
                    continue

                if remain_moves > 0:
                    new_state = (new_pos, remain_moves - 1, remain_stealth)
                    if new_state not in visited:
                        visited.add(new_state)
                        q.append((*new_state,new_path))

                if board[end_pos[0]][end_pos[1]].terrain == chess_defs.Terrain.GRASS and remain_stealth > 0:
                    new_state = (new_pos, remain_moves, remain_stealth - 1)
                    if new_state not in visited:
                        visited.add(new_state)
                        q.append((*new_state,new_path))

        return result

    if (piece.type == chess_defs.PieceType.SHIELD
            or piece.type == chess_defs.PieceType.HUNTER
            or piece.type == chess_defs.PieceType.COMMANDER):
        if piece.type == chess_defs.PieceType.SHIELD:
            steps = 2
        else:
            steps = 3
        q = deque()
        visited = set()
        init_state = (pos, steps)  # (当前位置, 剩余步数, 剩余潜伏值)
        q.append((*init_state,[]))
        visited.add(init_state)

        while q:
            end_pos, remain_moves, path = q.popleft()

            if remain_moves == 0:
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

                new_path=path+[new_pos]

                if target_piece is not None and target_piece.owner != viewer:
                    result.append(new_path)
                    continue

                result.append(new_path)

                new_state = (new_pos, remain_moves - 1)
                if new_state not in visited:
                    visited.add(new_state)
                    q.append((*new_state,new_path))

        return result

    if (piece.type == chess_defs.PieceType.ARCHER
            or piece.type == chess_defs.PieceType.MAGE):
        if piece.type == chess_defs.PieceType.MAGE:
            steps = 2
        else:
            steps = 3
        q = deque()
        visited = set()
        init_state = (pos, steps)  # (当前位置, 剩余步数, 剩余潜伏值)
        q.append((*init_state,[]))
        visited.add(init_state)

        while q:
            end_pos, remain_moves, path= q.popleft()

            if remain_moves == 0:
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
                if target_piece is not None:
                    continue

                new_path = path + [new_pos]
                result.append(new_path)

                new_state = (new_pos, remain_moves - 1)
                if new_state not in visited:
                    visited.add(new_state)
                    q.append((*new_state,new_path))

        return result

    return None

#获取弓手的合法目标
def get_archer_targets(board:list[list[chess_defs.Block]],pos:tuple[int,int],viewer:chess_defs.Owner) -> set[tuple[int,int]] | None:
    piece = board[pos[0]][pos[1]].piece
    result: set[tuple[int, int]] = set()
    if not piece:
        return None
    if piece.owner != viewer:
        return None
    if piece.type != chess_defs.PieceType.ARCHER:
        return None
    else:
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        steps = 7
        for direction in directions:
            end_pos = pos
            for _ in range(steps):
                end_pos = (end_pos[0] + direction[0], end_pos[1] + direction[1])
                if end_pos[0] < 0 or end_pos[0] > 16 or end_pos[1] < 0 or end_pos[1] > 16:
                    break  # 目标不在棋盘内
                if board[end_pos[0]][end_pos[1]].terrain==chess_defs.Terrain.GRASS:
                    continue
                end_piece = board[end_pos[0]][end_pos[1]].piece
                if end_piece is not None:
                    if end_piece.owner != viewer:
                        result.add(end_pos)
                    break

        return result

#获取法师的合法目标
def get_mage_targets(board:list[list[chess_defs.Block]],pos:tuple[int,int],viewer:chess_defs.Owner) -> list[set[tuple[int,int]]] | None:
    piece = board[pos[0]][pos[1]].piece
    if not piece:
        return None
    if piece.owner != viewer:
        return None
    if piece.type != chess_defs.PieceType.MAGE:
        return None
    final_result: list[set[tuple[int, int]]] = list()
    steps=3
    for direction in directions:
        result: set[tuple[int, int]]=set()
        end_pos = pos
        for _ in range(steps):
            end_pos = (end_pos[0] + direction[0], end_pos[1] + direction[1])
            if end_pos[0] < 0 or end_pos[0] > 16 or end_pos[1] < 0 or end_pos[1] > 16:
                break  # 目标不在棋盘内
            end_piece = board[end_pos[0]][end_pos[1]].piece
            if end_piece is not None:
                result.add(end_pos)
                if end_piece.type==chess_defs.PieceType.SHIELD:
                    break
        if result:
            final_result.append(result)

    return final_result

#获取猎手的合法目标
def get_hunter_targets(board:list[list[chess_defs.Block]],pos:tuple[int,int],viewer:chess_defs.Owner) -> set[tuple[int,int]] | None:
    piece = board[pos[0]][pos[1]].piece
    result: set[tuple[int, int]] = set()
    if not piece:
        return None
    if piece.owner != viewer:
        return None
    if piece.type != chess_defs.PieceType.HUNTER:
        return None
    else:
        directions = [(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,0)]
        for direction in directions:
            end_pos = pos
            end_pos = (end_pos[0] + direction[0], end_pos[1] + direction[1])
            if end_pos[0] < 0 or end_pos[0] > 16 or end_pos[1] < 0 or end_pos[1] > 16:
                continue  # 目标不在棋盘内
            end_piece = board[end_pos[0]][end_pos[1]].piece
            if end_piece is not None and direction!=(0,0):
                continue
            if board[end_pos[0]][end_pos[1]].trap_owner & chess_defs.TrapOwner(viewer.value):
                continue
            result.add(end_pos)
        return result

