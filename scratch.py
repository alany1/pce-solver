import pygambit

# Create prisoners dilemma game
game = pygambit.Game.new_table([2, 2])
game.title = "Prisoners Dilemma"
game.players[0].label = "Player 1"
game.players[1].label = "Player 2"

# Set payoffs
game.players[0].strategies[0].label = "Cooperate"
game.players[0].strategies[1].label = "Defect"
game.players[1].strategies[0].label = "Cooperate"
game.players[1].strategies[1].label = "Defect"

# game.players[0].strategies[0].payoff = [3, 3]
# game.players[0].strategies[1].payoff = [0, 5]
# game.players[1].strategies[0].payoff = [5, 0]
# game.players[1].strategies[1].payoff = [1, 1]
# Set player rewards
game[0,0][0] = 3
game[0,0][1] = 3

game[0,1][0] = 0
game[0,1][1] = 5
game[1,0][0] = 5
game[1,0][1] = 0
game[1,1][0] = 1
game[1,1][1] = 1
# Write to file

# This will print out all strategy profile

# p is a mixed strategy profile of ALL PLAYERS in the game
 
p = game.mixed_strategy_profile()
print(list(p))
print(p[game.players[0].strategies[0]]) # This will give the probability of player 0 playign stratey 0 under p.
print(p.payoff(game.players[0])) # Expected payoff of player 0 under p.