# chess-ai
ai plays against eachother


[4:14 PM, 1/28/2026] White plays: ♖ a1b1
(Searched 840 positions)

     a   b   c   d   e   f   g   h
 8     ♚                    8
 7  ♟  ♟           ♟  ♟  ♟  7
 6                          6
 5              ♙  ♙        5
 4                 ♙        4
 3                          3
 2              ♜        ♙  2
 1     ♖              ♔     1
     a   b   c   d   e   f   g   h
Move 200: Black's turn
Press Enter to see the move...
Black plays: ♜ e2e3
(Searched 1042 positions)

     a   b   c   d   e   f   g   h
 8     ♚                    8
 7  ♟  ♟           ♟  ♟  ♟  7
 6                          6
 5              ♙  ♙        5
 4                 ♙        4
 3              ♜           3
 2                       ♙  2
 1     ♖              ♔     1
     a   b   c   d   e   f   g   h
Draw by move limit (200 moves).

Final position:
     a   b   c   d   e   f   g   h
 8     ♚                    8
 7  ♟  ♟           ♟  ♟  ♟  7
 6                          6
 5              ♙  ♙        5
 4                 ♙        4
 3              ♜           3
 2                       ♙  2
 1     ♖              ♔     1
     a   b   c   d   e   f   g   h
Total moves played: 200
[4:14 PM, 1/28/2026]DRAW LIMIT
[4:21 PM, 1/28/2026] ❯ Can you run a game of chess ai and observe and then make an algo update                      
                                                                                                
⏺ I'll explore the codebase to understand the chess AI structure first.                         
                                                                                                
⏺ Explore(Explore chess AI codebase)                                                            
  ⎿  Done (18 tool uses · 46.7k tokens · 52s)                                                   
                                                                                                
⏺ I found the chess AI. Let me run a game to observe the AI's play style.                …
[4:24 PM, 1/28/2026]: def get_best_move(self, game):                                                   
      582          """Get the best move for the current position."""                            
      583          self.nodes_searched = 0                                                      
      584 +        # Clear killer moves for new search                                          
      585 +        self.killer_moves = [[] for _ in range(20)]                                  
      586 +                                                                                     
      587          _, best_move = self.minimax(                                                 
      588              game,                                                                    
      589              self.depth,                                                              
     ...                                                                                        
      570              float('inf'),                                                            
      571              game.white_to_move                                                       
      572          )                                                                            
      573 +                                                                                     
      574 +        # Update position history after move is selected                             
      575 +        if best_move:                                                                
      576 +            game_copy = copy.deepcopy(game)                                          
      577 +            game_copy.make_move(best_move)                                           
      578 +            board_hash = self.get_board_hash(game_copy)                              
      579 +            self.position_history[board_hash] =                                      
          +self.position_history.get(board_hash, 0) + 1                                         
      580 +                                                                                     
      581          return best_move, self.nodes_searched                                        
      582                                                                                       
      583                                                                                       
                                                                                                
⏺ Now let me run another game to compare the improved AI's performance.                         
                                                                                                
  Bash(python3 -c "                                                                             
      import sys…)                                                                              
  ⎿  Running…                                                                                   
     ctrl+b to run in background                                                                
                                                                                                
✽ Metamorphosing… (esc to interrupt · 6m 21s · ↓ 9.5k tokens · thinking)



Move 20: Black's turn
Press Enter to see the move...
Black plays: ♝ c5f2 captures ♙
(Searched 1093 positions)

     a   b   c   d   e   f   g   h
 8  ♘        ♛     ♚  ♞  ♜  8
 7  ♟  ♟           ♟  ♟  ♟  7
 6                          6
 5                    ♘  ♝  5
 4        ♞        ♗        4
 3                       ♙  3
 2  ♙  ♙  ♙     ♙  ♝  ♙     2
 1  ♖        ♕  ♔  ♗     ♖  1
     a   b   c   d   e   f   g   h
White is in CHECK!
Move 21: White's turn
Press Enter to see the move...
White plays: ♔ e1f2 captures ♝
(Searched 179 positions)

     a   b   c   d   e   f   g   h
 8  ♘        ♛     ♚  ♞  ♜  8
 7  ♟  ♟           ♟  ♟  ♟  7
 6                          6
 5                    ♘  ♝  5
 4        ♞        ♗        4
 3                       ♙  3
 2  ♙  ♙  ♙     ♙  ♔  ♙     2
 1  ♖        ♕     ♗     ♖  1
     a   b   c   d   e   f   g   h
Move 22: Black's turn
Press Enter to see the move...

Always a stalemate???
