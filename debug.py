from game import Game

choice = ' '
while choice != "q":
    game = Game()
    game.step()
    snapshot = game.ascii_snapshot()
    print(snapshot)
    print(f'{len(snapshot)} characters')
    choice = input()
