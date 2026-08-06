from enum import Enum
from dataclasses import dataclass

# 1. 定义棋子归属
class Owner(Enum):
    A = -1
    B = 1

# 2. 定义棋子类型
class PieceType(Enum):
    KNIGHT = 1
    ASSASSIN = 2
    SHIELD = 3
    ARCHER = 4
    MAGE = 5
    HUNTER=6
    COMMANDER=7

# 3. 定义棋子结构
@dataclass(slots=True, frozen=True, kw_only=True)
class Piece:
    owner: Owner
    type: PieceType

#4. 定义地形
class Terrain(Enum):
    PLAIN=1
    GRASS=2
    BRIDGE=3
    RIVER=4

#5. 定义格子
@dataclass(slots=True, frozen=True, kw_only=True)
class Block:
    terrain: Terrain
    piece: Piece | None