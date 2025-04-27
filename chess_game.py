import tkinter as tk
from tkinter import messagebox, simpledialog

class ChessGame:
    def __init__(self, root):
        """Initialize the chess game with GUI and game logic."""
        self.root = root
        self.root.title("Chess Game")
        self.root.resizable(False, False)
        
        # Game state
        self.selected_piece = None
        self.turn = "white"  # white or black
        self.board = self.initialize_board()
        self.check_status = {"white": False, "black": False}
        
        # Constants
        self.SQUARE_SIZE = 80
        self.BOARD_SIZE = 8
        
        # Colors
        self.LIGHT_SQUARE_COLOR = "#f0d9b5"  # light square
        self.DARK_SQUARE_COLOR = "#b58863"   # dark square
        self.HIGHLIGHT_COLOR = "#aaaaff"     # highlighted square
        self.POSSIBLE_MOVE_COLOR = "#bbff99" # possible move
        self.CHECK_COLOR = "#ff6666"         # check highlight
        
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
        
        # Control panel
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(self.control_frame, text=f"Current turn: {self.turn.capitalize()}", font=("Arial", 12))
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Reset button
        self.reset_button = tk.Button(self.control_frame, text="New Game", command=self.reset_game)
        self.reset_button.pack(side=tk.RIGHT, padx=10)
        
        # Move history
        self.history_frame = tk.Frame(root)
        self.history_frame.pack(pady=5, fill=tk.X)
        
        self.history_label = tk.Label(self.history_frame, text="Move History", font=("Arial", 10, "bold"))
        self.history_label.pack()
        
        self.history_text = tk.Text(self.history_frame, width=30, height=5, font=("Arial", 9))
        self.history_text.pack()
        self.move_history = []
        
    def initialize_board(self):
        """Initialize the chess board with pieces in starting positions."""
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Place pawns
        for col in range(8):
            board[1][col] = {"type": "pawn", "color": "black", "has_moved": False}
            board[6][col] = {"type": "pawn", "color": "white", "has_moved": False}
            
        # Place rooks
        board[0][0] = board[0][7] = {"type": "rook", "color": "black", "has_moved": False}
        board[7][0] = board[7][7] = {"type": "rook", "color": "white", "has_moved": False}
        
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
        board[0][4] = {"type": "king", "color": "black", "has_moved": False}
        board[7][4] = {"type": "king", "color": "white", "has_moved": False}
        
        return board
        
    def draw_board(self):
        """Draw the chess board with alternating square colors."""
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
                
                # Add coordinate labels on the edges of the board
                if col == 0:  # Add row numbers on the left edge
                    self.canvas.create_text(
                        5, y0 + 10, 
                        text=str(8 - row), 
                        anchor="nw", 
                        fill="#555555", 
                        font=("Arial", 8)
                    )
                
                if row == 7:  # Add column letters on the bottom edge
                    self.canvas.create_text(
                        x0 + self.SQUARE_SIZE - 10, y1 - 5, 
                        text=chr(97 + col),  # 'a' through 'h'
                        anchor="se", 
                        fill="#555555", 
                        font=("Arial", 8)
                    )
    
    def draw_pieces(self):
        """Draw all pieces on the board with proper icons."""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    x = col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    y = row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    piece_symbol = self.PIECES[f"{piece['color']}_{piece['type']}"]
                    
                    # Use a standard font size
                    font_size = 40
                    
                    self.canvas.create_text(
                        x, y, text=piece_symbol, fill="black", 
                        font=("Arial", font_size, "bold")
                    )
                    
    def highlight_possible_moves(self, row, col):
        """Highlight squares where selected piece can move."""
        # Clear any previous highlights
        self.clear_highlights()
        
        piece = self.board[row][col]
        if not piece or piece["color"] != self.turn:
            return []
        
        possible_moves = self.get_legal_moves(row, col)
        
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
        
        # Also highlight the selected piece
        x0 = col * self.SQUARE_SIZE
        y0 = row * self.SQUARE_SIZE
        x1 = x0 + self.SQUARE_SIZE
        y1 = y0 + self.SQUARE_SIZE
        highlight = self.canvas.create_rectangle(
            x0, y0, x1, y1, outline=self.HIGHLIGHT_COLOR, width=3
        )
        self.highlighted_squares.append(highlight)
            
        return possible_moves
        
    def clear_highlights(self):
        """Clear all highlighted squares."""
        for highlight in self.highlighted_squares:
            self.canvas.delete(highlight)
        self.highlighted_squares = []
        
    def get_possible_moves(self, row, col):
        """Get all possible moves for a piece at the given position without checking for check."""
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
                
                # Can move two squares from starting position if both squares are empty
                if not piece.get("has_moved", True):  # Check if pawn hasn't moved
                    if (0 <= row + 2*direction < 8 and 
                        not self.board[row + direction][col] and  # Check first square
                        not self.board[row + 2*direction][col]):  # Check second square
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
    
    def get_legal_moves(self, row, col):
        """Get all legal moves for a piece considering check rules."""
        piece = self.board[row][col]
        if not piece:
            return []
        
        color = piece["color"]
        possible_moves = self.get_possible_moves(row, col)
        legal_moves = []
        
        # Check each move to see if it would leave the king in check
        for move_row, move_col in possible_moves:
            # Make a temporary move
            temp_board = [row[:] for row in self.board]
            temp_board[move_row][move_col] = temp_board[row][col]
            temp_board[row][col] = None
            
            # Check if the king is in check after this move
            if not self.would_be_in_check(color, temp_board):
                legal_moves.append((move_row, move_col))
        
        return legal_moves
    
    def would_be_in_check(self, color, board):
        """Check if the given color's king would be in check with the given board state."""
        # Find king position
        king_row, king_col = None, None
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
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
                piece = board[row][col]
                if piece and piece["color"] == opponent_color:
                    # Get possible moves for this opponent piece
                    for dr, dc in self.get_attack_squares(row, col, board):
                        if (dr, dc) == (king_row, king_col):
                            return True
        
        return False
    
    def get_attack_squares(self, row, col, board):
        """Get squares that a piece can attack, used for check detection."""
        piece = board[row][col]
        if not piece:
            return []
            
        attack_squares = []
        piece_type = piece["type"]
        color = piece["color"]
        
        # Pawns attack diagonally
        if piece_type == "pawn":
            direction = -1 if color == "white" else 1
            for dx in [-1, 1]:
                attack_row, attack_col = row + direction, col + dx
                if 0 <= attack_row < 8 and 0 <= attack_col < 8:
                    attack_squares.append((attack_row, attack_col))
        
        # Rooks (and part of queen)
        if piece_type in ["rook", "queen"]:
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                r, c = row + dr, col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    attack_squares.append((r, c))
                    if board[r][c]:  # Stop at any piece (friend or foe)
                        break
                    r += dr
                    c += dc
        
        # Bishops (and part of queen)
        if piece_type in ["bishop", "queen"]:
            for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                r, c = row + dr, col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    attack_squares.append((r, c))
                    if board[r][c]:  # Stop at any piece
                        break
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
                if 0 <= r < 8 and 0 <= c < 8:
                    attack_squares.append((r, c))
        
        # King
        if piece_type == "king":
            king_moves = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1),           (0, 1),
                (1, -1),  (1, 0),  (1, 1)
            ]
            for dr, dc in king_moves:
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    attack_squares.append((r, c))
        
        return attack_squares
        
    def handle_click(self, event):
        """Handle click events on the chess board."""
        col = event.x // self.SQUARE_SIZE
        row = event.y // self.SQUARE_SIZE
        
        # If a piece is already selected
        if self.selected_piece:
            selected_row, selected_col = self.selected_piece
            possible_moves = self.get_legal_moves(selected_row, selected_col)
            
            # If clicked on a possible move
            if (row, col) in possible_moves:
                # Move the piece
                self.move_piece(selected_row, selected_col, row, col)
                self.selected_piece = None
                self.clear_highlights()
                
                # Check for check status after move
                opponent = "black" if self.turn == "white" else "white"
                
                # Check if opponent is in check
                if self.is_in_check(opponent):
                    self.check_status[opponent] = True
                    if self.is_checkmate(opponent):
                        messagebox.showinfo("Checkmate", f"{opponent.capitalize()} is in checkmate! {self.turn.capitalize()} wins!")
                        self.reset_game()
                        return
                    else:
                        messagebox.showinfo("Check", f"{opponent.capitalize()} is in check!")
                else:
                    self.check_status[opponent] = False
                
                # Switch turns
                self.turn = opponent
                self.status_label.config(text=f"Current turn: {self.turn.capitalize()}")
                
                # Check for stalemate
                if self.is_stalemate(self.turn):
                    messagebox.showinfo("Stalemate", f"Stalemate! The game is a draw.")
                    self.reset_game()
                    return
                
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
        """Move a piece on the board and handle special cases like pawn promotion."""
        piece = self.board[from_row][from_col]
        
        # Record the move in algebraic notation
        from_coord = chr(97 + from_col) + str(8 - from_row)
        to_coord = chr(97 + to_col) + str(8 - to_row)
        
        piece_letter = ""
        if piece["type"] != "pawn":
            piece_letter = piece["type"][0].upper()
            if piece["type"] == "knight":  # Knight uses 'N' instead of 'K'
                piece_letter = "N"
        
        captured = "x" if self.board[to_row][to_col] else ""
        move_text = f"{piece_letter}{from_coord}{captured}{to_coord}"
        
        # Handle pawn promotion
        is_promotion = False
        if piece["type"] == "pawn" and (to_row == 0 or to_row == 7):
            is_promotion = True
            promotion_options = ["queen", "rook", "bishop", "knight"]
            promotion_piece = simpledialog.askstring(
                "Pawn Promotion",
                "Choose promotion piece (queen, rook, bishop, knight):",
                initialvalue="queen"
            )
            
            if promotion_piece is None or promotion_piece.lower() not in promotion_options:
                promotion_piece = "queen"  # Default to queen
            
            # Update the piece type
            piece["type"] = promotion_piece.lower()
            move_text += f"={promotion_piece[0].upper()}"
        
        # Mark the piece as having moved
        piece["has_moved"] = True
        
        # Move piece in the board data structure
        self.board[to_row][to_col] = self.board[from_row][from_col]
        self.board[from_row][from_col] = None
        
        # Update move history
        self.move_history.append(move_text)
        move_number = (len(self.move_history) + 1) // 2
        if len(self.move_history) % 2 == 1:  # White's move
            history_entry = f"{move_number}. {move_text}"
        else:  # Black's move
            history_entry = f"{move_text}\n"
            
        self.history_text.insert(tk.END, history_entry)
        self.history_text.see(tk.END)  # Scroll to see the latest move
        
        # Redraw the board
        self.draw_board()
        self.draw_pieces()
        
        # If king or opponent is in check, highlight the king
        for color in ["white", "black"]:
            if self.is_in_check(color):
                self.highlight_king_in_check(color)
    
    def highlight_king_in_check(self, color):
        """Highlight the king that is in check."""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece["type"] == "king" and piece["color"] == color:
                    x0 = col * self.SQUARE_SIZE
                    y0 = row * self.SQUARE_SIZE
                    x1 = x0 + self.SQUARE_SIZE
                    y1 = y0 + self.SQUARE_SIZE
                    highlight = self.canvas.create_rectangle(
                        x0, y0, x1, y1, outline=self.CHECK_COLOR, width=3
                    )
                    self.highlighted_squares.append(highlight)
                    return
    
    def is_in_check(self, color):
        """Check if the given color's king is in check."""
        return self.would_be_in_check(color, self.board)
    
    def is_checkmate(self, color):
        """Check if the given color is in checkmate."""
        # If not in check, can't be checkmate
        if not self.is_in_check(color):
            return False
        
        # Check if any piece has legal moves
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece["color"] == color:
                    legal_moves = self.get_legal_moves(row, col)
                    if legal_moves:
                        return False
        
        # No legal moves and king is in check = checkmate
        return True
    
    def is_stalemate(self, color):
        """Check if the given color is in stalemate (not in check but no legal moves)."""
        # If in check, can't be stalemate
        if self.is_in_check(color):
            return False
        
        # Check if any piece has legal moves
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece["color"] == color:
                    legal_moves = self.get_legal_moves(row, col)
                    if legal_moves:
                        return False
        
        # No legal moves and king is not in check = stalemate
        return True
    
    def reset_game(self):
        """Reset the game to initial state."""
        self.board = self.initialize_board()
        self.turn = "white"
        self.selected_piece = None
        self.check_status = {"white": False, "black": False}
        self.clear_highlights()
        self.draw_board()
        self.draw_pieces()
        self.status_label.config(text=f"Current turn: {self.turn.capitalize()}")
        
        # Clear move history
        self.history_text.delete("1.0", tk.END)
        self.move_history = []

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()
