# Insufficient material stalemate detection is invalid (opposite square bishops opposed is not a draw)
# Castling is glitched
# Minimax thinks stalemate is a win for the computer

import sys, random, time, copy, pickle

# Piece definitions

EMPTY = "ee"

W_PAWN = "wp"
W_BISHOP = "wb"
W_KNIGHT = "wn"
W_ROOK = "wr"
W_QUEEN = "wq"
W_KING = "wk"

B_PAWN = "bp"
B_BISHOP = "bb"
B_KNIGHT = "bn"
B_ROOK = "br"
B_QUEEN = "bq"
B_KING = "bk"

WHITE_WIN = "white_win"
BLACK_WIN = "black_win"
STALEMATE = "stalemate"

knight_squares = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
king_squares = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
promotion_pieces = {0: "q", 1: "r", 2: "n", 3: "b"}

class Board:
    # Example FEN: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
    # White pieces get uppercase letters, black gets lowercase.
    # Ranks 8 through 1, files a through h

    def __init__(this): # Create an empty board object.
        
        this.grid = {} # Fill board with pieces in standard position.
        for x in range(8):
            this.grid[x] = {}
            for y in range(8):
                if y == 0:
                    if x == 0 or x == 7:
                        this.grid[x][y] = W_ROOK
                    elif x == 1 or x == 6:
                        this.grid[x][y] = W_KNIGHT
                    elif x == 2 or x == 5:
                        this.grid[x][y] = W_BISHOP
                    elif x == 3:
                        this.grid[x][y] = W_QUEEN
                    else:
                        this.grid[x][y] = W_KING
                elif y == 1:
                    this.grid[x][y] = W_PAWN
                elif y == 6:
                    this.grid[x][y] = B_PAWN
                elif y == 7:
                    if x == 0 or x == 7:
                        this.grid[x][y] = B_ROOK
                    elif x == 1 or x == 6:
                        this.grid[x][y] = B_KNIGHT
                    elif x == 2 or x == 5:
                        this.grid[x][y] = B_BISHOP
                    elif x == 3:
                        this.grid[x][y] = B_QUEEN
                    else:
                        this.grid[x][y] = B_KING
                else:
                    this.grid[x][y] = EMPTY

        # Turn (begin with white)
        this.turn = 0
        
        # Castling availability
        this.wk_castle = True
        this.wq_castle = True
        this.bk_castle = True
        this.bq_castle = True

        this.wk_castled = False
        this.wq_castled = False
        this.bk_castled = False
        this.bq_castled = False

        # En Passant file
        this.passant_file = -1

        # Move clock
        this.half_moves = 0
        this.full_moves = 1

        # Used to check for threefold repetition
        this.previous_boards = []

        # King coordinates - used only to optimize move listing process.
        this.wk_location = (4, 0)
        this.bk_location = (4, 7)

        # Piece score - changes every time a piece is captured.
        this.piece_score = 0

        # A quick way to reference the remaining pieces on the board.
        this.remaining_pieces = {
            W_PAWN: 8,
            W_BISHOP: 2,
            W_KNIGHT: 2,
            W_ROOK: 2,
            W_QUEEN: 1,
            B_PAWN: 8,
            B_BISHOP: 2,
            B_KNIGHT: 2,
            B_ROOK: 2,
            B_QUEEN: 1}

    def print(this):
        for y in range(7, -1, -1): # Reverse order (prints top first)
            line = ""
            for x in range(8):
                if this.grid[x][y][0] == "w":
                    line += this.grid[x][y][1].upper()
                elif this.grid[x][y][0] == "b":
                    line += this.grid[x][y][1]
                else:
                    line += "."
                if x < 7:
                    line += " "
            print(line)
        print()

    def is_checkmate(this):
        pass

    def game_result(this, possible_moves): # Is this position drawn based on insufficient material, threefold repetition, or 50 move rule? Also find checkmate.

        if len(possible_moves) == 0:
            
            if this.find_check: # Checkmate
                if this.turn == 0:
                    return BLACK_WIN
                return WHITE_WIN

            return STALEMATE # No possible moves but no check is a stalemate.
            

        # Insufficient material
        if (board.remaining_pieces[W_PAWN] == 0 and board.remaining_pieces[B_PAWN] == 0 and # No pawns, queens or rooks remaining
        board.remaining_pieces[W_ROOK] == 0 and board.remaining_pieces[B_ROOK] == 0 and \
        board.remaining_pieces[W_QUEEN] == 0 and board.remaining_pieces[B_QUEEN] == 0) and \
        (board.remaining_pieces[W_BISHOP] == 1 and board.remaining_pieces[W_KNIGHT] == 0 or # White insufficient material
        board.remaining_pieces[W_BISHOP] == 0 and board.remaining_pieces[W_KNIGHT] == 1 or \
        board.remaining_pieces[W_BISHOP] == 0 and board.remaining_pieces[W_KNIGHT] == 0) and \
        (board.remaining_pieces[B_BISHOP] == 1 and board.remaining_pieces[B_KNIGHT] == 0 or # Black insufficient material
        board.remaining_pieces[B_BISHOP] == 0 and board.remaining_pieces[B_KNIGHT] == 1 or \
        board.remaining_pieces[B_BISHOP] == 0 and board.remaining_pieces[B_KNIGHT] == 0):
            
            return STALEMATE

        # 50 move rule
        if board.half_moves >= 100:
            return STALEMATE

        # Threefold repetition (add later)
        
        return False # This is not a terminal node.

    def evaluate(this): # Does not account for checkmate/stalemate

        score = this.piece_score

        # Rewards
        move_num_score = 0.04 # Score per available move
        castle_kingside = 0.20
        castle_queenside = 0.10

        piece_advancement_score = {'p': [0, 0, 0.01, 0.03, 0.05, 0.1, 0.3, 0],
                                   'b': [0, 0.05, 0.05, 0.05, 0.1, 0.3, 0.4, 0.4],
                                   'n': [0, 0.05, 0.05, 0.05, 0.1, 0.3, 0.4, 0.4],
                                   'r': [0, 0.03, 0.03, 0.05, 0.1, 0.3, 0.4, 0.4],
                                   'q': [0, 0.03, 0.03, 0.1, 0.3, 0.5, 0.8, 0.8],
                                   'k': [0.1, 0, 0, 0, 0, 0, 0, 0]
                                   }

        # Penalties
        stacked_pawn_penalty = 0.05 # Should probably be removed later

        # Apply rewards and penalties
        
        for x in range(8):
            for y in range(8):
                if this.grid[x][y][0] == "w":
                    score += piece_advancement_score[this.grid[x][y][1]][y]
                elif this.grid[x][y][0] == "b":
                    score -= piece_advancement_score[this.grid[x][y][1]][7 - y]

            if y != 7: # Stacked pawns
                if this.grid[x][y] == "wp" and this.grid[x][y + 1] == "wp":
                    score -= stacked_pawn_penalty
                elif this.grid[x][y] == "bp" and this.grid[x][y + 1] == "bp":
                    score += stacked_pawn_penalty

        # Castling rewards
        if this.wk_castled:
            score += castle_kingside
        elif this.wq_castled:
            score += castle_queenside
        if this.bk_castled:
            score -= castle_kingside
        elif this.bq_castled:
            score -= castle_queenside
        
        return score

    def name_move(this, move): # If called before the move is applied, will name the move.

        try:
            if move[4] == "c": # Castling
                #print("CASTLING!")
                if move[2] == 6:
                    return "O-O" # Kingside
                else:
                    return "O-O-O" # Queenside
        except: pass
        
        move_string = ""
        file_numbers = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}

        # Identify the type of piece moving
        if this.grid[move[0]][move[1]][1] != "p":
            move_string += this.grid[move[0]][move[1]][1].upper()

        # Add file and rank identification if necessary
        if len(move) == 4:
            all_moves = this.list_moves()
            ambiguous = False # Can two of the same piece go to the same spot?
            same_x = False # Determine if files/ranks are ambiguous.
            same_y = False
            for dup_move in all_moves: # File indication
                if this.grid[dup_move[0]][dup_move[1]] == this.grid[move[0]][move[1]] and dup_move[2] == move[2] and dup_move[3] == move[3] and \
                dup_move != move:
                    ambiguous = True
                    if move[0] == dup_move[0]:
                        same_x = True
                    if move[1] == dup_move[1]:
                        same_y = True
                    if same_x and same_y:
                        break
                    
            # Based on ambiguity, determine if file/rank needs to be indicated.
            if ambiguous:
                if same_y or not (same_x or same_y):
                    move_string += file_numbers[move[0]] # Indicate file
                if same_x:
                    move_string += str(move[1] + 1) # Indicate rank

        # If this is a capture, identify it here.
        try:
            if move[4] == "p":
                move_string += file_numbers[move[0]] # Indicate pawn starting file for en passant
                move_string += "x" # En passant capture
        except: pass
        
        if this.grid[move[2]][move[3]] != EMPTY: # All other captures
            if move_string == "":
                move_string += file_numbers[move[0]] # Indicate pawn starting file for pawn capture
            move_string += "x"

        # Add destination coordinate
        move_string += file_numbers[move[2]]
        move_string += str(move[3] + 1)

        # Promotion
        try:
            move_string += "=" + promotion_pieces[move[4]].upper()
        except: pass

        # Test for check and checkmate
        new_board = pickle.loads(pickle.dumps(this))
        #new_board = copy.deepcopy(this)
        new_board.apply_move(move)

        if new_board.find_check():
            if len(new_board.list_moves()) == 0:
                move_string += "#" # Checkmate
            else:
                move_string += "+" # Check

        return move_string

    def find_check(this): # Determine if we are in check or not.
        if this.turn == 0:
            king_location = this.wk_location
        else:
            king_location = this.bk_location

        for direction in range(8, -1, -1):
            if this.find_threats(king_location[0], king_location[1], direction) != EMPTY:
                print(this.find_threats(king_location[0], king_location[1], direction))
                return True
        return False

    def apply_move(this, move): # Update the grid and object data for a move.

        # Flip turn
        if this.turn == 0:
            this.turn = 1
        else:
            this.turn = 0
            this.full_moves += 1

        # Half move counter - increments if there was no capture or pawn movement
        if not (this.grid[move[0]][move[1]][1] == "p" or this.grid[move[2]][move[3]] != EMPTY):
            this.half_moves += 1
        else:
            this.half_moves = 0

        # Update king coordinate
        if this.grid[move[0]][move[1]] == "wk":
            this.wk_location = (move[2], move[3],)
        elif this.grid[move[0]][move[1]] == "bk":
            this.bk_location = (move[2], move[3],)

        # Update piece score
        if this.grid[move[2]][move[3]] != EMPTY:
            if this.grid[move[2]][move[3]] == "wk":
                this.print()
            this.remaining_pieces[this.grid[move[2]][move[3]]] -= 1
            
            score = {"p": 1, "b": 3, "n": 3, "r": 5, "q": 9}[this.grid[move[2]][move[3]][1]]
            if this.grid[move[2]][move[3]][0] == "w":
                this.piece_score -= score
            else:
                this.piece_score += score

        # Moving a pawn two squares forward validates en passant capture.
        if this.grid[move[0]][move[1]] == "wp" and move[1] == 1 and move[3] == 3:
            this.passant_file = move[0]
        elif this.grid[move[0]][move[1]] == "bp" and move[1] == 6 and move[3] == 4:
            this.passant_file = move[0]
        else:
            this.passant_file = -1
        
        # Move the piece from one location to another.
        this.grid[move[2]][move[3]] = this.grid[move[0]][move[1]]
        this.grid[move[0]][move[1]] = EMPTY

        if move[1] == 0: # Remove castling availability upon piece movement
            if move[0] == 4 or move[2] == 4:
                this.wk_castle = False
                this.wq_castle = False
            if move[0] == 0 or move[2] == 0:
                this.wq_castle = False
            if move[0] == 7 or move[2] == 7:
                this.wk_castle = False
        if move[1] == 7:
            if move[0] == 4 or move[2] == 4:
                this.bk_castle = False
                this.bq_castle = False
            if move[0] == 0 or move[2] == 0:
                this.bq_castle = False
            if move[0] == 7 or move[2] == 7:
                this.bk_castle = False
        
        if len(move) == 5: # Handles pawn promotion, en passant and castling board updates
            if move[4] == "c": # Castling
                if move == (4, 0, 6, 0, "c"): # White Kingside
                    this.grid[5][0] = this.grid[7][0]
                    this.grid[7][0] = EMPTY
                    this.wk_castled = True
                if move == (4, 0, 2, 0, "c"): # White Queenside
                    this.grid[3][0] = this.grid[0][0]
                    this.grid[0][0] = EMPTY
                    this.wq_castled = True
                if move == (4, 7, 6, 7, "c"): # Black Kingside
                    this.grid[5][7] = this.grid[7][7]
                    this.grid[7][7] = EMPTY
                    this.bk_castled = True
                if move == (4, 7, 2, 7, "c"): # Black Queenside
                    this.grid[3][7] = this.grid[0][7]
                    this.grid[0][7] = EMPTY
                    this.bq_castled = True
            elif move[4] == "p": # En passant
                this.remaining_pieces[this.grid[move[2]][move[1]]] -= 1
                this.grid[move[2]][move[1]] = EMPTY
            else:
                this.remaining_pieces[this.grid[move[2]][move[3]]] -= 1 # Remove the pawn from the list of pieces
                this.remaining_pieces[this.grid[move[2]][move[3]][0] + promotion_pieces[move[4]]] += 1 # Account for the addition of the promoted piece
                this.grid[move[2]][move[3]] = this.grid[move[2]][move[3]][0] + promotion_pieces[move[4]] # Update board

    def find_threats(this, x, y, direction): # Only return a piece if it is the opposite color of our king
        coordinate = this.check_line(x, y, direction)
        if coordinate == EMPTY:
            return EMPTY
        if (this.grid[coordinate[0]][coordinate[1]][0] == "b" and this.turn == 0) or (this.grid[coordinate[0]][coordinate[1]][0] == "w" and this.turn == 1):
            return coordinate
        else:
            return EMPTY

    def check_line(this, x, y, direction): # Returns the closest piece to a coordinate.
        i = 1
        if direction == 0: # North
            while y + i <= 7:
                if this.grid[x][y + i] != EMPTY:
                    if this.grid[x][y + i][1] == "r" or this.grid[x][y + i][1] == "q":
                        return (x, y + i)
                    break
                i += 1
        elif direction == 1: # Northeast
            while x + i <= 7 and y + i <= 7:
                if this.grid[x + i][y + i] != EMPTY:
                    if this.grid[x + i][y + i][1] == "b" or this.grid[x + i][y + i][1] == "q":
                        return (x + i, y + i)
                    break
                i += 1
        elif direction == 2: # East
            while x + i <= 7:
                if this.grid[x + i][y] != EMPTY:
                    if this.grid[x + i][y][1] == "r" or this.grid[x + i][y][1] == "q":
                        return (x + i, y)
                    break
                i += 1
        elif direction == 3: # Southeast
            while x + i <= 7 and y - i >= 0:
                if this.grid[x + i][y - i] != EMPTY:
                    if this.grid[x + i][y - i][1] == "b" or this.grid[x + i][y - i][1] == "q":
                        return (x + i, y - i)
                    break
                i += 1
        elif direction == 4: # South
            while y - i >= 0:
                if this.grid[x][y - i] != EMPTY:
                    if this.grid[x][y - i][1] == "r" or this.grid[x][y - i][1] == "q":
                        return (x, y - i)
                    break
                i += 1
        elif direction == 5: # Southwest
            while x - i >= 0 and y - i >= 0:
                if this.grid[x - i][y - i] != EMPTY:
                    if this.grid[x - i][y - i][1] == "b" or this.grid[x - i][y - i][1] == "q":
                        return (x - i, y - i)
                    break
                i += 1
        elif direction == 6: # West
            while x - i >= 0:
                if this.grid[x - i][y] != EMPTY:
                    if this.grid[x - i][y][1] == "r" or this.grid[x - i][y][1] == "q":
                        return (x - i, y)
                    break
                i += 1
        elif direction == 7: # Northwest
            while x - i >= 0 and y + i <= 7:
                if this.grid[x - i][y + i] != EMPTY:
                    if this.grid[x - i][y + i][1] == "b" or this.grid[x - i][y + i][1] == "q":
                        return (x - i, y + i)
                    break
                i += 1
        elif direction == 8: # Knights, Kings, Pawns
            for offset in knight_squares:
                try:
                    if this.grid[x + offset[0]][y + offset[1]][1] == "n": # If this knight is ours, skip it and look for other threats.
                        color = this.grid[x + offset[0]][y + offset[1]][0]
                        if color == "b" and this.turn == 0 or color == "w" and this.turn == 1:
                            return (x + offset[0], y + offset[1])
                except: pass
            for offset in king_squares:
                try:
                    if this.grid[x + offset[0]][y + offset[1]][1] == "k": # If this king is ours, skip it and look for other threats.
                        color = this.grid[x + offset[0]][y + offset[1]][0]
                        if color == "b" and this.turn == 0 or color == "w" and this.turn == 1:
                            return (x + offset[0], y + offset[1])
                except: pass
            if this.turn == 0: # Check for black pawn threats
                try:
                    if this.grid[x - 1][y + 1] == "bp":
                        return (x - 1, y + 1)
                except: pass
                try:
                    if this.grid[x + 1][y + 1] == "bp":
                        return (x + 1, y + 1)
                except: pass
            else: # Check for white pawn threats
                try:
                    if this.grid[x - 1][y - 1] == "wp":
                        return (x - 1, y - 1)
                except: pass
                try:
                    if this.grid[x + 1][y - 1] == "wp":
                        return (x + 1, y - 1)
                except: pass
                
        return EMPTY

    def list_moves(this, xray_moves=False): # X-ray moves evaluates possible future moves for the evaluation function.

        # Determine where our king is for quick reference.
        if this.turn == 0:
            king_location = this.wk_location
        else:
            king_location = this.bk_location

        # Count the number of checks we are in
        checks = 0
        threat = EMPTY
        for direction in range(8, -1, -1):
            potential_threat = this.find_threats(king_location[0], king_location[1], direction)
            if potential_threat != EMPTY:
                threat = potential_threat
                checks += 1
                if checks > 1:
                    break

        moves = [] # A list of four-integer tuples, where promotions, en passant and castling have five.
        approved_moves = [] # Moves which don't expose ourselves to check
        
        # If double check, skip to king moves.
        if checks < 2:
            for x in range(8):
                for y in range(8):
                    if this.grid[x][y][0] == "w" and this.turn == 0 or this.grid[x][y][0] == "b" and this.turn == 1:
                        if this.grid[x][y] == "wp": # White pawns
                            if this.grid[x][y + 1] == EMPTY:
                                if y == 6:
                                    moves.append((x, y, x, y + 1, 0)) # Pawn promotions
                                    moves.append((x, y, x, y + 1, 1))
                                    moves.append((x, y, x, y + 1, 2))
                                    moves.append((x, y, x, y + 1, 3))
                                else:
                                    moves.append((x, y, x, y + 1)) # Forward 1
                                if y == 1:
                                    if this.grid[x][3] == EMPTY:
                                        moves.append((x, y, x, 3)) # Forward 2
                            try:
                                if this.grid[x - 1][y + 1][0] == "b": # Capture
                                    if y == 6:
                                        moves.append((x, y, x - 1, y + 1, 0)) # Capture promotions
                                        moves.append((x, y, x - 1, y + 1, 1))
                                        moves.append((x, y, x - 1, y + 1, 2))
                                        moves.append((x, y, x - 1, y + 1, 3))
                                    else:
                                        moves.append((x, y, x - 1, y + 1)) # Capture
                            except: pass
                            try:
                                if this.grid[x + 1][y + 1][0] == "b":
                                    if y == 6:
                                        moves.append((x, y, x + 1, y + 1, 0)) # Capture promotions
                                        moves.append((x, y, x + 1, y + 1, 1))
                                        moves.append((x, y, x + 1, y + 1, 2))
                                        moves.append((x, y, x + 1, y + 1, 3))
                                    else:
                                        moves.append((x, y, x + 1, y + 1)) # Capture
                            except: pass
                            if y == 4:
                                if x > 0 and x - 1 == this.passant_file: # En passant moves
                                    moves.append((x, y, x - 1, y + 1, "p"))
                                if x < 7 and x + 1 == this.passant_file:
                                    moves.append((x, y, x + 1, y + 1, "p"))
                                    
                        elif this.grid[x][y] == "bp": # Black pawns
                            if this.grid[x][y - 1] == EMPTY:
                                if y == 1:
                                    moves.append((x, y, x, y - 1, 0)) # Pawn promotions
                                    moves.append((x, y, x, y - 1, 1))
                                    moves.append((x, y, x, y - 1, 2))
                                    moves.append((x, y, x, y - 1, 3))
                                else:
                                    moves.append((x, y, x, y - 1)) # Forward 1
                                if y == 6:
                                    if this.grid[x][4] == EMPTY:
                                        moves.append((x, y, x, 4)) # Forward 2
                            try:
                                if this.grid[x - 1][y - 1][0] == "w": # Capture
                                    if y == 1:
                                        moves.append((x, y, x - 1, y - 1, 0)) # Capture promotions
                                        moves.append((x, y, x - 1, y - 1, 1))
                                        moves.append((x, y, x - 1, y - 1, 2))
                                        moves.append((x, y, x - 1, y - 1, 3))
                                    else:
                                        moves.append((x, y, x - 1, y - 1)) # Capture
                            except: pass
                            try:
                                if this.grid[x + 1][y - 1][0] == "w":
                                    if y == 1:
                                        moves.append((x, y, x + 1, y - 1, 0)) # Capture promotions
                                        moves.append((x, y, x + 1, y - 1, 1))
                                        moves.append((x, y, x + 1, y - 1, 2))
                                        moves.append((x, y, x + 1, y - 1, 3))
                                    else:
                                        moves.append((x, y, x + 1, y - 1)) # Capture
                            except: pass
                            if y == 3:
                                if x > 0 and x - 1 == this.passant_file: # En passant moves
                                    moves.append((x, y, x - 1, y - 1, "p"))
                                if x < 7 and x + 1 == this.passant_file:
                                    moves.append((x, y, x + 1, y - 1, "p"))

                        elif this.grid[x][y][1] == "n": # Knights
                            for offset in knight_squares:
                                if 0 <= x + offset[0] <= 7 and 0 <= y + offset[1] <= 7:
                                    if this.grid[x + offset[0]][y + offset[1]][0] != this.grid[king_location[0]][king_location[1]][0]:
                                        moves.append((x, y, x + offset[0], y + offset[1]))

                        elif this.grid[x][y][1] == "r" or this.grid[x][y][1] == "q": # Rooks and queens
                            i = 1
                            while True: # North
                                if y + i > 7:
                                    break
                                if this.grid[x][y + i] == EMPTY:
                                    moves.append((x, y, x, y + i))
                                else:
                                    if this.grid[x][y + i][0] == "b" and this.turn == 0 or this.grid[x][y + i][0] == "w" and this.turn == 1:
                                        moves.append((x, y, x, y + i))
                                    break
                                i += 1
                            i = 1
                            while True: # East
                                if x + i > 7:
                                    break
                                if this.grid[x + i][y] == EMPTY:
                                    moves.append((x, y, x + i, y))
                                else:
                                    if this.grid[x + i][y][0] == "b" and this.turn == 0 or this.grid[x + i][y][0] == "w" and this.turn == 1:
                                        moves.append((x, y, x + i, y))
                                    break
                                i += 1
                            i = 1
                            while True: # South
                                if y - i < 0:
                                    break
                                if this.grid[x][y - i] == EMPTY:
                                    moves.append((x, y, x, y - i))
                                else:
                                    if this.grid[x][y - i][0] == "b" and this.turn == 0 or this.grid[x][y - i][0] == "w" and this.turn == 1:
                                        moves.append((x, y, x, y - i))
                                    break
                                i += 1
                            i = 1
                            while True: # West
                                if x - i < 0:
                                    break
                                if this.grid[x - i][y] == EMPTY:
                                    moves.append((x, y, x - i, y))
                                else:
                                    if this.grid[x - i][y][0] == "b" and this.turn == 0 or this.grid[x - i][y][0] == "w" and this.turn == 1:
                                        moves.append((x, y, x - i, y))
                                    break
                                i += 1

                        if this.grid[x][y][1] == "b" or this.grid[x][y][1] == "q": # Bishops and queens
                            i = 1
                            while True: # Northeast
                                if x + i > 7 or y + i > 7:
                                    break
                                if this.grid[x + i][y + i] == EMPTY:
                                    moves.append((x, y, x + i, y + i))
                                else:
                                    if this.grid[x + i][y + i][0] == "b" and this.turn == 0 or this.grid[x + i][y + i][0] == "w" and this.turn == 1:
                                        moves.append((x, y, x + i, y + i))
                                    break
                                i += 1
                            i = 1
                            while True: # Southeast
                                if x + i > 7 or y - i < 0:
                                    break
                                if this.grid[x + i][y - i] == EMPTY:
                                    moves.append((x, y, x + i, y - i))
                                else:
                                    if this.grid[x + i][y - i][0] == "b" and this.turn == 0 or this.grid[x + i][y - i][0] == "w" and this.turn == 1:
                                        moves.append((x, y, x + i, y - i))
                                    break
                                i += 1
                            i = 1
                            while True: # Southwest
                                if x - i < 0 or y - i < 0:
                                    break
                                if this.grid[x - i][y - i] == EMPTY:
                                    moves.append((x, y, x - i, y - i))
                                else:
                                    if this.grid[x - i][y - i][0] == "b" and this.turn == 0 or this.grid[x - i][y - i][0] == "w" and this.turn == 1:
                                        moves.append((x, y, x - i, y - i))
                                    break
                                i += 1
                            i = 1
                            while True: # Northwest
                                if x - i < 0 or y + i > 7:
                                    break
                                if this.grid[x - i][y + i] == EMPTY:
                                    moves.append((x, y, x - i, y + i))
                                else:
                                    if this.grid[x - i][y + i][0] == "b" and this.turn == 0 or this.grid[x - i][y + i][0] == "w" and this.turn == 1:
                                        moves.append((x, y, x - i, y + i))
                                    break
                                i += 1      
            
            for move in moves: # Ensure moves don't leave us exposed to check.

                # If the move is en passant, perform a different check.
                en_passant = False
                if len(move) == 5:
                    if move[4] == "p":
                        en_passant = True

                if en_passant:
                    captured_piece = this.grid[move[2]][move[1]]
                    this.grid[move[2]][move[3]] = this.grid[move[0]][move[1]] # Modify the board to simulate en passant
                    this.grid[move[0]][move[1]] = EMPTY
                    this.grid[move[2]][move[1]] = EMPTY

                    # If king is safe, approve the en passant.
                    approved_move = True
                    for direction in king_location:
                        if this.find_threats(king_location[0], king_location[1], direction) != EMPTY:
                            approved_move = False
                            break
                    if approved_move:
                        approved_moves.append(move)

                    # Restore the board.
                    this.grid[move[2]][move[1]] = captured_piece
                    this.grid[move[0]][move[1]] = this.grid[move[2]][move[3]]
                    this.grid[move[2]][move[3]] = EMPTY

                else:
                    # Prevent us from moving pinned pieces, exposing ourselves to check.
                    new_threat = EMPTY
                    pinned_piece = this.grid[move[0]][move[1]] # Remove the piece from the board to see if it blocks an attack
                    this.grid[move[0]][move[1]] = EMPTY
                        
                    if king_location[0] == move[0] and move[2] != move[0]: # Moved out of vertical line
                        if move[1] > king_location[1]: # North
                            new_threat = this.find_threats(king_location[0], king_location[1], 0)
                        else: # South
                            new_threat = this.find_threats(king_location[0], king_location[1], 4)
                    
                    elif king_location[1] == move[1] and move[1] != move[3]: # Moved out of horizontal line
                        if move[0] > king_location[0]: # East
                            new_threat = this.find_threats(king_location[0], king_location[1], 2)
                        else: # West
                            new_threat = this.find_threats(king_location[0], king_location[1], 6)
                    
                    elif king_location[0] + king_location[1] == move[0] + move[1] and move[0] + move[1] != move[2] + move[3]: # Southeast diagonal
                        if move[0] > king_location[0]: # Southeast
                            new_threat = this.find_threats(king_location[0], king_location[1], 3)
                        else: # Northwest
                            new_threat = this.find_threats(king_location[0], king_location[1], 7)
                    
                    elif king_location[0] - king_location[1] == move[0] - move[1] and move[0] - move[1] != move[2] - move[3]: # Northeast diagonal
                        if move[0] > king_location[0]: # Northeast
                            new_threat = this.find_threats(king_location[0], king_location[1], 1)
                        else: # Southwest
                            new_threat = this.find_threats(king_location[0], king_location[1], 5)

                    this.grid[move[0]][move[1]] = pinned_piece # Restore the piece to the board.

                    # Either capture or block check threats.
                    if new_threat == EMPTY:
                        if checks == 1:
                            
                            if move[2] == threat[0] and move[3] == threat[1]:
                                approved_moves.append(move) # Approve moves which capture offending piece (takes care of pawns and knights)

                            elif this.grid[threat[0]][threat[1]][1] == "r" or this.grid[threat[0]][threat[1]][1] == "q": # Rooks and queens can be blocked.
                                if threat[0] == move[2] and king_location[0] == threat[0]: # In line vertically
                                    if king_location[1] < move[3] < threat[1] or threat[1] < move[3] < king_location[1]:
                                        approved_moves.append(move)
                                elif threat[1] == move[3] and king_location[1] == threat[1]: # In line horizontally
                                    if king_location[0] < move[2] < threat[0] or threat[0] < move[2] < king_location[0]:
                                        approved_moves.append(move)

                            if this.grid[threat[0]][threat[1]][1] == "b" or this.grid[threat[0]][threat[1]][1] == "q": # Bishops and queens can be blocked.
                                if threat[0] + threat[1] == move[2] + move[3] and king_location[0] + king_location[1] == move[2] + move[3]: # Southeast diagonal
                                    if king_location[0] < move[2] < threat[0] or threat[0] < move[2] < king_location[0]:
                                        approved_moves.append(move)
                                elif threat[0] - threat[1] == move[2] - move[3] and king_location[0] - king_location[1] == move[2] - move[3]: # Northeast diagonal
                                    if king_location[0] < move[2] < threat[0] or threat[0] < move[2] < king_location[0]:
                                        approved_moves.append(move)
                        else:
                            approved_moves.append(move)

            # Castling
            if checks == 0:
                if this.wk_castle and this.turn == 0:
                    if this.grid[5][0] == EMPTY and this.grid[6][0] == EMPTY:
                        if this.find_threats(6, 0, 2) == EMPTY and this.find_threats(6, 0, 1) == EMPTY and this.find_threats(6, 0, 0) == EMPTY and \
                           this.find_threats(6, 0, 7) == EMPTY and this.find_threats(5, 0, 1) == EMPTY and this.find_threats(5, 0, 0) == EMPTY and \
                           this.find_threats(5, 0, 7) == EMPTY and this.find_threats(6, 0, 8) == EMPTY and this.find_threats(5, 0, 8) == EMPTY:
                            approved_moves.append((4, 0, 6, 0, "c"))

                if this.wq_castle and this.turn == 0:
                    if this.grid[1][0] == EMPTY and this.grid[2][0] == EMPTY and this.grid[3][0] == EMPTY:
                        if this.find_threats(1, 0, 6) == EMPTY and this.find_threats(1, 0, 7) == EMPTY and this.find_threats(1, 0, 0) == EMPTY and \
                           this.find_threats(1, 0, 1) == EMPTY and this.find_threats(2, 0, 7) == EMPTY and this.find_threats(2, 0, 0) == EMPTY and \
                           this.find_threats(2, 0, 1) == EMPTY and this.find_threats(3, 0, 7) == EMPTY and this.find_threats(3, 0, 0) == EMPTY and \
                           this.find_threats(3, 0, 1) == EMPTY and this.find_threats(1, 0, 8) == EMPTY and this.find_threats(2, 0, 8) == EMPTY and \
                           this.find_threats(3, 0, 8) == EMPTY:
                            approved_moves.append((4, 0, 2, 0, "c"))

                if this.bk_castle and this.turn == 1:
                    if this.grid[5][7] == EMPTY and this.grid[6][7] == EMPTY:
                        if this.find_threats(6, 7, 2) == EMPTY and this.find_threats(6, 7, 3) == EMPTY and this.find_threats(6, 7, 4) == EMPTY and \
                           this.find_threats(6, 7, 5) == EMPTY and this.find_threats(5, 7, 3) == EMPTY and this.find_threats(5, 7, 4) == EMPTY and \
                           this.find_threats(5, 7, 5) == EMPTY and this.find_threats(6, 7, 8) == EMPTY and this.find_threats(5, 7, 8) == EMPTY:
                            approved_moves.append((4, 7, 6, 7, "c"))

                if this.bq_castle and this.turn == 1:
                    if this.grid[1][7] == EMPTY and this.grid[2][7] == EMPTY and this.grid[3][7] == EMPTY:
                        if this.find_threats(1, 7, 6) == EMPTY and this.find_threats(1, 7, 5) == EMPTY and this.find_threats(1, 7, 4) == EMPTY and \
                           this.find_threats(1, 7, 3) == EMPTY and this.find_threats(2, 7, 5) == EMPTY and this.find_threats(2, 7, 4) == EMPTY and \
                           this.find_threats(2, 7, 3) == EMPTY and this.find_threats(3, 7, 5) == EMPTY and this.find_threats(3, 7, 4) == EMPTY and \
                           this.find_threats(3, 7, 3) == EMPTY and this.find_threats(1, 7, 8) == EMPTY and this.find_threats(2, 7, 8) == EMPTY and \
                           this.find_threats(3, 7, 8) == EMPTY:
                            approved_moves.append((4, 7, 2, 7, "c"))

        # For each king move, check to see if square is threatened.
        king = this.grid[king_location[0]][king_location[1]]
        this.grid[king_location[0]][king_location[1]] = EMPTY # Temporarily remove king from the board.
        for king_square in king_squares:
            if 0 <= king_location[0] + king_square[0] <= 7 and 0 <= king_location[1] + king_square[1] <= 7:
                if this.grid[king_location[0] + king_square[0]][king_location[1] + king_square[1]][0] != king[0]:
                    move_approved = True
                    for direction in range(8, -1, -1):
                        new_threat = this.find_threats(king_location[0] + king_square[0], king_location[1] + king_square[1], direction)
                        if new_threat != EMPTY:
                            move_approved = False
                            break
                    if move_approved:
                        pass
                        approved_moves.append((king_location[0], king_location[1], king_location[0] + king_square[0], king_location[1] + king_square[1]))

        this.grid[king_location[0]][king_location[1]] = king # Replace the king on the board.

        return approved_moves

