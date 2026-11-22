import os
import re
import sys
import chess
import chess.svg

REPO = "riguidix/riguidix"
STATE_FILE = "chess_state.fen"
SVG_FILE = "chess-board.svg"
README_FILE = "README.md"

def load_board():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            fen = f.read().strip()
            if fen:
                return chess.Board(fen)
    return chess.Board()

def save_board(board):
    with open(STATE_FILE, "w") as f:
        f.write(board.fen())

def generate_svg(board, last_move=None):
    crt_colors = {
        "square light": "#a3d9a5",          # Verde menta claro (contrasta con blancas y negras)
        "square dark": "#2d6a3e",           # Verde bosque medio (las piezas negras resaltan)
        "margin": "#080c08",                # Fondo del monitor CRT
        "coord": "#33ff33",                 # Coordenadas verde fósforo
        "square light lastmove": "#c2f0c2", # Resaltado de última jugada (clara)
        "square dark lastmove": "#3e8e52",  # Resaltado de última jugada (oscura)
    }
    svg_code = chess.svg.board(
        board=board,
        lastmove=last_move,
        size=420,
        colors=crt_colors
    )
    with open(SVG_FILE, "w") as f:
        f.write(svg_code)

def build_markdown(board):
    turn = "White (Blancas)" if board.turn == chess.WHITE else "Black (Negras)"
    
    if board.is_game_over():
        status = f"GAME OVER :: {board.result()}"
        new_game_url = f"https://github.com/{REPO}/issues/new?title=chess%7Cnew&body=Just+click+Submit+to+start+a+new+game!"
        moves_md = f"<h3><a href='{new_game_url}'>[ > START NEW GAME ]</a></h3>"
    else:
        status = f"TURN :: {turn} | CLICK A MOVE TO PLAY"
        # Agrupa jugadas legales por casilla de origen (ej. e2 -> e3, e4)
        moves_by_from = {}
        for move in board.legal_moves:
            uci = move.uci()
            src, dst = uci[:2], uci[2:]
            moves_by_from.setdefault(src, []).append((dst, uci))

        rows = []
        for src in sorted(moves_by_from.keys()):
            links = []
            for dst, uci in sorted(moves_by_from[src]):
                url = f"https://github.com/{REPO}/issues/new?title=chess%7Cmove%7C{uci}&body=Just+click+Submit+new+issue+to+play+{uci}!"
                links.append(f"[{dst}]({url})")
            rows.append(f"| **`{src}`** | {' • '.join(links)} |")
        
        table_header = "| From | Valid Moves |\n| :---: | :--- |\n"
        moves_md = "<details>\n<summary><code>[ > CLICK TO VIEW & PLAY VALID MOVES ]</code></summary>\n\n" + table_header + "\n".join(rows) + "\n\n</details>"

    new_game_link = f"https://github.com/{REPO}/issues/new?title=chess%7Cnew&body=Reset+board"

    return f"""<!-- CHESS_BOARD_START -->
<div align="center">
  <p><code>[ {status} ]</code></p>
  <img src="./{SVG_FILE}" alt="CRT Chess Board" width="420" />
  <br/><br/>
  {moves_md}
  <br/>
  <sub><a href="{new_game_link}"><code>[ ./reset_board.sh ]</code></a></sub>
</div>
<!-- CHESS_BOARD_END -->"""

def update_readme(content):
    with open(README_FILE, "r", encoding="utf-8") as f:
        readme = f.read()
    
    pattern = r"<!-- CHESS_BOARD_START -->.*?<!-- CHESS_BOARD_END -->"
    updated = re.sub(pattern, content, readme, flags=re.DOTALL)
    
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(updated)

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "init"
    board = load_board()
    last_move = None

    if action == "chess|new":
        board = chess.Board()
    elif action.startswith("chess|move|"):
        move_uci = action.split("|")[2].strip()
        try:
            move = chess.Move.from_uci(move_uci)
            if move in board.legal_moves:
                board.push(move)
                last_move = move
            else:
                print(f"Illegal move: {move_uci}")
                sys.exit(0)
        except Exception as e:
            print(f"Invalid move format: {e}")
            sys.exit(0)

    save_board(board)
    generate_svg(board, last_move)
    md = build_markdown(board)
    update_readme(md)

if __name__ == "__main__":
    main()
