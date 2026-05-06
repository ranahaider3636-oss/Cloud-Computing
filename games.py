import pygame
import random
import math
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3

@dataclass
class Vector2:
    x: float
    y: float
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

class Weapon(Enum):
    PISTOL = 1
    RIFLE = 2
    SNIPER = 3

class Bullet:
    def __init__(self, x: float, y: float, angle: float, weapon: Weapon):
        self.pos = Vector2(x, y)
        self.angle = angle
        self.weapon = weapon
        
        # Set speed based on weapon
        if weapon == Weapon.PISTOL:
            self.speed = 8
            self.damage = 10
            self.radius = 3
        elif weapon == Weapon.RIFLE:
            self.speed = 12
            self.damage = 15
            self.radius = 4
        else:  # SNIPER
            self.speed = 15
            self.damage = 50
            self.radius = 5
        
        self.velocity = Vector2(
            math.cos(angle) * self.speed,
            math.sin(angle) * self.speed
        )
    
    def update(self):
        self.pos = self.pos + self.velocity
    
    def is_off_screen(self):
        return (self.pos.x < 0 or self.pos.x > SCREEN_WIDTH or
                self.pos.y < 0 or self.pos.y > SCREEN_HEIGHT)
    
    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (int(self.pos.x), int(self.pos.y)), self.radius)

class Item:
    def __init__(self, x: float, y: float, item_type: str):
        self.pos = Vector2(x, y)
        self.item_type = item_type  # "health", "ammo", "weapon"
        self.radius = 10
    
    def draw(self, surface):
        if self.item_type == "health":
            color = GREEN
        elif self.item_type == "ammo":
            color = BLUE
        else:  # weapon
            color = RED
        pygame.draw.rect(surface, color, (self.pos.x - self.radius, self.pos.y - self.radius,
                                          self.radius * 2, self.radius * 2))

class Player:
    def __init__(self, x: float, y: float):
        self.pos = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.radius = 15
        self.speed = 5
        self.max_health = 100
        self.health = self.max_health
        self.rotation = 0
        self.current_weapon = Weapon.PISTOL
        self.ammo = {Weapon.PISTOL: 100, Weapon.RIFLE: 60, Weapon.SNIPER: 20}
        self.score = 0
        self.alive = True
    
    def update(self, keys, mouse_pos):
        # Movement
        self.velocity = Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.velocity.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.velocity.y += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity.x += self.speed
        
        # Update position
        new_pos = self.pos + self.velocity
        
        # Boundary checking
        if 0 <= new_pos.x <= SCREEN_WIDTH:
            self.pos.x = new_pos.x
        if 0 <= new_pos.y <= SCREEN_HEIGHT:
            self.pos.y = new_pos.y
        
        # Rotation towards mouse
        self.rotation = math.atan2(mouse_pos[1] - self.pos.y, mouse_pos[0] - self.pos.x)
    
    def shoot(self) -> Bullet:
        if self.ammo[self.current_weapon] > 0:
            self.ammo[self.current_weapon] -= 1
            return Bullet(self.pos.x, self.pos.y, self.rotation, self.current_weapon)
        return None
    
    def take_damage(self, damage: int):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            self.health = 0
    
    def heal(self, amount: int):
        self.health = min(self.health + amount, self.max_health)
    
    def add_ammo(self, weapon: Weapon, amount: int):
        self.ammo[weapon] += amount
    
    def draw(self, surface):
        # Draw player body
        pygame.draw.circle(surface, BLUE, (int(self.pos.x), int(self.pos.y)), self.radius)
        
        # Draw player direction
        end_x = self.pos.x + math.cos(self.rotation) * (self.radius + 10)
        end_y = self.pos.y + math.sin(self.rotation) * (self.radius + 10)
        pygame.draw.line(surface, WHITE, (int(self.pos.x), int(self.pos.y)),
                        (int(end_x), int(end_y)), 2)
        
        # Draw health bar
        health_width = 30
        health_height = 5
        health_x = self.pos.x - health_width / 2
        health_y = self.pos.y - self.radius - 15
        
        pygame.draw.rect(surface, RED, (health_x, health_y, health_width, health_height))
        pygame.draw.rect(surface, GREEN, (health_x, health_y, 
                                          health_width * (self.health / self.max_health), health_height))

