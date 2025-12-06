import pygame
import sys
import random
import math

pygame.init()

# Window
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Egg Rescue Game - Flat Ground")
clock = pygame.time.Clock()

# World
WORLD_WIDTH = 3000
GROUND_Y = 350

# Load images
man = pygame.image.load("Desktop\\Jackfruit\\image.png").convert_alpha()
dino = pygame.image.load("Desktop\\Jackfruit\\deno.png").convert_alpha()
egg = pygame.image.load("Desktop\\Jackfruit\\eggg.png").convert_alpha()
rock_img = pygame.image.load("Desktop\\Jackfruit\\rock(1).png").convert_alpha()

# Resize
man = pygame.transform.scale(man, (100, 159))
dino = pygame.transform.scale(dino, (200, 200))
egg = pygame.transform.scale(egg, (80, 120))
rock_img = pygame.transform.scale(rock_img, (80, 60))

man_width, man_height = 100, 159
dino_width, dino_height = 200, 200
egg_width, egg_height = 80, 120
rock_width, rock_height = 80, 60

gravity = 1
jump_strength = -20

egg_x = 2000
egg_y = GROUND_Y - egg_height

# Dino movement
dino_radius = 120
dino_speed_angle = 0.03

speed = 6
rock_speed = 3

# Platforms
platform_colors = [(139, 69, 19), (160, 82, 45), (205, 133, 63)]
platforms = [
    [600, 250, 150, 15, random.choice(platform_colors)],
    [1000, 200, 200, 15, random.choice(platform_colors)],
    [1500, 230, 150, 15, random.choice(platform_colors)],
]

# Nature decoration
clouds = [[random.randint(0, WORLD_WIDTH), random.randint(50, 150),
           random.randint(50, 120), random.uniform(0.2, 0.5)] for _ in range(8)]
trees = [[random.randint(0, WORLD_WIDTH), GROUND_Y - 120,
          random.randint(50, 100)] for _ in range(10)]
flowers = [[random.randint(0, WORLD_WIDTH), GROUND_Y - 10,
            random.choice([(255, 0, 0), (255, 192, 203), (255, 255, 0),
                           (0, 255, 255), (0, 128, 0), (255, 140, 0),
                           (128, 0, 128)])] for _ in range(60)]
birds = [[random.randint(0, WORLD_WIDTH), random.randint(50, 200),
          random.choice([-1, 1]) * random.uniform(1, 2)] for _ in range(6)]

# Fonts (emoji support)
font = pygame.font.SysFont("Segoe UI Emoji", 40)
big_font = pygame.font.SysFont("Segoe UI Emoji", 60)