class Node:

    def __init__(this, input_board, input_move):

        this.board = input_board
        this.move = input_move # The move that got us to this position.
        this.value = this.board.evaluate()

        this.terminal_node = False
        this.children = None # Becomes a list later if this node is selected for evaluation.

    def find_best_child(this): # Lists most favorable children
        
        if this.board.turn == 0:
            best_value = -1000000
        else:
            best_value = 1000000
        
        best_child = None
        for child in this.children:
            if this.board.turn == 0 and child.value >= best_value:
                best_child = child
                best_value = child.value
            elif this.board.turn == 1 and child.value <= best_value:
                best_child = child
                best_value = child.value

        return best_child

def minimax(node, depth, a, b):

    next_moves = node.board.list_moves() # Create children moves for later

    # Determine if this is a terminal node
    game_result = node.board.game_result(next_moves)
    if game_result:
        if game_result == WHITE_WIN:
            node.value = 1000000 + depth
            return 1000000 + depth
        if game_result == BLACK_WIN:
            node.value = -1000000 - depth
            return -1000000 - depth
        return 0

    if depth == 0:
        return node.value

    node.children = []
    
    if node.board.turn == 0: # Maximize
        value = -1000000
        
        for move in next_moves:
            #new_board = copy.deepcopy(node.board)
            new_board = pickle.loads(pickle.dumps(node.board, -1))
            new_board.apply_move(move)
            
            new_node = Node(new_board, move)
            node.children.append(new_node)
            
            value = max(value, minimax(new_node, depth - 1, a, b))
            a = max(a, value)
            if a >= b:
                break # Beta cutoff

        node.value = value # Backpropagate (Critical for find_best_child)
        return value
    
    else: # Minimize
        value = 1000000
        
        for move in next_moves:
            #new_board = copy.deepcopy(node.board)
            new_board = pickle.loads(pickle.dumps(node.board, -1))
            new_board.apply_move(move)
            
            new_node = Node(new_board, move)
            node.children.append(new_node)
            
            value = min(value, minimax(new_node, depth - 1, a, b))
            b = min(b, value)
            
            if a >= b:
                break # Alpha cutoff

        node.value = value # Backpropagate (Critical for find_best_child)
        return value

