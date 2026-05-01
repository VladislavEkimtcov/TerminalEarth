from engine import GameState

state = GameState()
state.load_from_earth()
print("Initial Player Wealth:", state.player_wealth)

actions = ["build factory in nsw", "deploy 100 troops to nsw"]
for a in actions:
    print(state.parse_action(a))

print("After Player Wealth:", state.player_wealth)
print("NSW Wealth:", state.regions["NSW"].wealth)
