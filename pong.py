import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
FPS = 60
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
BALL_SIZE = 10
PADDLE_SPEED = 6
BALL_SPEED = 5
MAX_BALL_SPEED = 12

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

class Paddle:
    """Player and Computer paddles"""
    def __init__(self, x, y, is_player=True):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.is_player = is_player
        self.speed = PADDLE_SPEED
        self.color = CYAN if is_player else MAGENTA
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
    
    def move_up(self):
        if self.rect.top > 0:
            self.rect.y -= self.speed
    
    def move_down(self):
        if self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed
    
    def clamp(self):
        """Keep paddle within screen bounds"""
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - PADDLE_HEIGHT))

class Ball:
    """Game ball with physics"""
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, 
                                SCREEN_HEIGHT // 2 - BALL_SIZE // 2, 
                                BALL_SIZE, BALL_SIZE)
        self.vx = BALL_SPEED * 0.7
        self.vy = BALL_SPEED * 0.7
        self.color = YELLOW
        self.speed = BALL_SPEED
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.circle(screen, YELLOW, self.rect.center, BALL_SIZE // 2)
    
    def update(self):
        """Update ball position"""
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        # Bounce off top and bottom walls
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.vy *= -1
            self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - BALL_SIZE))
    
    def reset(self, direction=1):
        """Reset ball to center"""
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = BALL_SPEED
        angle = math.radians(30)
        self.vx = math.cos(angle) * self.speed * direction
        self.vy = (math.sin(angle) * self.speed) * (1 if direction > 0 else -1)
    
    def increase_speed(self):
        """Gradually increase ball speed on paddle hits"""
        self.speed = min(self.speed + 0.5, MAX_BALL_SPEED)
    
    def check_paddle_collision(self, paddle):
        """Check and handle collision with paddle"""
        if not self.rect.colliderect(paddle.rect):
            return False
        
        # Determine collision side
        if self.vx > 0:  # Moving right (hit right paddle)
            self.rect.right = paddle.rect.left
            self.vx *= -1
        else:  # Moving left (hit left paddle)
            self.rect.left = paddle.rect.right
            self.vx *= -1
        
        # Add spin based on paddle position
        hit_pos = (self.rect.centery - paddle.rect.centery) / (PADDLE_HEIGHT / 2)
        hit_pos = max(-1, min(1, hit_pos))
        self.vy += hit_pos * 3
        
        # Increase speed
        self.increase_speed()
        
        # Clamp velocity
        speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if speed > MAX_BALL_SPEED:
            self.vx = (self.vx / speed) * MAX_BALL_SPEED
            self.vy = (self.vy / speed) * MAX_BALL_SPEED
        
        return True

class PongGame:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pong Game - Python Edition")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_small = pygame.font.Font(None, 36)
        
        # Game objects
        self.player_paddle = Paddle(30, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, is_player=True)
        self.computer_paddle = Paddle(SCREEN_WIDTH - 30 - PADDLE_WIDTH, 
                                     SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2, is_player=False)
        self.ball = Ball()
        
        # Game state
        self.score_player = 0
        self.score_computer = 0
        self.game_running = True
        self.game_paused = False
        self.game_started = False
    
    def handle_events(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_started:
                        self.game_started = True
                    else:
                        self.game_paused = not self.game_paused
                if event.key == pygame.K_r:
                    self.reset_game()
                if event.key == pygame.K_ESCAPE:
                    return False
        
        # Continuous key checks for paddle movement
        if self.game_started and not self.game_paused:
            keys = pygame.key.get_pressed()
            
            # Player paddle - Arrow keys
            if keys[pygame.K_UP]:
                self.player_paddle.move_up()
            if keys[pygame.K_DOWN]:
                self.player_paddle.move_down()
        
        return True
    
    def update_ai(self):
        """Update computer AI"""
        if not self.game_started or self.game_paused:
            return
        
        # Simple AI: follow the ball
        ai_center = self.computer_paddle.rect.centery
        ball_center = self.ball.rect.centery
        
        # Add some tolerance (dead zone) for more human-like behavior
        dead_zone = 35
        
        if ball_center < ai_center - dead_zone:
            self.computer_paddle.move_up()
        elif ball_center > ai_center + dead_zone:
            self.computer_paddle.move_down()
        
        self.computer_paddle.clamp()
    
    def update(self):
        """Update game logic"""
        if not self.game_started or self.game_paused:
            return
        
        # Update ball
        self.ball.update()
        
        # Check paddle collisions
        self.ball.check_paddle_collision(self.player_paddle)
        self.ball.check_paddle_collision(self.computer_paddle)
        
        # Check if ball went out of bounds (scoring)
        if self.ball.rect.left <= 0:
            self.score_computer += 1
            self.ball.reset(direction=1)
        elif self.ball.rect.right >= SCREEN_WIDTH:
            self.score_player += 1
            self.ball.reset(direction=-1)
    
    def draw(self):
        """Draw game elements"""
        self.screen.fill(BLACK)
        
        # Draw center line
        for y in range(0, SCREEN_HEIGHT, 15):
            pygame.draw.line(self.screen, WHITE, 
                           (SCREEN_WIDTH // 2, y), 
                           (SCREEN_WIDTH // 2, y + 10), 2)
        
        # Draw paddles
        self.player_paddle.draw(self.screen)
        self.computer_paddle.draw(self.screen)
        
        # Draw ball
        self.ball.draw(self.screen)
        
        # Draw scores
        score_text = self.font_large.render(f"{self.score_player}  {self.score_computer}", 
                                           True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(score_text, score_rect)
        
        # Draw labels
        player_label = self.font_small.render("PLAYER", True, CYAN)
        computer_label = self.font_small.render("COMPUTER", True, MAGENTA)
        self.screen.blit(player_label, (50, 50))
        self.screen.blit(computer_label, (SCREEN_WIDTH - 300, 50))
        
        # Draw instructions
        if not self.game_started:
            start_text = self.font_small.render("Press SPACE to START", True, GREEN)
            start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(start_text, start_rect)
        
        if self.game_paused:
            pause_text = self.font_large.render("PAUSED", True, YELLOW)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(pause_text, pause_rect)
        
        # Draw help text
        help_text = self.font_small.render("UP/DOWN: Move | SPACE: Pause | R: Reset | ESC: Quit", 
                                          True, WHITE)
        help_rect = help_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(help_text, help_rect)
        
        pygame.display.flip()
    
    def reset_game(self):
        """Reset game to initial state"""
        self.score_player = 0
        self.score_computer = 0
        self.game_started = False
        self.game_paused = False
        self.player_paddle.rect.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.computer_paddle.rect.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.ball.reset()
    
    def run(self):
        """Main game loop"""
        while self.game_running:
            if not self.handle_events():
                self.game_running = False
                break
            
            self.update_ai()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = PongGame()
    game.run()
