import pygame
import math
import random
import os

pygame.init()

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced Chase Game")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PURPLE = (160, 32, 240) 
PINK = (255, 20, 147)
GOLD = (255, 215, 0)

player_size = 50
player_speed = 5
enemy_size = 50
enemy_speed = 4
projectile_speed = 10
projectile_lifetime = 500
projectile_damage = 1
points = 0
total_points = 0
projectile_streams = [0]  # Initial stream of projectiles

player_x = WIDTH // 2
player_y = HEIGHT // 2
enemies = [{"x": 100, "y": 100, "speed": enemy_speed, "color": BLUE, "hit_points": 1, "points": 2}]
projectiles = []

start_time = pygame.time.get_ticks()
spawn_event = pygame.USEREVENT + 1
pygame.time.set_timer(spawn_event, 2000)
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)

# Player data stored within the game
player_data = {
    'total_points': total_points,
    'player_speed': player_speed,
    'projectile_speed': projectile_speed,
    'projectile_lifetime': projectile_lifetime,
    'projectile_damage': projectile_damage,
    'projectile_streams': projectile_streams
}

def load_player_data():
    global total_points, player_speed, projectile_speed, projectile_lifetime, projectile_damage, projectile_streams
    total_points = player_data['total_points']
    player_speed = player_data['player_speed']
    projectile_speed = player_data['projectile_speed']
    projectile_lifetime = player_data['projectile_lifetime']
    projectile_damage = player_data['projectile_damage']
    projectile_streams = player_data['projectile_streams']

def save_player_data():
    player_data['total_points'] = total_points
    player_data['player_speed'] = player_speed
    player_data['projectile_speed'] = projectile_speed
    player_data['projectile_lifetime'] = projectile_lifetime
    player_data['projectile_damage'] = projectile_damage
    player_data['projectile_streams'] = projectile_streams

load_player_data()

def reset_game():
    """Resets the game to its initial state."""
    global points, player_x, player_y, enemies, projectiles, start_time
    points = 0
    player_x = WIDTH // 2
    player_y = HEIGHT // 2
    enemies = [{"x": 100, "y": 100, "speed": enemy_speed, "color": BLUE, "hit_points": 1, "points": 2}]
    projectiles = []
    start_time = pygame.time.get_ticks()

def spawn_enemy():
    """Spawns a new enemy at a random position, avoiding the player."""
    while True:
        new_enemy = {
            "x": random.randint(0, WIDTH - enemy_size),
            "y": random.randint(0, HEIGHT - enemy_size),
            "speed": enemy_speed + random.uniform(0.5, 2.0), 
        }
        rarity_roll = random.random()
        if rarity_roll < 0.0126:
            new_enemy["color"] = GOLD
            new_enemy["hit_points"] = 10  
            new_enemy["points"] = 1000  
        elif rarity_roll < 0.0186:
            new_enemy["color"] = RED
            new_enemy["hit_points"] = 8  
            new_enemy["points"] = 80  
        elif rarity_roll < 0.0606:
            new_enemy["color"] = PINK
            new_enemy["hit_points"] = 6  
            new_enemy["points"] = 10  
        elif rarity_roll < 0.3004:
            new_enemy["color"] = PURPLE
            new_enemy["hit_points"] = 4  
            new_enemy["points"] = 5  
        else:
            new_enemy["color"] = BLUE
            new_enemy["hit_points"] = 2  
            new_enemy["points"] = 1  

        if math.hypot(new_enemy["x"] - player_x, new_enemy["y"] - player_y) > 100:
            enemies.append(new_enemy)
            break

