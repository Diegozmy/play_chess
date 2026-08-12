from enum import Enum,IntFlag
from dataclasses import dataclass

# 1. 定义棋子归属
class Owner(Enum):
    A = 1
    B = 2

# 2. 定义棋子类型
class PieceType(Enum):
    KNIGHT = 1
    ASSASSIN = 2
    SHIELD = 3
    ARCHER = 4
    MAGE = 5
    HUNTER = 6
    COMMANDER = 7
    UNKNOWN = 8

# 3. 定义棋子结构
@dataclass(slots=True, kw_only=True)
class Piece:
    owner: Owner
    type: PieceType
    stealth: None | int
    viewed: bool

#4. 定义地形
class Terrain(Enum):
    PLAIN=0
    GRASS=1
    RIVER = 2
    BRIDGE=3

#5.定义陷阱归属
class TrapOwner(IntFlag):
    NONE = 0
    A = 1
    B = 2

#6. 定义格子
@dataclass(slots=True, kw_only=True)
class Block:
    terrain: Terrain
    piece: Piece | None
    trap_owner: TrapOwner