import pygame
import random
from collections import deque
import heapq
 
# Initialize Pygame
pygame.init()
 
# Screen Settings
WIDTH, HEIGHT = 600, 600
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
 
# Colors
BLACK = (0, 0, 0)
GREEN1 = (0, 180, 0)
GREEN2 = (0, 255, 0)
HEAD_COLOR = (50, 255, 50)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
OBSTACLE_COLORS = [(100, 100, 100), (80, 80, 80), (120, 120, 120)]
 
# Directions
DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0)
}
 
# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🐍 Snake Game ")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Consolas", 24, bold=True)
 
# High Score Functions
def load_high_score():
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read())
    except:
        return 0
 
def save_high_score(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))
 
class Snake:
    def __init__(self):
        self.body = deque([(5, 5)])
        self.direction = "RIGHT"
        self.grow_next = False
 
    def move(self):
        head_x, head_y = self.body[-1]
        dx, dy = DIRECTIONS[self.direction]
        new_head = (head_x + dx, head_y + dy)
        self.body.append(new_head)
        if not self.grow_next:
            self.body.popleft()
        else:
            self.grow_next = False
        return new_head
 
    def grow(self):
        self.grow_next = True
 
    def change_direction(self, new_dir):
        opposite = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
        if new_dir != opposite[self.direction]:
            self.direction = new_dir
 
    def get_head(self):
        return self.body[-1]
 
    def collides_with_self(self):
        return self.get_head() in list(self.body)[:-1]
 
    def collides_with_wall(self):
        x, y = self.get_head()
        return not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT)
 
    def collides_with_obstacle(self, obstacles):
        return self.get_head() in obstacles
 
def draw_snake(snake):
    for i, (x, y) in enumerate(snake.body):
        color = HEAD_COLOR if i == len(snake.body) - 1 else (GREEN1 if i % 2 == 0 else GREEN2)
        pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
 
def draw_obstacles(obstacles):
    for i, (x, y) in enumerate(obstacles):
        color = OBSTACLE_COLORS[i % len(OBSTACLE_COLORS)]
        pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
 
def draw_text(text, x, y, center=False):
    text_surface = font.render(text, True, WHITE)
    rect = text_surface.get_rect(center=(x, y)) if center else (x, y)
    screen.blit(text_surface, rect)
 
def place_food(snake, obstacles):
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos != snake.get_head() and pos not in snake.body and pos not in obstacles:
            return pos
 
def select_difficulty_and_mode():
    selecting = True
    difficulty = None
    mode = None
 
    while selecting:
        screen.fill(BLACK)
        draw_text("Select Difficulty", WIDTH // 2, HEIGHT // 3 - 40, center=True)
        draw_text("[1] Easy", WIDTH // 2, HEIGHT // 3, center=True)
        draw_text("[2] Medium", WIDTH // 2, HEIGHT // 3 + 30, center=True)
        draw_text("[3] Hard", WIDTH // 2, HEIGHT // 3 + 60, center=True)
 
        draw_text("Select Mode", WIDTH // 2, HEIGHT // 2 + 40, center=True)
        draw_text("[M] Manual", WIDTH // 2, HEIGHT // 2 + 80, center=True)
        draw_text("[A] AI Mode", WIDTH // 2, HEIGHT // 2 + 110, center=True)
 
        pygame.display.flip()
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    difficulty = (8, 5)
                elif event.key == pygame.K_2:
                    difficulty = (12, 10)
                elif event.key == pygame.K_3:
                    difficulty = (18, 20)
 
                if event.key == pygame.K_m:
                    mode = "MANUAL"
                elif event.key == pygame.K_a:
                    mode = "AI"
 
                if difficulty and mode:
                    return difficulty[0], difficulty[1], mode
 
def game_over_screen(score, high_score):
    draw_text("Game Over", WIDTH // 2, HEIGHT // 2 - 20, center=True)
    draw_text("Press R to Restart or Q to Quit", WIDTH // 2, HEIGHT // 2 + 20, center=True)
    draw_text(f"Final Score: {score}  High Score: {high_score}", WIDTH // 2, HEIGHT // 2 + 60, center=True)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                    return
                elif event.key == pygame.K_q:
                    pygame.quit(); exit()
 
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
 
def get_neighbors(pos):
    neighbors = []
    for direction in DIRECTIONS.values():
        neighbor = (pos[0] + direction[0], pos[1] + direction[1])
        if 0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT:
            neighbors.append(neighbor)
    return neighbors
 
def a_star(start, goal, snake, obstacles):
    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start))
    came_from = {}
    g_score = {start: 0}
    closed_set = set(list(snake.body)[:-1]) | obstacles
 
    while open_set:
        _, cost, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]
 
        for neighbor in get_neighbors(current):
            if neighbor in closed_set:
                continue
            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, tentative_g_score, neighbor))
 
    return []
 
def main():
    snake = Snake()
    speed, obstacle_count, mode = select_difficulty_and_mode()
 
    obstacles = set()
    while len(obstacles) < obstacle_count:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in snake.body:
            obstacles.add(pos)
 
    food = place_food(snake, obstacles)
    score = 0
    high_score = load_high_score()
    paused = False
    running = True
    path = []
 
    while running:
        screen.fill(BLACK)
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
               running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
            elif event.key == pygame.K_TAB:
            # Toggle between MANUAL and AI mode
                mode = "MANUAL" if mode == "AI" else "AI"
                path = []  # Clear current AI path when switching mode
 
        if paused:
            draw_text("Paused", WIDTH // 2, HEIGHT // 2, center=True)
            pygame.display.flip()
            continue
 
        if mode == "MANUAL":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]: snake.change_direction("UP")
            elif keys[pygame.K_DOWN]: snake.change_direction("DOWN")
            elif keys[pygame.K_LEFT]: snake.change_direction("LEFT")
            elif keys[pygame.K_RIGHT]: snake.change_direction("RIGHT")
        else:
            if not path:
                path = a_star(snake.get_head(), food, snake, obstacles)
            if path:
                next_move = path.pop(0)
                dx = next_move[0] - snake.get_head()[0]
                dy = next_move[1] - snake.get_head()[1]
                for dir_name, (x, y) in DIRECTIONS.items():
                    if (dx, dy) == (x, y):
                        snake.change_direction(dir_name)
 
        new_head = snake.move()
 
        if new_head == food:
            snake.grow()
            food = place_food(snake, obstacles)
            score += 10
            path = []
 
        if snake.collides_with_self() or snake.collides_with_wall() or snake.collides_with_obstacle(obstacles):
            if score > high_score:
                save_high_score(score)
                high_score = score
            game_over_screen(score, high_score)
            break
 
        draw_snake(snake)
        draw_obstacles(obstacles)
        pygame.draw.rect(screen, RED, (food[0] * CELL_SIZE, food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        draw_text(f"Score: {score}", 10, 10)
        draw_text(f"High Score: {high_score}", WIDTH - 200, 10)
 
        pygame.display.flip()
        clock.tick(speed)
 
    pygame.quit()
 
if __name__ == "__main__":
    main()