def show_text(text, color, y, big=False, x=None):
    label = big_font.render(text, True, color) if big else font.render(text, True, color)
    if x is None:
        rect = label.get_rect(center=(WIDTH // 2, y))
    else:
        rect = label.get_rect(topleft=(x, y))
    screen.blit(label, rect)

# Mountains
mountain_points = []
step = 100
for x in range(0, WORLD_WIDTH + step, step):
    height = random.randint(150, 250)
    mountain_points.append((x, GROUND_Y - height))

# Rocks
def create_rocks():
    rocks = []
    x = 50
    while x < egg_x - 50:
        x += random.randint(300, 500)
        rocks.append([x, GROUND_Y - rock_height])
    return rocks

# Game state
def reset_game():
    return {
        "man_x": 50,
        "man_y": GROUND_Y - man_height,
        "man_vel_y": 0,
        "is_jumping": False,
        "dino_angle": 0,
        "rocks": create_rocks(),
        "game_state": "playing",
        "max_distance": egg_x,
        "score": 0
    }

# Hitboxes
def get_man_hitbox(state):
    return pygame.Rect(state["man_x"] + 20, state["man_y"] + 10, man_width - 40, man_height - 20)
def get_dino_hitbox(dino_x, dino_y):
    return pygame.Rect(dino_x + 30, dino_y + 40, dino_width - 60, dino_height - 60)
def get_rock_hitbox(rock):
    return pygame.Rect(rock[0] + 5, rock[1] + 5, rock_width - 10, rock_height - 10)
def get_egg_hitbox():
    return pygame.Rect(egg_x + 10, egg_y + 10, egg_width - 20, egg_height - 20)

state = reset_game()
running = True

# Main loop
while running:
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if state["game_state"] == "playing":
        # Update score based on distance
        state["score"] = state["man_x"]

        # Move player
        if keys[pygame.K_RIGHT]:
            state["man_x"] += speed
        if keys[pygame.K_LEFT]:
            state["man_x"] -= speed
        state["man_x"] = max(0, min(WORLD_WIDTH - man_width, state["man_x"]))

        # Jump
        if keys[pygame.K_SPACE] and not state["is_jumping"]:
            state["man_vel_y"] = jump_strength
            state["is_jumping"] = True

        # Gravity
        state["man_vel_y"] += gravity
        state["man_y"] += state["man_vel_y"]

        man_rect = get_man_hitbox(state)

        # Platform collision
        on_platform = False
        for plat in platforms:
            plat_rect = pygame.Rect(plat[0], plat[1], plat[2], plat[3])
            if man_rect.colliderect(plat_rect) and state["man_vel_y"] >= 0:
                if state["man_y"] + man_height <= plat[1] + 10:
                    state["man_y"] = plat[1] - man_height
                    state["man_vel_y"] = 0
                    state["is_jumping"] = False
                    on_platform = True

        # Ground collision
        if state["man_y"] + man_height >= GROUND_Y and not on_platform:
            state["man_y"] = GROUND_Y - man_height
            state["man_vel_y"] = 0
            state["is_jumping"] = False

        # Camera
        camera_x = max(0, min(WORLD_WIDTH - WIDTH, state["man_x"] - 200))

        # Dino movement
        state["dino_angle"] += dino_speed_angle
        dino_x = egg_x + dino_radius * math.cos(state["dino_angle"])
        dino_y = egg_y + dino_radius * math.sin(state["dino_angle"])

        # Move rocks
        for rock in state["rocks"]:
            if keys[pygame.K_RIGHT]:
                rock[0] -= rock_speed
            elif keys[pygame.K_LEFT]:
                rock[0] += rock_speed

        # Draw everything
        screen.fill((135, 206, 235))  # sky

        # Mountains
        mountain_poly = [(mountain_points[0][0] - camera_x * 0.5, GROUND_Y)]
        for px, py in mountain_points:
            mountain_poly.append((px - camera_x * 0.5, py))
        mountain_poly.append((mountain_points[-1][0] - camera_x * 0.5, GROUND_Y))
        pygame.draw.polygon(screen, (120, 120, 120), mountain_poly)
        for px, py in mountain_points:
            pygame.draw.polygon(screen, (255, 255, 255), [
                (px - 20 - camera_x * 0.5, py + 20),
                (px + 20 - camera_x * 0.5, py + 20),
                (px - camera_x * 0.5, py)
            ])

        # Clouds
        for cloud in clouds:
            cx = cloud[0] - camera_x * cloud[3]
            pygame.draw.ellipse(screen, (255, 255, 255), (cx, cloud[1], cloud[2], cloud[2] // 2))
            cloud[0] += 0.2

        # Trees
        for tree in trees:
            tx = tree[0] - camera_x
            pygame.draw.rect(screen, (101, 67, 33), (tx + tree[2]//2, tree[1]+50, 15, 50))
            pygame.draw.ellipse(screen, (34, 139, 34), (tx, tree[1], tree[2], tree[2]))

        # Grass
        for i in range(3):
            pygame.draw.rect(screen, (50 + i*20, 180 + i*10, 50), (0, GROUND_Y + i*10, WIDTH, HEIGHT - GROUND_Y))

        # Flowers
        for flower in flowers:
            fx = flower[0] - camera_x
            pygame.draw.circle(screen, flower[2], (fx, flower[1] - 5), 5)

        # Platforms
        for plat in platforms:
            pygame.draw.rect(screen, plat[4], (plat[0] - camera_x, plat[1], plat[2], plat[3]), border_radius=8)

        # Birds
        for bird in birds:
            bx = bird[0] - camera_x
            pygame.draw.polygon(screen, (0, 0, 0), [(bx, bird[1]), (bx+10*bird[2], bird[1]+5), (bx, bird[1]+2)])
            bird[0] += bird[2]

        # Egg
        screen.blit(egg, (egg_x - camera_x, egg_y))

        # Dino
        screen.blit(dino, (dino_x - camera_x, dino_y))

        # Player
        screen.blit(man, (state["man_x"] - camera_x, state["man_y"]))

        # Rocks
        for rock in state["rocks"]:
            screen.blit(rock_img, (rock[0] - camera_x, rock[1]))

        # Collisions
        if man_rect.colliderect(get_dino_hitbox(dino_x, dino_y)) or any(man_rect.colliderect(get_rock_hitbox(r)) for r in state["rocks"]):
            state["game_state"] = "lost"
        if man_rect.colliderect(get_egg_hitbox()):
            state["game_state"] = "won"

        # Score display in-game
        show_text(f"Distance: {int((state['score']/state['max_distance'])*100)}%", (255, 255, 255), 10, big=False, x=10)

    else:
        # End screen
        screen.fill((0, 0, 0))
        distance_covered = max(0, min(state["man_x"], state["max_distance"]))
        percentage = int((distance_covered/state["max_distance"])*100)

        line_spacing = 60
        start_y = HEIGHT // 2 - 90

        if state["game_state"] == "won":
            show_text("YOU WON 🎉", (0,255,0), start_y, big=True)
            show_text("You collected the egg!", (255,255,0), start_y + line_spacing)
            show_text(f"Distance Covered: 100%", (255, 255, 255), start_y + 2*line_spacing)
        else:
            show_text("GAME OVER 💀", (255,0,0), start_y, big=True)
            show_text(f"Distance Covered: {percentage}%", (255, 255, 255), start_y + line_spacing)

        show_text("Press R to Restart", (255,255,255), start_y + 3*line_spacing)

        if keys[pygame.K_r]:
            state = reset_game()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
