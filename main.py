from engine import GameState
from ui import main_menu

def main():
    state = GameState()
    state.load_from_earth()
    main_menu(state)

if __name__ == "__main__":
    main()

