

# @ author: Gediyon M. Girma
# Tic-Tac-Toe game AI computer vs human

# the logic implemented in this game is taken form the book Reinforcement Learning: an Introduction second edition by Richard S. Sutton and Andrew G. Barto
# simiplified explanation of the strategy used
# 1, all possible states of the board were generated by combining all possible sequences of "X", "O" and " " posisiton of the board for all 9 cells
# 2, a look up table is created form a dictionary to assign all winning posion for "X" as 1 and for "O" as zero and all other states to be 0.5 initially.
# 3, two types of moves were considered one a "greedy move" where the player always chooses the move that ends up with higher next state value and an "Exploratory move" which is a move at random
# 4, we need a feed back loop to update the state values whenever we make a greedy move



import random
from itertools import product
from collections import deque

class TicTacToeRL:
    def __init__(self):
        self.board = [' ' for _ in range(9)]
        self.state_values = {}  # Dictionary to store state values
        self.learning_rate = 0.1  # Learning rate for Q-learning
        self.epsilon = 0.1  # Epsilon for epsilon-greedy policy
        self.recent_states = deque(maxlen=3)  # List to save recent states
        self.recent_states.append(self.get_state())
        self.recent_states.append(self.get_state())


        # Initialize state values
        self.initialize_state_values()
        
    # we assume the computer is playing as X

    def initialize_state_values(self):
        # Initialize state values as described
        # Generate all possible combinations of three numbers (0, 1, and 2) for each of the nine sequences
        sequences = product([0, 1, 2], repeat=9)

        all_combinations = []

        for combination in sequences:
            # Check if the maximum difference between the count of 1's and 2's is one for this combination
            count_1 = combination.count(1)
            count_2 = combination.count(2)
            if abs(count_1 - count_2) <= 1:
                all_combinations.append(combination)
        
        self.state_values = {}
        
        win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8),  # Horizontal
                    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Vertical
                    (0, 4, 8), (2, 4, 6)]             # Diagonal
        
        for combination in all_combinations:
            
            self.state_values[combination] = 0.5  # by default all states are assigned 0.5
            for condition in win_conditions:
                if combination[condition[0]] == combination[condition[1]] == combination[condition[2]] == 'X':
                    self.state_values[combination] = 1 # if X win assign 1
                    break
                elif combination[condition[0]] == combination[condition[1]] == combination[condition[2]] == 'O':
                    self.state_values[combination] = 0  # if O wins assign 0
                    break



    def get_state(self):
        # Convert board to state representation
        state = []
        for i, cell in enumerate(self.board):
            if cell == 'X':
                state.append(1)
            elif cell == 'O':
                state.append(2)
            else:
                state.append(0)
        return state

    def set_position(self, position, player):
        if self.board[position] == ' ':
            self.board[position] = player
            self.recent_states.append(self.get_state())
            return True
        else:
            return False


    def make_greedy_move(self):
        state = self.get_state()
        available_moves = [i for i, cell in enumerate(self.board) if cell == ' '] # list of empty cells
        next_states = []
        for move in available_moves:
            new_state = state.copy()[move]=1
            next_states.append((new_state, move))
                    
        next_state_values = {move: self.state_values.get(next_state, 0) for next_state, move in next_states}
        max_value = max(next_state_values.values())
        best_moves = [move for move, value in next_state_values.items() if value == max_value]
        return random.choice(best_moves)


    def make_exploratory_move(self):
        available_moves = [i for i, cell in enumerate(self.board) if cell == ' ']
        return random.choice(available_moves)

    def make_move(self, player):
        greedy_move = False
        if player == 'X':
            if random.random() > self.epsilon:
                move = self.make_greedy_move() 
                greedy_move = True
            else:
                move = self.make_exploratory_move()
        else:
            available_moves = [i for i, cell in enumerate(self.board) if cell == ' ']
            move = random.choice(available_moves)
        self.board[move] = player
        self.recent_states.append(self.get_state())
        if greedy_move:
            self.backup_state_values(self.recent_states[0],self.recent_states[2])        

    def backup_state_values(self, old_state, new_state):
        old_state = tuple(old_state)
        new_state = tuple(new_state)
        old_value = self.state_values[old_state]
        new_value = self.state_values[new_state]
        updated_value = old_value + self.learning_rate * (new_value - old_value)
        self.state_values[old_state] = updated_value

    def play_game(self):
        self.reset()
        winner = None
        while not self.check_win() and not self.check_draw():
            self.make_move('X')
            if self.check_win() or self.check_draw():
                break
            self.make_move('O')
            if self.check_win() or self.check_draw():
                break

        if self.check_win():
            winner = self.check_win()
        return winner

    def reset(self):
        self.board = [' ' for _ in range(9)]
        self.recent_states = deque(maxlen=3)  # List to save recent states
        self.recent_states.append(self.get_state())
        self.recent_states.append(self.get_state())
        

    def check_win(self):
        win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8),  # Horizontal
                    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Vertical
                    (0, 4, 8), (2, 4, 6)]             # Diagonal

        for condition in win_conditions:
            if self.board[condition[0]] == self.board[condition[1]] == self.board[condition[2]] != ' ':
                return self.board[condition[0]]
        return None

    def check_draw(self):
        return ' ' not in self.board

    def print_board(self):
        for i in range(3):
            print(self.board[i*3], '|', self.board[i*3 + 1], '|', self.board[i*3 + 2])
            if i < 2:
                print("---------")

if __name__ == "__main__":
    num_episodes = 10000 # Number of episodes/games to play during training

    # Training phase
    game = TicTacToeRL()

    for episode in range(num_episodes):
        game.play_game()

    print("Training complete!")

    # Human vs Computer game
    while True:
        game.reset()
        print("New Game!")

        while not game.check_win() and not game.check_draw():
            game.print_board()

            # Human move
            human_move = int(input("Enter your move (0-8): "))
            if game.set_position(human_move, 'O'):
                if game.check_win() == 'O':
                    game.print_board()
                    print("You win!")
                    break
                elif game.check_draw():
                    game.print_board()
                    print("It's a draw!")
                    break

                # Computer move
                game.make_move('X')
                if game.check_win() == 'X':
                    game.print_board()
                    print("Computer wins!")
                    break
                elif game.check_draw():
                    game.print_board()
                    print("It's a draw!")
                    break
            else:
                print("Invalid move! Try again.")

        play_again = input("Do you want to play again? (yes/no): ")
        if play_again.lower() != 'yes':
            break

