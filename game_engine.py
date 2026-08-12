import chess_defs
from collections import deque
from enum import Enum
from dataclasses import dataclass, field


#定义游戏状态
@dataclass(slots=True, kw_only=True)
class GameState:
    board: list[chess_defs.Block]
    now_round: int
    current_player:chess_defs.Owner
    flag_capture_count: dict[chess_defs.Owner, int] = field(default_factory=lambda: {chess_defs.Owner.A: 0, chess_defs.Owner.B: 0})
    trap_count: dict[chess_defs.Owner, int] = field(default_factory=lambda: {chess_defs.Owner.A: 0, chess_defs.Owner.B: 0})
    died_pieces:dict[chess_defs.Owner, list[chess_defs.Piece]]=field(default_factory=lambda: {chess_defs.Owner.A: [], chess_defs.Owner.B: []})
    winner:list[chess_defs.Owner]

#定义动作类型
class ActionType(Enum):
    MOVE=1
    SKILL=2

#定义动作
@dataclass(slots=True, kw_only=True)
class Action:
    type: ActionType
    start: tuple[int, int]
    target:list[tuple[int, int]]

#添加坐标转换
def pos_to_idx(pos:tuple[int, int])->int:
    return pos[0] * 17 + pos[1]

#添加切换玩家
def switch_player(current_player:chess_defs.Owner)->chess_defs.Owner:
    return chess_defs.Owner.B if current_player == chess_defs.Owner.A else chess_defs.Owner.A

#初始化棋盘
def init_board()->list[chess_defs.Block]:
    # 地形数据
    cols_with_rivers = [0, 1, 2, 4, 5, 6, 10, 11, 12, 14, 15, 16]
    rivers = {(row, col) for col in cols_with_rivers for row in range(7, 10)}
    cols_with_bridges = [3, 7, 8, 9, 13]
    bridges = {(row, col) for col in cols_with_bridges for row in range(7, 10)}
    grasses = {(row, col) for col in cols_with_rivers for row in [6, 10]}
    grasses.update((row, col) for col in [1, 5, 11, 15] for row in [5, 11])
    grasses.update((row, col) for col in [6, 10] for row in [0, 1, 2, 16, 15, 14])
    grasses.update((row, col) for col in [7, 8, 9] for row in [3, 13])

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
    board: list[chess_defs.Block] = [
        chess_defs.Block(terrain=determine_terrain((x, y)),
                          piece=None,
                          trap_owner=chess_defs.TrapOwner.NONE)
         for y in range(17)
        for x in range(17)
    ]

    return board

