import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced Chase Game")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

player_size = 50
player_speed = 5
enemy_size = 50
enemy_speed = 4
projectile_speed = 10
projectile_lifetime = 500
points = 0

player_x = WIDTH // 2
player_y = HEIGHT // 2
enemies = [{"x": 100, "y": 100, "speed": enemy_speed}]
projectiles = []

start_time = pygame.time.get_ticks()
spawn_event = pygame.USEREVENT + 1
pygame.time.set_timer(spawn_event, 2000)
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)

def reset_game():
    """Resets the game to its initial state."""
    global points, player_x, player_y, enemies, projectiles, start_time
    points = 0
    player_x = WIDTH // 2
    player_y = HEIGHT // 2
    enemies = [{"x": 100, "y": 100, "speed": enemy_speed}]
    projectiles = []
    start_time = pygame.time.get_ticks()

def spawn_enemy():
    """Spawns a new enemy at a random position."""
    new_enemy = {
        "x": random.randint(0, WIDTH - enemy_size),
        "y": random.randint(0, HEIGHT - enemy_size),
        "speed": enemy_speed,
    }
    enemies.append(new_enemy)

def end_game_screen(points):
    """Display the end game screen with options to restart or quit."""
    end_running = True

    while end_running:
        screen.fill(WHITE)

        game_over_text = font.render("Game Over!", True, BLACK)
        screen.blit(game_over_text, ((WIDTH - game_over_text.get_width()) // 2, HEIGHT // 4))

        score_text = font.render(f"Your Score: {points}", True, BLACK)
        screen.blit(score_text, ((WIDTH - score_text.get_width()) // 2, HEIGHT // 3))

        restart_button_rect = pygame.Rect(WIDTH // 3 - 75, HEIGHT // 2, 150, 50)
        quit_button_rect = pygame.Rect(2 * WIDTH // 3 - 75, HEIGHT // 2, 150, 50)

        pygame.draw.rect(screen, GREEN, restart_button_rect)
        pygame.draw.rect(screen, RED, quit_button_rect)

        restart_text = font.render("Restart", True, BLACK)
        quit_text = font.render("Quit", True, BLACK)

        screen.blit(restart_text, (restart_button_rect.x + (restart_button_rect.width - restart_text.get_width()) // 2,
                                   restart_button_rect.y + 10))
        screen.blit(quit_text, (quit_button_rect.x + (quit_button_rect.width - quit_text.get_width()) // 2,
                                quit_button_rect.y + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end_running = False
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                if restart_button_rect.collidepoint(mouse_x, mouse_y):
                    return True
                elif quit_button_rect.collidepoint(mouse_x, mouse_y):
                    end_running = False
                    return False

running = True
while running:
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == spawn_event:
            spawn_enemy()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - player_x
            dy = mouse_y - player_y
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                direction_x = dx / distance
                direction_y = dy / distance
                projectiles.append({
                    "x": player_x + player_size // 2,
                    "y": player_y + player_size // 2,
                    "dx": direction_x,
                    "dy": direction_y,
                    "spawn_time": pygame.time.get_ticks(),
                })

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player_y -= player_speed
    if keys[pygame.K_DOWN]:
        player_y += player_speed
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed

    player_x = max(0, min(WIDTH - player_size, player_x))
    player_y = max(0, min(HEIGHT - player_size, player_y))

    for projectile in projectiles[:]:
        projectile["x"] += projectile["dx"] * projectile_speed
        projectile["y"] += projectile["dy"] * projectile_speed
        if pygame.time.get_ticks() - projectile["spawn_time"] > projectile_lifetime:
            projectiles.remove(projectile)

    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    for enemy in enemies[:]:
        dx = player_x - enemy["x"]
        dy = player_y - enemy["y"]
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            enemy["x"] += enemy["speed"] * (dx / distance)
            enemy["y"] += enemy["speed"] * (dy / distance)

        enemy_rect = pygame.Rect(enemy["x"], enemy["y"], enemy_size, enemy_size)
        if player_rect.colliderect(enemy_rect):
            running = False
        for projectile in projectiles[:]:
            projectile_rect = pygame.Rect(projectile["x"], projectile["y"], 10, 10)
            if projectile_rect.colliderect(enemy_rect):
                enemies.remove(enemy)
                projectiles.remove(projectile)
                points += 1
                break

    screen.fill(WHITE)
    pygame.draw.rect(screen, RED, (player_x, player_y, player_size, player_size))

    for enemy in enemies:
        pygame.draw.rect(screen, BLUE, (enemy["x"], enemy["y"], enemy_size, enemy_size))

    for projectile in projectiles:
        pygame.draw.rect(screen, GREEN, (projectile["x"], projectile["y"], 10, 10))

    time_text = font.render(f"Time: {elapsed_time}s", True, BLACK)
    points_text = font.render(f"Points: {points}", True, BLACK)
    screen.blit(time_text, (10, 10))
    screen.blit(points_text, (WIDTH - 150, 10))

    pygame.display.flip()
    clock.tick(60)

    if not running:
        if end_game_screen(points):
            reset_game()
            running = True
        else:
            pygame.quit()