class Enemy:
    def __init__(self, x: float, y: float):
        self.pos = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.radius = 12
        self.speed = 2
        self.max_health = 50
        self.health = self.max_health
        self.rotation = 0
        self.target = None
        self.shoot_timer = 0
        self.shoot_cooldown = 60
    
    def update(self, player: Player, enemies: List['Enemy']):
        # AI: Move towards player
        direction = player.pos - self.pos
        distance = direction.distance_to(Vector2(0, 0))
        
        if distance > 0:
            self.velocity = Vector2(
                (direction.x / distance) * self.speed,
                (direction.y / distance) * self.speed
            )
        
        self.pos = self.pos + self.velocity
        self.rotation = math.atan2(direction.y, direction.x)
        
        # Boundary checking
        self.pos.x = max(0, min(SCREEN_WIDTH, self.pos.x))
        self.pos.y = max(0, min(SCREEN_HEIGHT, self.pos.y))
        
        self.shoot_timer -= 1
    
    def take_damage(self, damage: int):
        self.health -= damage
        return self.health <= 0
    
    def can_shoot(self) -> bool:
        return self.shoot_timer <= 0
    
    def shoot(self) -> Bullet:
        if self.can_shoot():
            self.shoot_timer = self.shoot_cooldown
            return Bullet(self.pos.x, self.pos.y, self.rotation + random.uniform(-0.2, 0.2), Weapon.PISTOL)
        return None
    
    def draw(self, surface):
        # Draw enemy body
        pygame.draw.circle(surface, RED, (int(self.pos.x), int(self.pos.y)), self.radius)
        
        # Draw enemy direction
        end_x = self.pos.x + math.cos(self.rotation) * (self.radius + 8)
        end_y = self.pos.y + math.sin(self.rotation) * (self.radius + 8)
        pygame.draw.line(surface, WHITE, (int(self.pos.x), int(self.pos.y)),
                        (int(end_x), int(end_y)), 2)
        
        # Draw health bar
        health_width = 25
        health_height = 4
        health_x = self.pos.x - health_width / 2
        health_y = self.pos.y - self.radius - 12
        
        pygame.draw.rect(surface, RED, (health_x, health_y, health_width, health_height))
        pygame.draw.rect(surface, GREEN, (health_x, health_y,
                                          health_width * (self.health / self.max_health), health_height))

