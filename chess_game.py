import tkinter as tk
from tkinter import messagebox
import os

class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")
        self.root.resizable(False, False)
        
        # Game state
        self.selected_piece = None
        self.turn = "white"  # white or black
        self.board = self.initialize_board()
        
        # Constants
        self.SQUARE_SIZE = 80
        self.BOARD_SIZE = 8
        
        # Colors
        self.LIGHT_SQUARE_COLOR = "#f0d9b5"  # light square
        self.DARK_SQUARE_COLOR = "#b58863"   # dark square
        self.HIGHLIGHT_COLOR = "#aaaaff"    # highlighted square
        self.POSSIBLE_MOVE_COLOR = "#bbff99" # possible move
        
        # Unicode Chess Pieces
        self.PIECES = {
            "white_pawn": "\u2659", "white_rook": "\u2656", "white_knight": "\u2658", 
            "white_bishop": "\u2657", "white_queen": "\u2655", "white_king": "\u2654",
            "black_pawn": "\u265f", "black_rook": "\u265c", "black_knight": "\u265e", 
            "black_bishop": "\u265d", "black_queen": "\u265b", "black_king": "\u265a"
        }
        
        # GUI Setup
        self.canvas = tk.Canvas(root, width=self.SQUARE_SIZE * self.BOARD_SIZE, 
                              height=self.SQUARE_SIZE * self.BOARD_SIZE)
        self.canvas.pack()
        
        # Dictionary to keep track of highlighted possible moves
        self.highlighted_squares = []
        
        # Draw initial board
        self.draw_board()
        self.draw_pieces()
        
        # Bind click events
        self.canvas.bind("<Button-1>", self.handle_click)
        
        # Status label
        self.status_label = tk.Label(root, text=f"Current turn: {self.turn.capitalize()}")
        self.status_label.pack()
        
    def initialize_board(self):
        """Initialize the chess board with pieces in starting positions"""
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Place pawns
        for col in range(8):
            board[1][col] = {"type": "pawn", "color": "black"}
            board[6][col] = {"type": "pawn", "color": "white"}
            
        # Place rooks
        board[0][0] = board[0][7] = {"type": "rook", "color": "black"}
        board[7][0] = board[7][7] = {"type": "rook", "color": "white"}
        
        # Place knights
        board[0][1] = board[0][6] = {"type": "knight", "color": "black"}
        board[7][1] = board[7][6] = {"type": "knight", "color": "white"}
        
        # Place bishops
        board[0][2] = board[0][5] = {"type": "bishop", "color": "black"}
        board[7][2] = board[7][5] = {"type": "bishop", "color": "white"}
        
        # Place queens
        board[0][3] = {"type": "queen", "color": "black"}
        board[7][3] = {"type": "queen", "color": "white"}
        
        # Place kings
        board[0][4] = {"type": "king", "color": "black"}
        board[7][4] = {"type": "king", "color": "white"}
        
        return board
        
    def draw_board(self):
        """Draw the chess board"""
        for row in range(8):
            for col in range(8):
                # Calculate position
                x0 = col * self.SQUARE_SIZE
                y0 = row * self.SQUARE_SIZE
                x1 = x0 + self.SQUARE_SIZE
                y1 = y0 + self.SQUARE_SIZE
                
                # Get square color
                if (row + col) % 2 == 0:
                    color = self.LIGHT_SQUARE_COLOR
                else:
                    color = self.DARK_SQUARE_COLOR
                    
                # Draw the square
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
    
    def draw_pieces(self):
        """Draw all pieces on the board"""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    x = col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    y = row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    piece_symbol = self.PIECES[f"{piece['color']}_{piece['type']}"]
                    
                    # Adjust font size based on platform
                    font_size = 40
                    
                    self.canvas.create_text(
                        x, y, text=piece_symbol, fill="black", 
                        font=("Arial", font_size, "bold")
                    )
                    
    def highlight_possible_moves(self, row, col):
        """Highlight squares where selected piece can move"""
        # Clear any previous highlights
        self.clear_highlights()
        
        piece = self.board[row][col]
        if not piece or piece["color"] != self.turn:
            return []
        
        possible_moves = self.get_possible_moves(row, col)
        
        # Highlight the possible moves
        for move_row, move_col in possible_moves:
            x0 = move_col * self.SQUARE_SIZE
            y0 = move_row * self.SQUARE_SIZE
            x1 = x0 + self.SQUARE_SIZE
            y1 = y0 + self.SQUARE_SIZE
            
            # Highlight with a different color
            highlight = self.canvas.create_rectangle(
                x0, y0, x1, y1, fill=self.POSSIBLE_MOVE_COLOR, stipple="gray50"
            )
            self.highlighted_squares.append(highlight)
            
        return possible_moves
        
    def clear_highlights(self):
        """Clear all highlighted squares"""
        for highlight in self.highlighted_squares:
            self.canvas.delete(highlight)
        self.highlighted_squares = []
        
    def get_possible_moves(self, row, col):
        """Get all possible moves for a piece at the given position"""
        piece = self.board[row][col]
        if not piece:
            return []
            
        moves = []
        piece_type = piece["type"]
        color = piece["color"]
        
        # Pawns
        if piece_type == "pawn":
            direction = -1 if color == "white" else 1
            
            # Move forward one square
            if 0 <= row + direction < 8 and not self.board[row + direction][col]:
                moves.append((row + direction, col))
                
                # Can move two squares from starting position
                starting_row = 6 if color == "white" else 1
                if row == starting_row and not self.board[row + 2*direction][col]:
                    moves.append((row + 2*direction, col))
            
            # Capture diagonally
            for dx in [-1, 1]:
                capture_row, capture_col = row + direction, col + dx
                if (0 <= capture_row < 8 and 0 <= capture_col < 8 and 
                    self.board[capture_row][capture_col] and 
                    self.board[capture_row][capture_col]["color"] != color):
                    moves.append((capture_row, capture_col))
        
        # Rooks (and part of queen movement)
        if piece_type in ["rook", "queen"]:
            # Horizontal and vertical movement
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                r, c = row + dr, col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    if not self.board[r][c]:  # Empty square
                        moves.append((r, c))
                    else:  # Occupied square
                        if self.board[r][c]["color"] != color:  # Can capture
                            moves.append((r, c))
                        break  # Stop after hitting a piece
                    r += dr
                    c += dc
        
        # Bishops (and part of queen movement)
        if piece_type in ["bishop", "queen"]:
            # Diagonal movement
            for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                r, c = row + dr, col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    if not self.board[r][c]:  # Empty square
                        moves.append((r, c))
                    else:  # Occupied square
                        if self.board[r][c]["color"] != color:  # Can capture
                            moves.append((r, c))
                        break  # Stop after hitting a piece
                    r += dr
                    c += dc
        
        # Knights
        if piece_type == "knight":
            knight_moves = [
                (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1)
            ]
            for dr, dc in knight_moves:
                r, c = row + dr, col + dc
                if (0 <= r < 8 and 0 <= c < 8 and 
                    (not self.board[r][c] or self.board[r][c]["color"] != color)):
                    moves.append((r, c))
        
        # King
        if piece_type == "king":
            king_moves = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1),           (0, 1),
                (1, -1),  (1, 0),  (1, 1)
            ]
            for dr, dc in king_moves:
                r, c = row + dr, col + dc
                if (0 <= r < 8 and 0 <= c < 8 and 
                    (not self.board[r][c] or self.board[r][c]["color"] != color)):
                    moves.append((r, c))
        
        return moves
        
    def handle_click(self, event):
        """Handle click events on the chess board"""
        col = event.x // self.SQUARE_SIZE
        row = event.y // self.SQUARE_SIZE
        
        # If a piece is already selected
        if self.selected_piece:
            selected_row, selected_col = self.selected_piece
            possible_moves = self.get_possible_moves(selected_row, selected_col)
            
            # If clicked on a possible move
            if (row, col) in possible_moves:
                # Move the piece
                self.move_piece(selected_row, selected_col, row, col)
                self.selected_piece = None
                self.clear_highlights()
                
                # Check for check status
                if self.is_in_check(self.turn):
                    messagebox.showinfo("Check", f"{self.turn.capitalize()} is in check!")
                
                # Check if either king has been captured (simplified win condition)
                if self.is_king_captured():
                    winner = "Black" if self.turn == "white" else "White"
                    messagebox.showinfo("Game Over", f"{winner} wins!")
                    self.reset_game()
                    return
                
                # Switch turns
                self.turn = "black" if self.turn == "white" else "white"
                self.status_label.config(text=f"Current turn: {self.turn.capitalize()}")
                
            else:
                # If clicked on another piece of same color, select that piece instead
                piece = self.board[row][col]
                if piece and piece["color"] == self.turn:
                    self.selected_piece = (row, col)
                    self.highlight_possible_moves(row, col)
                else:
                    # Deselect if clicked elsewhere
                    self.selected_piece = None
                    self.clear_highlights()
        else:
            # Select a piece
            piece = self.board[row][col]
            if piece and piece["color"] == self.turn:
                self.selected_piece = (row, col)
                self.highlight_possible_moves(row, col)
    
    def move_piece(self, from_row, from_col, to_row, to_col):
        """Move a piece on the board"""
        # Move piece in the board data structure
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None
        
        # Redraw the board
        self.draw_board()
        self.draw_pieces()
    
    def is_king_captured(self):
        """Check if either king has been captured (simplified)"""
        white_king_exists = False
        black_king_exists = False
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece["type"] == "king":
                    if piece["color"] == "white":
                        white_king_exists = True
                    else:
                        black_king_exists = True
        
        return not (white_king_exists and black_king_exists)
    
    def is_in_check(self, color):
        """Check if the given color's king is in check"""
        # Find king position
        king_row, king_col = None, None
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece["type"] == "king" and piece["color"] == color:
                    king_row, king_col = row, col
                    break
            if king_row is not None:
                break
        
        # If king not found, return False
        if king_row is None:
            return False
        
        # Check if any opponent's piece can capture the king
        opponent_color = "black" if color == "white" else "white"
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece["color"] == opponent_color:
                    possible_moves = self.get_possible_moves(row, col)
                    if (king_row, king_col) in possible_moves:
                        return True
        
        return False
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.board = self.initialize_board()
        self.turn = "white"
        self.selected_piece = None
        self.clear_highlights()
        self.draw_board()
        self.draw_pieces()
        self.status_label.config(text=f"Current turn: {self.turn.capitalize()}")

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()