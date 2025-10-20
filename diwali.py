import pygame
import random
import math

# --- Diwali Fireworks with Music ---
# To enable music, place a file named 'diwali_bgm.mp3' or 'diwali_bgm.ogg' in the same folder as this script.
# Music will auto-play and can be toggled with the S key.

# --- Pygame Setup ---
pygame.init()

# --- Music Setup ---
import os
from pygame import mixer
mixer.init()
MUSIC_FILE = None
for fname in ["jethalal-sings-happy-diwali-taarak-mehta-ka-oolta-chashmah-happ-made-with-Voicemod.mp3", "diwali_bgm.ogg"]:
    if os.path.exists(fname):
        MUSIC_FILE = fname
        break
if MUSIC_FILE:
    mixer.music.load(MUSIC_FILE)
    mixer.music.set_volume(0.5)
    mixer.music.play(-1)
    MUSIC_ON = True
else:
    MUSIC_ON = False

# Constants
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Happy Diwali Fireworks!")
CLOCK = pygame.time.Clock()
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FIREWORK_COLORS = [
    (255, 100, 0),  # Bright Orange (Deepak/Fire)
    (0, 255, 255),  # Cyan
    (255, 0, 255),  # Magenta
    (255, 255, 0),  # Yellow/Gold
    (50, 255, 50),  # Light Green
    (100, 100, 255), # Light Blue
]

# Global impact value set when a firework explodes; stars react to this briefly
FIREWORK_IMPACT = 0.0

# Fonts
FONT_LARGE = pygame.font.Font(None, 74)
FONT_MEDIUM = pygame.font.Font(None, 36)

# --- Particle Class for Firework Sparks ---
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, velocity, gravity, lifetime):
        super().__init__()
        self.pos = pygame.Vector2(x, y)
        self.vel = velocity
        self.color = color
        self.gravity = gravity
        self.lifetime = lifetime
        self.start_lifetime = lifetime
        self.radius = 2

    def update(self):
        # Apply gravity
        self.vel.y += self.gravity
        # Update position
        self.pos += self.vel
        # Decrease lifetime (fade effect)
        self.lifetime -= 1
    
    def draw(self, screen):
        # Calculate alpha based on remaining lifetime for fade effect
        if self.start_lifetime > 0:
            alpha = int(255 * (self.lifetime / self.start_lifetime))
        else:
            alpha = 0

        # Clamp alpha to 0..255
        alpha = max(0, min(255, alpha))

        # Create a surface for the particle with alpha channel
        particle_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)

        # Ensure color is a 3-tuple and draw using RGBA tuple with our computed alpha
        color_rgb = (
            max(0, min(255, int(self.color[0]))),
            max(0, min(255, int(self.color[1]))),
            max(0, min(255, int(self.color[2])))
        )
        color_rgba = (*color_rgb, alpha)

        pygame.draw.circle(particle_surface, color_rgba, (self.radius, self.radius), self.radius)

        # Blit the particle surface to the screen
        screen.blit(particle_surface, self.pos - pygame.Vector2(self.radius, self.radius))

# --- Firework Class (Rocket and Explosion Manager) ---
class Firework(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.particles = pygame.sprite.Group()
        self.exploded = False
        self.color = random.choice(FIREWORK_COLORS)
        
        # Rocket start position (bottom center)
        self.pos = pygame.Vector2(random.randint(WIDTH // 4, WIDTH * 3 // 4), HEIGHT)
        # Rocket velocity (slowly upward)
        self.vel = pygame.Vector2(0, random.uniform(-10, -16))
        
        # Explosion height (randomly selected)
        self.explosion_y = random.randint(HEIGHT // 5, HEIGHT // 2)

    def explode(self):
        global FIREWORK_IMPACT
        self.exploded = True
        num_particles = random.randint(30, 80)
        
        # Create particles radiating outwards
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            
            # Use random variation on the firework color
            # Clamp color components to valid 0-255 range to avoid invalid color errors
            p_color = (
                max(0, min(255, self.color[0] + random.randint(-50, 50))),
                max(0, min(255, self.color[1] + random.randint(-50, 50))),
                max(0, min(255, self.color[2] + random.randint(-50, 50)))
            )
            
            velocity = pygame.Vector2(speed * math.cos(angle), speed * math.sin(angle))
            gravity = 0.1
            lifetime = random.randint(30, 80)
            
            particle = Particle(self.pos.x, self.pos.y, p_color, velocity, gravity, lifetime)
            self.particles.add(particle)
        # Increase impact so background stars get a small drift effect
        FIREWORK_IMPACT += 1.0

    def update(self):
        if not self.exploded:
            # Rocket phase
            self.pos += self.vel
            if self.pos.y <= self.explosion_y:
                self.explode()
        
        # Update particles if exploded
        if self.exploded:
            self.particles.update()
            # Remove the firework if all its particles are gone
            if not self.particles:
                self.kill() # Removes the firework sprite from all groups
    
    def draw(self, screen):
        if not self.exploded:
            # Draw the rising rocket (simple dot)
            pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), 3)
        else:
            # Draw all particles
            for particle in self.particles:
                particle.draw(screen)


# --- Additional Effects: Fountain and RoundCracker ---
class Fountain:
    """A ground fountain that emits continuous upward spark particles."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles = []
        self.alive = True

    def update(self):
        # emit a few particles each frame
        for _ in range(2):
            vx = random.uniform(-1.5, 1.5)
            vy = random.uniform(-6.0, -3.0)
            color = random.choice(FIREWORK_COLORS)
            # small lifetime for fountain sparks
            p = Particle(self.x, self.y, color, pygame.Vector2(vx, vy), 0.12, random.randint(20, 45))
            p.radius = random.randint(1, 3)
            self.particles.append(p)

        # update particles
        for p in self.particles:
            p.update()
        # remove dead
        self.particles = [p for p in self.particles if p.lifetime > 0]
        # fountain persists for a while; if no particles and external logic wants to remove, handle elsewhere

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)


class RoundCracker:
    """A round cracker: small ground burst producing a circular explosion."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles = []
        self._create_burst()

    def _create_burst(self):
        num = random.randint(40, 100)
        base_color = random.choice(FIREWORK_COLORS)
        for _ in range(num):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.5, 6.5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = (
                max(0, min(255, base_color[0] + random.randint(-40, 40))),
                max(0, min(255, base_color[1] + random.randint(-40, 40))),
                max(0, min(255, base_color[2] + random.randint(-40, 40)))
            )
            p = Particle(self.x, self.y, color, pygame.Vector2(vx, vy), 0.12, random.randint(25, 70))
            p.radius = random.randint(1, 3)
            self.particles.append(p)

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.lifetime > 0]

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)