def end_game_screen(points):
    """Display the end game screen with options to restart, go to main menu, or quit."""
    global total_points
    total_points += points
    save_player_data()
    end_running = True

    while end_running:
        screen.fill(WHITE)

        game_over_text = font.render("Game Over!", True, BLACK)
        screen.blit(game_over_text, ((WIDTH - game_over_text.get_width()) // 2, HEIGHT // 4))

        score_text = font.render(f"Your Score: {points}", True, BLACK)
        screen.blit(score_text, ((WIDTH - score_text.get_width()) // 2, HEIGHT // 3))

        restart_button_rect = pygame.Rect(WIDTH // 3 - 75, HEIGHT // 2, 150, 50)
        main_menu_button_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2, 150, 50)
        quit_button_rect = pygame.Rect(2 * WIDTH // 3 - 75, HEIGHT // 2, 150, 50)

        pygame.draw.rect(screen, GREEN, restart_button_rect)
        pygame.draw.rect(screen, BLUE, main_menu_button_rect)
        pygame.draw.rect(screen, RED, quit_button_rect)

        restart_text = font.render("Restart", True, BLACK)
        main_menu_text = font.render("Main Menu", True, BLACK)
        quit_text = font.render("Quit", True, BLACK)

        screen.blit(restart_text, (restart_button_rect.x + (restart_button_rect.width - restart_text.get_width()) // 2,
                                   restart_button_rect.y + 10))
        screen.blit(main_menu_text, (main_menu_button_rect.x + (main_menu_button_rect.width - main_menu_text.get_width()) // 2,
                                     main_menu_button_rect.y + 10))
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
                elif main_menu_button_rect.collidepoint(mouse_x, mouse_y):
                    return "main_menu"
                elif quit_button_rect.collidepoint(mouse_x, mouse_y):
                    end_running = False
                    return False

def avoid_collision(enemy, other_enemy):
    """Adjust enemy position to avoid collision with another enemy."""
    dx = enemy["x"] - other_enemy["x"]
    dy = enemy["y"] - other_enemy["y"]
    distance = math.sqrt(dx**2 + dy**2)
    if distance < enemy_size:
        if dx != 0:
            enemy["x"] += (dx / distance) * enemy_speed
        if dy != 0:
            enemy["y"] += (dy / distance) * enemy_speed

def shop_screen():
    """Display the shop screen with upgrade options."""
    global total_points, player_speed, projectile_speed, projectile_lifetime, projectile_damage, projectile_streams
    shop_running = True

    while shop_running:
        screen.fill(WHITE)

        shop_text = font.render("Shop", True, BLACK)
        screen.blit(shop_text, ((WIDTH - shop_text.get_width()) // 2, HEIGHT // 4))

        points_text = font.render(f"Points: {total_points}", True, BLACK)
        screen.blit(points_text, (10, 10))

        player_speed_button_rect = pygame.Rect(WIDTH // 3 - 75, HEIGHT // 2 - 210, 200, 60)
        projectile_speed_button_rect = pygame.Rect(WIDTH // 3 - 75, HEIGHT // 2 - 140, 200, 60)
        projectile_distance_button_rect = pygame.Rect(WIDTH // 3 - 75, HEIGHT // 2 - 70, 200, 60)
        projectile_damage_button_rect = pygame.Rect(WIDTH // 3 - 75, HEIGHT // 2, 200, 60)
        new_stream_button_rect = pygame.Rect(WIDTH // 3 - 75, HEIGHT // 2 + 70, 200, 60)
        back_button_rect = pygame.Rect(WIDTH // 3 - 75, HEIGHT // 2 + 140, 200, 60)

        pygame.draw.rect(screen, GREEN, player_speed_button_rect)
        pygame.draw.rect(screen, GREEN, projectile_speed_button_rect)
        pygame.draw.rect(screen, GREEN, projectile_distance_button_rect)
        pygame.draw.rect(screen, GREEN, projectile_damage_button_rect)
        pygame.draw.rect(screen, GREEN, new_stream_button_rect)
        pygame.draw.rect(screen, RED, back_button_rect)

        player_speed_text = font.render("Player Speed", True, BLACK)
        player_speed_price_text = font.render("40", True, BLACK)
        projectile_speed_text = font.render("Proj Speed", True, BLACK)
        projectile_speed_price_text = font.render("20", True, BLACK)
        projectile_distance_text = font.render("Proj Distance", True, BLACK)
        projectile_distance_price_text = font.render("40", True, BLACK)
        projectile_damage_text = font.render("Proj Damage", True, BLACK)
        projectile_damage_price_text = font.render("60", True, BLACK)
        new_stream_text = font.render("New Stream", True, BLACK)
        new_stream_price_text = font.render("150", True, BLACK)
        back_text = font.render("Back", True, BLACK)

        screen.blit(player_speed_text, (player_speed_button_rect.x + 5, player_speed_button_rect.y + 10))
        screen.blit(player_speed_price_text, (player_speed_button_rect.right - player_speed_price_text.get_width() - 5, player_speed_button_rect.y + 10))
        screen.blit(projectile_speed_text, (projectile_speed_button_rect.x + 5, projectile_speed_button_rect.y + 10))
        screen.blit(projectile_speed_price_text, (projectile_speed_button_rect.right - projectile_speed_price_text.get_width() - 5, projectile_speed_button_rect.y + 10))
        screen.blit(projectile_distance_text, (projectile_distance_button_rect.x + 5, projectile_distance_button_rect.y + 10))
        screen.blit(projectile_distance_price_text, (projectile_distance_button_rect.right - projectile_distance_price_text.get_width() - 5, projectile_distance_button_rect.y + 10))
        screen.blit(projectile_damage_text, (projectile_damage_button_rect.x + 5, projectile_damage_button_rect.y + 10))
        screen.blit(projectile_damage_price_text, (projectile_damage_button_rect.right - projectile_damage_price_text.get_width() - 5, projectile_damage_button_rect.y + 10))
        screen.blit(new_stream_text, (new_stream_button_rect.x + 5, new_stream_button_rect.y + 10))
        screen.blit(new_stream_price_text, (new_stream_button_rect.right - new_stream_price_text.get_width() - 5, new_stream_button_rect.y + 10))
        screen.blit(back_text, (back_button_rect.x + (back_button_rect.width - back_text.get_width()) // 2, back_button_rect.y + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                shop_running = False
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                if player_speed_button_rect.collidepoint(mouse_x, mouse_y) and total_points >= 40:
                    total_points -= 40
                    player_speed += 1
                    save_player_data()
                elif projectile_speed_button_rect.collidepoint(mouse_x, mouse_y) and total_points >= 20:
                    total_points -= 20
                    projectile_speed += 1
                    save_player_data()
                elif projectile_distance_button_rect.collidepoint(mouse_x, mouse_y) and total_points >= 40:
                    total_points -= 40
                    projectile_lifetime += 100
                    save_player_data()
                elif projectile_damage_button_rect.collidepoint(mouse_x, mouse_y) and total_points >= 60:
                    total_points -= 60
                    projectile_damage += 1
                    save_player_data()
                elif new_stream_button_rect.collidepoint(mouse_x, mouse_y) and total_points >= 150:
                    total_points -= 150
                    new_angle = 360 / (len(projectile_streams) + 1)
                    projectile_streams = [i * new_angle for i in range(len(projectile_streams) + 1)]
                    save_player_data()
                elif back_button_rect.collidepoint(mouse_x, mouse_y):
                    shop_running = False

def start_screen():
    """Display the start screen with options to start the game, go to the shop, or quit."""
    start_running = True

    while start_running:
        screen.fill(WHITE)

        title_text = font.render("Game", True, BLACK)
        screen.blit(title_text, ((WIDTH - title_text.get_width()) // 2, HEIGHT // 4))

        start_button_rect = pygame.Rect(WIDTH // 3 - 75, HEIGHT // 2, 150, 50)
        shop_button_rect = pygame.Rect(2 * WIDTH // 3 - 75, HEIGHT // 2, 150, 50)
        quit_button_rect = pygame.Rect((WIDTH - 150) // 2, HEIGHT // 2 + 90, 150, 50)

        pygame.draw.rect(screen, GREEN, start_button_rect)
        pygame.draw.rect(screen, BLUE, shop_button_rect)
        pygame.draw.rect(screen, RED, quit_button_rect)

        start_text = font.render("Start", True, BLACK)
        shop_text = font.render("Shop", True, BLACK)
        quit_text = font.render("Quit", True, BLACK)

        screen.blit(start_text, (start_button_rect.x + (start_button_rect.width - start_text.get_width()) // 2,
                                 start_button_rect.y + 10))
        screen.blit(shop_text, (shop_button_rect.x + (shop_button_rect.width - shop_text.get_width()) // 2,
                                shop_button_rect.y + 10))
        screen.blit(quit_text, (quit_button_rect.x + (quit_button_rect.width - quit_text.get_width()) // 2,
                                quit_button_rect.y + 10))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start_running = False
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                if start_button_rect.collidepoint(mouse_x, mouse_y):
                    return True
                elif shop_button_rect.collidepoint(mouse_x, mouse_y):
                    if shop_screen() == False:
                        return False
                elif quit_button_rect.collidepoint(mouse_x, mouse_y):
                    pygame.quit()
                    exit()

def handle_player_movement(keys):
    global player_x, player_y
    if keys[pygame.K_w]:
        player_y -= player_speed
    if keys[pygame.K_s]:
        player_y += player_speed
    if keys[pygame.K_a]:
        player_x -= player_speed
    if keys[pygame.K_d]:
        player_x += player_speed

    player_x = max(0, min(WIDTH - player_size, player_x))
    player_y = max(0, min(HEIGHT - player_size, player_y))

def handle_projectiles():
    for projectile in projectiles[:]:
        projectile["x"] += projectile["dx"] * projectile_speed
        projectile["y"] += projectile["dy"] * projectile_speed
        if pygame.time.get_ticks() - projectile["spawn_time"] > projectile_lifetime:
            projectiles.remove(projectile)

def handle_enemy_movement():
    global points  # Add this line
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
            return False
        for projectile in projectiles[:]:
            projectile_rect = pygame.Rect(projectile["x"], projectile["y"], 10, 10)
            if projectile_rect.colliderect(enemy_rect):
                enemy["hit_points"] -= projectile_damage
                projectiles.remove(projectile)
                if enemy["hit_points"] <= 0:
                    enemies.remove(enemy)
                    points += enemy["points"]
                break

        # Prevent enemies from stacking on top of each other
        for other_enemy in enemies:
            if other_enemy != enemy:
                other_enemy_rect = pygame.Rect(other_enemy["x"], other_enemy["y"], enemy_size, enemy_size)
                if enemy_rect.colliderect(other_enemy_rect):
                    avoid_collision(enemy, other_enemy)
    return True

def draw_game_elements():
    screen.fill(WHITE)
    pygame.draw.rect(screen, RED, (player_x, player_y, player_size, player_size))

    for enemy in enemies:
        pygame.draw.rect(screen, enemy["color"], (enemy["x"], enemy["y"], enemy_size, enemy_size))
        # Draw health bar
        health_bar_width = enemy_size * (enemy["hit_points"] / 5)
        pygame.draw.rect(screen, RED, (enemy["x"], enemy["y"] - 10, health_bar_width, 5))

    for projectile in projectiles:
        pygame.draw.rect(screen, GREEN, (projectile["x"], projectile["y"], 10, 10))

    time_text = font.render(f"Time: {elapsed_time}s", True, BLACK)
    points_text = font.render(f"Points: {points}", True, BLACK)
    total_points_text = font.render(f"Total Points: {total_points}", True, BLACK)
    screen.blit(time_text, (10, 10))
    screen.blit(points_text, (WIDTH - 200, 10))
    screen.blit(total_points_text, (WIDTH - 200, 50))

    pygame.display.flip()

if not start_screen():
    pygame.quit()
    exit()

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
                for angle in projectile_streams:
                    angle_rad = math.radians(angle)
                    dx = math.cos(angle_rad) * direction_x - math.sin(angle_rad) * direction_y
                    dy = math.sin(angle_rad) * direction_x + math.cos(angle_rad) * direction_y
                    projectiles.append({
                        "x": player_x + player_size // 2,
                        "y": player_y + player_size // 2,
                        "dx": dx,
                        "dy": dy,
                        "spawn_time": pygame.time.get_ticks(),
                    })

    keys = pygame.key.get_pressed()
    handle_player_movement(keys)
    handle_projectiles()
    if not handle_enemy_movement():
        running = False

    draw_game_elements()
    clock.tick(60)

    if not running:
        result = end_game_screen(points)
        if result == True:
            reset_game()
            running = True
        elif result == "main_menu":
            if not start_screen():
                pygame.quit()
                exit()
            reset_game()
            running = True
        else:
            pygame.quit()

