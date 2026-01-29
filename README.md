# chess-ai
ai plays against eachother

Developed with Claude Code on Opus 4.5 and iterated with the same!

# Running Parallel Simulations Example

⏺ Now let me launch 50 games in parallel using background processes. Each will have different algorithm
  configurations.

⏺ Bash(mkdir -p chess_results && for i in {1..50}; do
        # Vary configurations across games…)
  ⎿  Launched 50 games in parallel

⏺ Games launched. Let me monitor their progress.

⏺ Bash(echo "Active chess processes: $(pgrep -f chess_game_worker | wc -l)" && ls chess_results/ 2>/dev/null | wc
      -l && echo "files created")
  ⎿  Active chess processes:       50
     50
     files created

⏺ All 50 games are running. Let me wait for them to complete and then analyze results.

⏺ Bash(while [ $(pgrep -f chess_game_worker | wc -l) -gt 0 ]; do timeout: 10m 0s
        active=$(pgrep -f chess_game_worker | wc -l)…)
  ⎿  Running in the background (↓ to manage)

⏺ Let me check on the progress.

⏺ Read 1 file (ctrl+o to expand)

⏺ Let me check what's actually in the output files.

⏺ Bash(head -c 500 chess_results/game_1.json && echo "---" && ls -la chess_results/ | head -10)
  ⎿  ---
     total 0
     drwxr-xr-x@ 52 <>< >  staff  1664 Jan 29 10:41 .
     … +8 lines (ctrl+o to expand)

⏺ The files are empty because results are only written on completion. With 50 games running depth 3-4 minimax,
  this is CPU-intensive. Let me check if we should reduce parallelism for better throughput.

⏺ Bash(sysctl -n hw.ncpu)
  ⎿  10

⏺ 50 games on 10 cores means they're competing for CPU. Let me check progress on the monitoring task.

⏺ Bash(tail -5 /private/tmp/claude/-Users-<>< >-code/tasks/beb4051.output && echo "---" && ls -la
      chess_results/*.json | awk '$5 > 0 {print}' | head -10)
  ⎿  10:48:16 - Active:       50, Completed:        0/50
     10:48:26 - Active:       50, Completed:        0/50
     10:48:36 - Active:       50, Completed:        0/50
     … +3 lines (ctrl+o to expand)

⏺ Let me check the actual processes to ensure they're progressing.

⏺ Bash(ps aux | grep chess_game_worker | head -5)
  ⎿ <>< >       27016  18.0  0.1 435277104  23936   ??  RN   10:41AM   1:22.61 /Library/Developer/Comman
    dLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python c
    hess_game_worker.py --game-id 47 --white-depth 4 --black-depth 2 --white-center 85 --black-center 95 --wh
    … +17 lines (ctrl+o to expand)

All 50 processes are actively running and using CPU. Let me continue monitoring until games start completing.

⏺ Bash(while true; do                                                                                timeout: 10m
        completed_count=$(ls -la chess_results/*.json 2>/dev/null | awk '$5 > 0 {count++} END        0s
      {print count+0}')…)
  ⎿  10:50:20 - Active: 51, Completed: 0/50
     10:50:35 - Active: 51, Completed: 0/50
     10:50:50 - Active: 51, Completed: 0/50
     10:51:05 - Active: 51, Completed: 0/50
     10:51:20 - Active: 51, Completed: 0/50
     +4 more lines (2m 14s)
     ctrl+b to run in background


 Read 1 file (ctrl+o to expand)

⏺ The games are still running (51 includes the monitor). With depth 3-4 minimax, 100 moves each, and 50 games on
  10 cores, this takes significant time. Let me check how long the games have been running.

⏺ Bash(ps -o pid,etime,pcpu -p $(pgrep -f chess_game_worker | head -5 | tr '\n' ',')0 2>/dev/null | head -10)
  ⎿    PID ELAPSED  %CPU
     26970   11:32  18.0
     26971   11:32  16.2
     … +3 lines (ctrl+o to expand)

⏺ Games running for ~12 minutes at 16-18% CPU each. Let me continue monitoring.

# Single Threaded Game Example

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