DEPTH = 4
player_white = True

board = Board()
board.print()

main_node = Node(board, None)

if not player_white: # Computer starts
    print("Calculating move...")
    minimax(main_node, DEPTH, -1000000, 1000000)
    best_child = main_node.find_best_child()
    print(main_node.board.name_move(best_child.move))
    main_node.board.apply_move(best_child.move)

while True:
    # Player input
    possible_moves = main_node.board.list_moves()
    picked_move = False
    while not picked_move:
        move_name = input("Put in your move: ")
        
        '''for move in possible_moves: # Name all moves
            print(main_node.board.name_move(move) + " " + str(move))'''
        
        for move in possible_moves: # See if input was valid
            if main_node.board.name_move(move) == move_name:
                main_node.board.apply_move(move)
                picked_move = True
                break
            
    # Computer move
    print("Calculating move...")

    # Calculate move here
    minimax(main_node, DEPTH, -1000000, 1000000)
    best_child = main_node.find_best_child()

    # Name the line
    search_node = main_node
    line = ""
    while search_node.children != None and not search_node.terminal_node:

        child = search_node.find_best_child()
        
        line += search_node.board.name_move(child.move)
        line += " "

        search_node = child
    print(line)

    '''for child in main_node.children:
        print(main_node.board.name_move(child.move))
        print(round(child.value * 100) / 100)'''

    # Print the computer's output.
    #print(main_node.board.name_move(best_child.move))
    best_child.board.print()
    print(round(main_node.value * 100)/100)

    main_node = best_child # Update the node.