class SafeZone:
    def __init__(self, center_x: float, center_y: float, radius: float):
        self.center = Vector2(center_x, center_y)
        self.radius = radius
        self.shrink_rate = 0.3
        self.damage_per_frame = 0.5
    
    def shrink(self):
        if self.radius > 20:
            self.radius -= self.shrink_rate
    
    def is_inside(self, pos: Vector2) -> bool:
        return self.center.distance_to(pos) <= self.radius
    
    def draw(self, surface):
        pygame.draw.circle(surface, GREEN, (int(self.center.x), int(self.center.y)),
                          int(self.radius), 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Battle Royale - PUBG Style")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.state = GameState.MENU
        self.init_game()
    
    def init_game(self):
        self.player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.enemies: List[Enemy] = []
        self.bullets: List[Bullet] = []
        self.items: List[Item] = []
        self.safe_zone = SafeZone(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 300)
        
        # Spawn initial enemies
        for _ in range(5):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            self.enemies.append(Enemy(x, y))
        
        # Spawn initial items
        for _ in range(10):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            item_type = random.choice(["health", "ammo", "weapon"])
            self.items.append(Item(x, y, item_type))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.PLAYING
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_1:
                        self.player.current_weapon = Weapon.PISTOL
                    elif event.key == pygame.K_2:
                        self.player.current_weapon = Weapon.RIFLE
                    elif event.key == pygame.K_3:
                        self.player.current_weapon = Weapon.SNIPER
                    elif event.key == pygame.K_r:
                        self.player.ammo[self.player.current_weapon] = 999
                
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.MENU
                        self.init_game()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == GameState.PLAYING and event.button == 1:
                    bullet = self.player.shoot()
                    if bullet:
                        self.bullets.append(bullet)
        
        return True
    
    def update(self):
        if self.state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            
            # Update player
            self.player.update(keys, mouse_pos)
            
            # Update enemies
            for enemy in self.enemies[:]:
                enemy.update(self.player, self.enemies)
                
                # Enemy shooting
                bullet = enemy.shoot()
                if bullet:
                    self.bullets.append(bullet)
                
                # Remove dead enemies
                if enemy.health <= 0:
                    self.enemies.remove(enemy)
                    self.player.score += 100
                    # Spawn new enemy
                    x = random.randint(50, SCREEN_WIDTH - 50)
                    y = random.randint(50, SCREEN_HEIGHT - 50)
                    self.enemies.append(Enemy(x, y))
            
            # Update bullets
            for bullet in self.bullets[:]:
                bullet.update()
                
                # Check collisions with player
                dist_to_player = bullet.pos.distance_to(self.player.pos)
                if dist_to_player < self.player.radius + bullet.radius:
                    self.player.take_damage(bullet.damage)
                    self.bullets.remove(bullet)
                    continue
                
                # Check collisions with enemies
                hit_enemy = False
                for enemy in self.enemies:
                    dist_to_enemy = bullet.pos.distance_to(enemy.pos)
                    if dist_to_enemy < enemy.radius + bullet.radius:
                        if enemy.take_damage(bullet.damage):
                            self.enemies.remove(enemy)
                            self.player.score += 100
                            # Spawn new enemy
                            x = random.randint(50, SCREEN_WIDTH - 50)
                            y = random.randint(50, SCREEN_HEIGHT - 50)
                            self.enemies.append(Enemy(x, y))
                        hit_enemy = True
                        break
                
                if hit_enemy and bullet in self.bullets:
                    self.bullets.remove(bullet)
                elif bullet.is_off_screen() and bullet in self.bullets:
                    self.bullets.remove(bullet)
            
            # Check item collisions
            for item in self.items[:]:
                dist = item.pos.distance_to(self.player.pos)
                if dist < self.player.radius + item.radius:
                    if item.item_type == "health":
                        self.player.heal(30)
                        self.player.score += 10
                    elif item.item_type == "ammo":
                        self.player.add_ammo(Weapon.RIFLE, 30)
                        self.player.score += 10
                    elif item.item_type == "weapon":
                        self.player.add_ammo(Weapon.SNIPER, 10)
                        self.player.score += 50
                    self.items.remove(item)
            
            # Safe zone logic
            self.safe_zone.shrink()
            if not self.safe_zone.is_inside(self.player.pos):
                self.player.take_damage(self.safe_zone.damage_per_frame)
            
            # Check game over
            if not self.player.alive:
                self.state = GameState.GAME_OVER
    
    def draw(self):
        self.screen.fill(DARK_GRAY)
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_menu(self):
        title = self.font.render("BATTLE ROYALE", True, WHITE)
        subtitle = self.small_font.render("Press SPACE to Start", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
    
    def draw_game(self):
        # Draw safe zone
        self.safe_zone.draw(self.screen)
        
        # Draw items
        for item in self.items:
            item.draw(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw HUD
        self.draw_hud()
    
    def draw_hud(self):
        # Health
        health_text = self.small_font.render(f"Health: {int(self.player.health)}", True, GREEN)
        self.screen.blit(health_text, (10, 10))
        
        # Score
        score_text = self.small_font.render(f"Score: {self.player.score}", True, YELLOW)
        self.screen.blit(score_text, (10, 40))
        
        # Weapon and ammo
        weapon_name = self.player.current_weapon.name
        ammo_count = self.player.ammo[self.player.current_weapon]
        weapon_text = self.small_font.render(f"Weapon: {weapon_name} ({ammo_count})", True, WHITE)
        self.screen.blit(weapon_text, (10, 70))
        
        # Controls
        controls = [
            "WASD: Move | Mouse: Aim | Click: Shoot",
            "1/2/3: Change Weapon | R: Refill Ammo"
        ]
        for i, control in enumerate(controls):
            control_text = self.small_font.render(control, True, GRAY)
            self.screen.blit(control_text, (10, SCREEN_HEIGHT - 60 + i * 25))
        
        # Enemies remaining
        enemies_text = self.small_font.render(f"Enemies: {len(self.enemies)}", True, RED)
        self.screen.blit(enemies_text, (SCREEN_WIDTH - 200, 10))
    
    def draw_game_over(self):
        self.draw_game()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Final Score: {self.player.score}", True, YELLOW)
        restart_text = self.small_font.render("Press SPACE to Return to Menu", True, WHITE)
        
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                                         SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2,
                                      SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                                        SCREEN_HEIGHT // 2 + 60))
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
