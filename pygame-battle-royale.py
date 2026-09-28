import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Game Window Setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Free Fire - Python Mini Clone")
clock = pygame.time.Clock()

# Colors
BG_GREEN = (34, 139, 34)      # Map grass
ZONE_COLOR = (0, 0, 255)      # Blue zone border
PLAYER_BLUE = (0, 191, 255)
ENEMY_RED = (220, 20, 60)
BULLET_YELLOW = (255, 215, 0)
WHITE = (255, 255, 255)

# Game Variables
score = 0
player_health = 100
game_over = False

# Safe Zone / Play Zone System
zone_radius = 450
zone_center = [WIDTH // 2, HEIGHT // 2]
zone_shrink_speed = 0.15

# Player Class
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 15
        self.speed = 4

    def move(self, keys):
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  self.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.x += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:    self.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  self.y += self.speed

    def draw(self):
        pygame.draw.circle(screen, PLAYER_BLUE, (int(self.x), int(self.y)), self.radius)

# Bullet Class
class Bullet:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.radius = 4
        self.speed = 10
        
        # Calculate direction towards mouse pointer
        angle = math.atan2(target_y - y, target_x - x)
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        pygame.draw.circle(screen, BULLET_YELLOW, (int(self.x), int(self.y)), self.radius)

# Enemy Class
class Enemy:
    def __init__(self):
        # Spawn randomly outside the screen but within boundaries
        angle = random.uniform(0, 2 * math.pi)
        distance = random.randint(400, 600)
        self.x = zone_center[0] + math.cos(angle) * distance
        self.y = zone_center[1] + math.sin(angle) * distance
        self.radius = 12
        self.speed = random.uniform(1.5, 3.0)

    def update(self, p_x, p_y):
        # Hunt and track the player path
        angle = math.atan2(p_y - self.y, p_x - self.x)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed

    def draw(self):
        pygame.draw.circle(screen, ENEMY_RED, (int(self.x), int(self.y)), self.radius)

# Instantiate objects
player = Player()
bullets = []
enemies = []

# Enemy spawning timer
SPAWN_ENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ENEMY, 1200) # Spawns an enemy every 1.2 seconds

# Font Setup
font = pygame.font.SysFont("Arial", 24)

# Main Game Loop
while True:
    screen.fill(BG_GREEN)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if not game_over:
            if event.type == SPAWN_ENEMY:
                enemies.append(Enemy())
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Shoot a bullet towards mouse click location
                mx, my = pygame.mouse.get_pos()
                bullets.append(Bullet(player.x, player.y, mx, my))
                
        else:
            # Restart game on pressing 'R' key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                player = Player()
                bullets, enemies = [], []
                score = 0
                player_health = 100
                zone_radius = 450
                game_over = False

    if not game_over:
        # 1. Shrink the Playable Safe Zone (Simulating the Battle Royale Circle)
        if zone_radius > 50:
            zone_radius -= zone_shrink_speed
            
        # 2. Player Input Movement
        keys = pygame.key.get_pressed()
        player.move(keys)
        
        # Check if player is outside the safe blue zone (takes damage over time)
        dist_from_center = math.hypot(player.x - zone_center[0], player.y - zone_center[1])
        if dist_from_center > zone_radius:
            player_health -= 0.4  # Damage ticks out of the zone

        # 3. Update Bullets
        for b in bullets[:]:
            b.update()
            # Remove bullet if it goes off screen
            if b.x < 0 or b.x > WIDTH or b.y < 0 or b.y > HEIGHT:
                bullets.remove(b)

        # 4. Update Enemies & Check Collisions
        for e in enemies[:]:
            e.update(player.x, player.y)
            
            # Enemy hits player
            dist_to_player = math.hypot(e.x - player.x, e.y - player.y)
            if dist_to_player < (e.radius + player.radius):
                player_health -= 15
                enemies.remove(e)
                continue
                
            # Bullet hits enemy
            for b in bullets[:]:
                dist_to_bullet = math.hypot(e.x - b.x, e.y - b.y)
                if dist_to_bullet < (e.radius + b.radius):
                    score += 1
                    if e in enemies: enemies.remove(e)
                    if b in bullets: bullets.remove(b)

        # Health monitoring check
        if player_health <= 0:
            player_health = 0
            game_over = True

    # --- DRAWING EVERYTHING ---
    
    # Draw Safe Zone border
    pygame.draw.circle(screen, ZONE_COLOR, zone_center, int(zone_radius), 3)
    
    # Draw Game Elements
    player.draw()
    for b in bullets: b.draw()
    for e in enemies: e.draw()
    
    # HUD UI Text Displays
    health_txt = font.render(f"HP: {int(player_health)}", True, WHITE)
    score_txt = font.render(f"Kills: {score}", True, WHITE)
    screen.blit(health_txt, (20, 20))
    screen.blit(score_txt, (20, 50))
    
    if game_over:
        go_txt = font.render("ELIMINATED! Press 'R' to Respawn", True, WHITE)
        screen.blit(go_txt, (WIDTH//2 - 160, HEIGHT//2))

    pygame.display.flip()
    clock.tick(60)
