# Chess Game

A simple chess game implementation using Python and Tkinter.

## Features

- Graphical chess board using Tkinter
- Proper piece movement rules
- Turn-based gameplay (white goes first)
- Check detection
- Piece capture

## Requirements

- Python 3.x
- Tkinter (usually comes pre-installed with Python)

## How to Run

```bash
python chess_game.py
```

## How to Play

1. Click on a piece to select it
2. Valid moves will be highlighted in green
3. Click on a highlighted square to move the selected piece
4. Take turns between white and black
5. Capture opponent's pieces by moving onto their squares
6. The game will notify you when a player is in check
7. The game ends when a king is captured

## Implementation Details

- The board is represented as an 8x8 grid
- Pieces are displayed using Unicode chess symbols
- Each piece follows its traditional chess movement rules
- The game includes special rules for pawns (double move from starting position)

## Future Improvements

- Add castling, en passant, and pawn promotion rules
- Implement proper checkmate detection
- Add game timer
- Include move history
- Add save/load game functionality
- Implement a simple AI opponent