#获取可行移动
directions=[(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1),(1,0),(1,1)]
def get_valid_moves(board:list[chess_defs.Block],pos:tuple[int,int],viewer:chess_defs.Owner,now_round:int) -> list[list[tuple[int,int]]] | None:
    piece=board[pos_to_idx(pos)].piece
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
                if now_round==1 and board[pos_to_idx(end_pos)].terrain == chess_defs.Terrain.BRIDGE:
                    break # 第一回合不能上桥
                if board[pos_to_idx(end_pos)].terrain == chess_defs.Terrain.RIVER:
                    break # 不能进河流
                end_piece = board[pos_to_idx(end_pos)].piece
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

                target_block = board[pos_to_idx(new_pos)]
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
                        or (board[pos_to_idx(new_pos)].terrain == chess_defs.Terrain.GRASS
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

                if board[pos_to_idx(new_pos)].terrain == chess_defs.Terrain.GRASS and remain_stealth > 0:
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
        visited.add(pos)

        while q:
            end_pos, remain_moves, path = q.popleft()

            if remain_moves == 0:
                continue

            for direction in directions:
                new_pos = (end_pos[0] + direction[0], end_pos[1] + direction[1])
                # 边界检查
                if new_pos[0] < 0 or new_pos[0] > 16 or new_pos[1] < 0 or new_pos[1] > 16:
                    continue

                target_block = board[pos_to_idx(new_pos)]
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
                if new_pos not in visited:
                    visited.add(new_pos)
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
        visited.add(pos)

        while q:
            end_pos, remain_moves, path= q.popleft()

            if remain_moves == 0:
                continue

            for direction in directions:
                new_pos = (end_pos[0] + direction[0], end_pos[1] + direction[1])
                # 边界检查
                if new_pos[0] < 0 or new_pos[0] > 16 or new_pos[1] < 0 or new_pos[1] > 16:
                    continue

                target_block = board[pos_to_idx(new_pos)]
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
                if new_pos not in visited:
                    visited.add(new_pos)
                    q.append((*new_state,new_path))

        return result

    return None

#获取弓手的合法目标
def get_archer_targets(board:list[chess_defs.Block],pos:tuple[int,int],viewer:chess_defs.Owner) -> set[tuple[int,int]] | None:
    piece = board[pos_to_idx(pos)].piece
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
                if board[pos_to_idx(end_pos)].terrain==chess_defs.Terrain.GRASS:
                    continue
                end_piece = board[pos_to_idx(end_pos)].piece
                if end_piece is not None:
                    if end_piece.owner != viewer:
                        result.add(end_pos)
                    break

        return result

#获取法师的合法目标
def get_mage_targets(board:list[chess_defs.Block],pos:tuple[int,int],viewer:chess_defs.Owner) -> list[set[tuple[int,int]]] | None:
    piece = board[pos_to_idx(pos)].piece
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
            end_piece = board[pos_to_idx(end_pos)].piece
            if end_piece is not None:
                result.add(end_pos)
                if end_piece.type==chess_defs.PieceType.SHIELD:
                    break
        if result:
            final_result.append(result)

    return final_result

#获取猎手的合法目标
def get_hunter_targets(board:list[chess_defs.Block],pos:tuple[int,int],viewer:chess_defs.Owner) -> set[tuple[int,int]] | None:
    piece = board[pos_to_idx(pos)].piece
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
            end_piece = board[pos_to_idx(end_pos)].piece
            if end_piece is not None and direction!=(0,0):
                continue
            if board[pos_to_idx(end_pos)].trap_owner & chess_defs.TrapOwner(viewer.value):
                continue
            result.add(end_pos)
        return result

#施加动作
def apply_action(state:GameState,action:Action):
    enemy_player=switch_player(state.current_player)
    if action.type==ActionType.MOVE:
        should_break=False
        end_pos=action.target[-1]
        for i in action.target:
            if should_break:
                end_pos=i
                break
            if state.board[pos_to_idx(i)].trap_owner.is_enemy_trap(state.current_player):
                should_break=True
                state.board[pos_to_idx(i)].trap_owner=(
                    state.board[pos_to_idx(i)].trap_owner.resolve_trigger(state.current_player))
                state.trap_count[enemy_player]=(
                    max(0, state.trap_count[enemy_player] - 1))
        if state.board[pos_to_idx(end_pos)].piece is not None:
            state.board[pos_to_idx(end_pos)].piece.viewed=True
            state.died_pieces[state.board[pos_to_idx(end_pos)].piece.owner].append(state.board[pos_to_idx(end_pos)].piece)
            if state.board[pos_to_idx(end_pos)].piece.type==chess_defs.PieceType.COMMANDER:
                state.winner.append(switch_player(state.board[pos_to_idx(end_pos)].piece.owner))
        state.board[pos_to_idx(end_pos)].piece=state.board[pos_to_idx(action.start)].piece
        if should_break:
            state.board[pos_to_idx(end_pos)].piece.viewed = True
        state.board[pos_to_idx(action.start)].piece=None

    if action.type == ActionType.SKILL:
        start_piece=state.board[pos_to_idx(action.start)].piece

        if start_piece.type == chess_defs.PieceType.ARCHER:
            end_pos=action.target[0]
            state.board[pos_to_idx(end_pos)].piece.viewed = True
            state.died_pieces[state.board[pos_to_idx(end_pos)].piece.owner].append(
                state.board[pos_to_idx(end_pos)].piece)
            if state.board[pos_to_idx(end_pos)].piece.type == chess_defs.PieceType.COMMANDER:
                state.winner.append(switch_player(state.board[pos_to_idx(end_pos)].piece.owner))
            state.board[pos_to_idx(end_pos)].piece = None

        elif start_piece.type == chess_defs.PieceType.MAGE:
            for end_pos in action.target:
                state.board[pos_to_idx(end_pos)].piece.viewed = True
                state.died_pieces[state.board[pos_to_idx(end_pos)].piece.owner].append(
                    state.board[pos_to_idx(end_pos)].piece)
                if state.board[pos_to_idx(end_pos)].piece.type == chess_defs.PieceType.COMMANDER:
                    state.winner.append(switch_player(state.board[pos_to_idx(end_pos)].piece.owner))
                state.board[pos_to_idx(end_pos)].piece = None

        elif start_piece.type == chess_defs.PieceType.HUNTER:
            state.board[pos_to_idx(action.target[0])].trap_owner=(
                state.board[pos_to_idx(action.target[0])].trap_owner.place_trap(state.current_player))
            state.trap_count[state.current_player]+=1

        else:
            return None

    state.current_player = enemy_player
    return None