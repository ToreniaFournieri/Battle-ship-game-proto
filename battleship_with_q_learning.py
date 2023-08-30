
import random

# Constants
GRID_SIZE = 5
SHIP_ARMOR = 10
CANNON_DAMAGE = 2
REPAIR_AMOUNT = 1
DIRECTIONS = ['UP', 'DOWN', 'LEFT', 'RIGHT']
NUM_ACTIONS = 9  # 4 directions of move, 4 directions of shoot, 1 repair
LEARNING_RATE = 0.1
DISCOUNT_FACTOR = 0.9
EXPLORATION_RATE = 0.3
q_table = {}

def initialize_grid(size):
    return [[' ' for _ in range(size)] for _ in range(size)]

def place_ship(grid, ship_symbol):
    x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
    while grid[y][x] != ' ':
        x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
    grid[y][x] = ship_symbol
    return x, y

def move_ship_improved(grid, x, y, direction):
    old_x, old_y = x, y
    grid[y][x] = ' '
    if direction == 'UP' and y > 0:
        y -= 1
    elif direction == 'DOWN' and y < GRID_SIZE - 1:
        y += 1
    elif direction == 'LEFT' and x > 0:
        x -= 1
    elif direction == 'RIGHT' and x < GRID_SIZE - 1:
        x += 1
    if grid[y][x] != ' ':
        x, y = old_x, old_y
    grid[y][x] = 'S'
    return x, y

def shoot_cannon(x, y, direction):
    targets = []
    if direction == 'UP':
        targets.append((x, max(0, y - 2)))
    elif direction == 'DOWN':
        targets.append((x, min(GRID_SIZE - 1, y + 2)))
    elif direction == 'LEFT':
        targets.append((max(0, x - 2), y))
    elif direction == 'RIGHT':
        targets.append((min(GRID_SIZE - 1, x + 2), y))
    return targets

def apply_periodic_damage(player_armor, enemy_armor, turn_count):
    if turn_count % 5 == 0:
        player_armor -= 1
        enemy_armor -= 1
    return player_armor, enemy_armor

def get_state(player_pos, enemy_pos):
    return (player_pos, enemy_pos)

def choose_action(state):
    if random.random() < EXPLORATION_RATE or state not in q_table:
        return random.randint(0, NUM_ACTIONS - 1)
    return max(list(enumerate(q_table[state])), key=lambda x: x[1])[0]

def update_q_value(state, action, reward, next_state):
    if state not in q_table:
        q_table[state] = [0] * NUM_ACTIONS
    if next_state not in q_table:
        q_table[next_state] = [0] * NUM_ACTIONS
    max_future_q = max(q_table[next_state])
    new_q = (1 - LEARNING_RATE) * q_table[state][action] + LEARNING_RATE * (reward + DISCOUNT_FACTOR * max_future_q)
    q_table[state][action] = new_q

def display_action(action):
    if action < 4:
        return f"Moved {DIRECTIONS[action]}"
    elif action < 8:
        return f"Shot {DIRECTIONS[action - 4]}"
    else:
        return "Repaired the ship"

def play_displayed_game_with_q_learning():
    grid = initialize_grid(GRID_SIZE)
    player_x, player_y = place_ship(grid, 'P')
    enemy_x, enemy_y = place_ship(grid, 'E')
    player_armor = SHIP_ARMOR
    enemy_armor = SHIP_ARMOR
    turn_count = 0
    while player_armor > 0 and enemy_armor > 0 and turn_count < 50:
        print(f"\nTurn {turn_count + 1}")
        print(f"Q-learning Player Armor: {player_armor}")
        print(f"Random Player Armor: {enemy_armor}")
        print(' '.join(['-' for _ in range(GRID_SIZE)]))
        for row in grid:
            print(' '.join(row))
        print(' '.join(['-' for _ in range(GRID_SIZE)]))
        state = get_state((player_x, player_y), (enemy_x, enemy_y))
        action = choose_action(state)
        print(f"\nQ-learning Player's Action: {display_action(action)}")
        if action < 4:
            direction = DIRECTIONS[action]
            player_x, player_y = move_ship_improved(grid, player_x, player_y, direction)
        elif action < 8:
            direction = DIRECTIONS[action - 4]
            targets = shoot_cannon(player_x, player_y, direction)
            for tx, ty in targets:
                if (tx, ty) == (enemy_x, enemy_y):
                    enemy_armor -= CANNON_DAMAGE
        else:
            player_armor = min(SHIP_ARMOR, player_armor + REPAIR_AMOUNT)
        if enemy_armor <= 0:
            print("\nQ-learning player won!")
            return "Q-learning player won"
        
        # Random player's turn
        print("\nRandom Player's Action:")
        enemy_x, enemy_y, player_armor = automated_turn_with_display(grid, enemy_x, enemy_y, player_x, player_y, player_armor)
        
        if player_armor <= 0:
            print("\nRandom player won!")
            return "Random player won"
        
        # Apply periodic damage
        player_armor, enemy_armor = apply_periodic_damage(player_armor, enemy_armor, turn_count)
        
        turn_count += 1
    
    print("\nGame ended in a draw!")
    return "Draw"

def automated_turn_with_display(grid, x, y, enemy_x, enemy_y, armor):
    action = random.choice(["move", "shoot", "repair"])
    if action == "move":
        direction = random.choice(DIRECTIONS)
        x, y = move_ship_improved(grid, x, y, direction)
        print(f"Moved {direction}")
    elif action == "shoot":
        direction = random.choice(DIRECTIONS)
        targets = shoot_cannon(x, y, direction)
        hit = False
        for tx, ty in targets:
            if (tx, ty) == (enemy_x, enemy_y):
                armor -= CANNON_DAMAGE
                hit = True
        print(f"Shot {direction} {'and hit!' if hit else 'and missed.'}")
    elif action == "repair":
        armor = min(SHIP_ARMOR, armor + REPAIR_AMOUNT)
        print("Repaired the ship!")
    return x, y, armor

if __name__ == "__main__":
    result = play_displayed_game_with_q_learning()
    print(result)

