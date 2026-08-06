import chess_defs

#创建一个 17x17 的空棋盘
board: list[list[chess_defs.Block]] = [
    [chess_defs.Block(terrain=chess_defs.Terrain.PLAIN, piece=None) for _ in range(17)]
    for _ in range(17)
]

board[0][0]=chess_defs.Block(terrain=chess_defs.Terrain.PLAIN,
                             piece=chess_defs.Piece(owner=chess_defs.Owner.A,
                                                    type=chess_defs.PieceType.COMMANDER))

print(board[0][0].piece.owner)