# --- Parallax Star Background ---
class Star:
    def __init__(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT - 100)
        # smaller stars are further away and move less
        self.layer = random.choice([0.3, 0.6, 1.0])
        shade = random.randint(180, 255)
        self.color = (shade, shade, shade)
        self.radius = 1 if self.layer < 0.6 else 2

    def update(self):
        pass

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


# --- Diwali Environment Drawing ---
def draw_environment(screen):
    # Draw ground strip (assumes background/stars already drawn)
    pygame.draw.rect(screen, (10, 8, 6), (0, HEIGHT - 80, WIDTH, 80))

    # Draw diyas evenly spaced across the bottom
    diya_count = 9
    spacing = WIDTH // (diya_count + 1)
    for i in range(1, diya_count + 1):
        x = i * spacing
        y = HEIGHT - 40
        draw_diya(screen, x, y)


def draw_text(screen):
    # Sliding animated text: we'll animate its Y position via a global
    global text_target_y, text_current_y
    if 'text_target_y' not in globals():
        text_target_y = HEIGHT // 8
        text_current_y = HEIGHT + 50  # start below the screen

    # ease the text upward
    text_current_y -= (text_current_y - text_target_y) * 0.035

    # Render the main message
    text_surface = FONT_LARGE.render("Happy Diwali!", True, WHITE)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, int(text_current_y)))

    # Shadow effect
    shadow_color = (100, 100, 100)
    shadow_surface = FONT_LARGE.render("Happy Diwali!", True, shadow_color)
    screen.blit(shadow_surface, text_rect.move(2, 2))

    # Main text
    screen.blit(text_surface, text_rect)


def draw_diya(screen, x, y):
    """Draw a stylized diya (lamp) at (x, y) where y is the top of the base."""
    # base (clay)
    base_rect = pygame.Rect(int(x - 18), int(y - 6), 36, 12)
    pygame.draw.ellipse(screen, (90, 50, 20), base_rect)

    # oil pool
    pygame.draw.ellipse(screen, (200, 120, 30), (base_rect.x + 6, base_rect.y + 2, 24, 6))

    # flame
    t = pygame.time.get_ticks() / 250.0
    flame_h = 12 + math.sin(t + x * 0.01) * 3
    flame_color = (255, 200, 60)
    flame_points = [(x, y - flame_h), (x - 6, y + 2), (x + 6, y + 2)]
    pygame.draw.polygon(screen, flame_color, flame_points)


# --- Main Game Loop ---
def run_game():
    fireworks = pygame.sprite.Group()
    fountains = []
    round_crackers = []
    running = True

    # Initialize star field for parallax background
    stars = [Star() for _ in range(90)]

    # Timer for spawning new fireworks
    last_firework_time = pygame.time.get_ticks()
    firework_interval = 500  # milliseconds between fireworks (start fast)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # Launch a manual firework on spacebar press
                fireworks.add(Firework())
            # Spawn fountain with F key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                x = random.randint(80, WIDTH - 80)
                fountains.append(Fountain(x, HEIGHT - 44))
            # Spawn round cracker with R key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                x = random.randint(80, WIDTH - 80)
                round_crackers.append(RoundCracker(x, HEIGHT - 44))
            # Toggle music with S key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                global MUSIC_ON
                if MUSIC_FILE:
                    if MUSIC_ON:
                        mixer.music.pause()
                        MUSIC_ON = False
                    else:
                        mixer.music.unpause()
                        MUSIC_ON = True

        # Automatic Firework Spawning
        current_time = pygame.time.get_ticks()
        if current_time - last_firework_time > firework_interval:
            fireworks.add(Firework())
            last_firework_time = current_time
            # Slowly increase the interval (slow down the spam)
            firework_interval = min(2000, firework_interval + 20)


        # --- Update ---
        fireworks.update()
        for f in fountains:
            f.update()
        for r in round_crackers:
            r.update()

        # Update stars (no scrolling)
        for s in stars:
            s.update()

        # --- Draw ---
        # Draw background environment (stars drawn first)
        # Clear background
        SCREEN.fill(BLACK)
        for s in stars:
            s.draw(SCREEN)

        # Draw environment (ground, diyas)
        draw_environment(SCREEN)
        
        # Draw all active fireworks (rockets and explosions)
        for fw in fireworks:
            fw.draw(SCREEN)

        # Draw fountains and round crackers
        for f in fountains:
            f.draw(SCREEN)
        for r in round_crackers:
            r.draw(SCREEN)

        draw_text(SCREEN)

        # Update the full display
        pygame.display.flip()

        # Cap the framerate
        CLOCK.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    run_game()
