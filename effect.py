"""
Neon particle heart over scrolling Python code.

Install and run:
    python -m pip install pygame
    python neon_heart_code.py

Controls:
    ESC  quit
    SPACE pause/resume
    R    rebuild the particles
    S    save the complete frame
    T    save the transparent heart layer only
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path

import pygame


WIDTH, HEIGHT = 1280, 720
FPS = 60
HEART_CENTER = pygame.Vector2(WIDTH * 0.58, HEIGHT * 0.50)
HEART_SCALE = 15.2
PARTICLE_COUNT = 1750
BACKGROUND = (5, 7, 12)
PINK = (255, 34, 150)

CODE = '''
import math
import random
from dataclasses import dataclass

@dataclass
class Particle:
    position: Vector2
    velocity: Vector2
    brightness: float = 1.0

def heart(t: float) -> tuple[float, float]:
    x = 16 * math.sin(t) ** 3
    y = (13 * math.cos(t)
         - 5 * math.cos(2 * t)
         - 2 * math.cos(3 * t)
         - math.cos(4 * t))
    return x, -y

def breathe(time: float) -> float:
    slow_pulse = math.sin(time * 1.35)
    secondary = math.sin(time * 2.70 + 0.7)
    return 1.0 + slow_pulse * 0.045 + secondary * 0.010

def update_particles(particles, dt, time):
    for particle in particles:
        direction = target - particle.position
        particle.velocity += direction * dt * 0.8
        particle.velocity *= 0.965
        particle.position += particle.velocity * dt

def render_glow(layer, particles):
    # Multiple translucent passes create a soft neon bloom.
    draw_particles(layer, particles, radius=14, alpha=10)
    draw_particles(layer, particles, radius=7, alpha=26)
    draw_particles(layer, particles, radius=2, alpha=230)

if __name__ == "__main__":
    while running:
        clock.tick(60)
        update_particles(particles, dt, time)
        render_glow(transparent_heart_layer, particles)
        screen.blit(code_background, (0, 0))
        screen.blit(transparent_heart_layer, (0, 0))
        pygame.display.flip()
'''.strip().splitlines()


@dataclass
class Particle:
    base: pygame.Vector2
    position: pygame.Vector2
    velocity: pygame.Vector2
    size: float
    phase: float
    brightness: float
    kind: int


def heart_point(t: float) -> pygame.Vector2:
    x = 16.0 * math.sin(t) ** 3
    y = 13.0 * math.cos(t) - 5.0 * math.cos(2 * t)
    y -= 2.0 * math.cos(3 * t) + math.cos(4 * t)
    return pygame.Vector2(x, -y)


def random_point_in_heart() -> pygame.Vector2:
    # A boundary point multiplied by sqrt(r) produces a dense filled heart.
    edge = heart_point(random.random() * math.tau)
    radius = math.sqrt(random.random())
    point = edge * radius
    point.x += random.gauss(0, 0.18)
    point.y += random.gauss(0, 0.18)
    return point


def make_particles() -> list[Particle]:
    particles: list[Particle] = []
    for _ in range(PARTICLE_COUNT):
        base = random_point_in_heart()
        # Start near the heart, so the opening feels like fragments condensing.
        angle = random.random() * math.tau
        distance = random.uniform(5, 95)
        start = HEART_CENTER + base * HEART_SCALE
        start += pygame.Vector2(math.cos(angle), math.sin(angle)) * distance
        kind = 2 if random.random() < 0.035 else (1 if random.random() < 0.15 else 0)
        particles.append(
            Particle(
                base=base,
                position=start,
                velocity=pygame.Vector2(random.uniform(-8, 8), random.uniform(-8, 8)),
                size=random.uniform(0.7, 2.1) if kind == 0 else random.uniform(1.4, 3.4),
                phase=random.random() * math.tau,
                brightness=random.uniform(0.55, 1.0),
                kind=kind,
            )
        )
    return particles


def code_color(line: str) -> tuple[int, int, int]:
    stripped = line.strip()
    if stripped.startswith("#"):
        return (55, 105, 92)
    if stripped.startswith(("def ", "class ", "@")):
        return (96, 148, 190)
    if any(word in stripped for word in ("import ", "from ", "return ", "while ", "for ", "if ")):
        return (127, 103, 163)
    if '"' in line or "'" in line:
        return (142, 119, 80)
    return (76, 91, 110)


def draw_code_background(
    target: pygame.Surface,
    font: pygame.font.Font,
    scroll: float,
) -> None:
    target.fill(BACKGROUND)
    line_h = font.get_linesize() + 5
    cycle_h = len(CODE) * line_h
    y0 = -scroll % cycle_h - cycle_h

    # Very subtle vertical blue-magenta ambience behind the text.
    ambient = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(ambient, (26, 20, 54, 28), (int(WIDTH * .66), int(HEIGHT * .47)), 380)
    target.blit(ambient, (0, 0))

    for repeat in range(3):
        for index, line in enumerate(CODE):
            y = y0 + repeat * cycle_h + index * line_h
            if -line_h < y < HEIGHT:
                number = font.render(f"{index + 1:02d}", True, (38, 47, 59))
                text = font.render(line.replace("    ", "  "), True, code_color(line))
                target.blit(number, (44, y))
                target.blit(text, (88, y))

    # Dark veil keeps the heart dominant while code remains legible.
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    veil.fill((1, 3, 8, 50))
    target.blit(veil, (0, 0))


def update_particles(particles: list[Particle], time_s: float, dt: float) -> None:
    breath = 1.0 + math.sin(time_s * 1.30) * 0.047 + math.sin(time_s * 2.60 + 0.8) * 0.009
    formation = min(1.0, time_s / 2.8)
    ease = 1.0 - (1.0 - formation) ** 3

    for i, particle in enumerate(particles):
        # Microscopic turbulence prevents the filled heart from looking static.
        wobble = pygame.Vector2(
            math.sin(time_s * 1.7 + particle.phase) * 0.75,
            math.cos(time_s * 1.3 + particle.phase * 1.17) * 0.75,
        )
        target = HEART_CENTER + particle.base * HEART_SCALE * breath + wobble
        force = (target - particle.position) * (3.2 + ease * 5.0)
        particle.velocity += force * dt
        particle.velocity *= 0.90 ** (dt * 60.0)
        particle.position += particle.velocity * dt

        # A small subset peels off from the rim and then gets pulled back.
        if particle.kind == 2 and math.sin(time_s * 0.72 + particle.phase) > 0.92:
            particle.position.y -= 18.0 * dt
            particle.position.x += math.sin(time_s * 2.1 + i) * 7.0 * dt


def draw_heart_layer(layer: pygame.Surface, particles: list[Particle], time_s: float) -> None:
    """Draw only the effect. `layer` remains fully transparent elsewhere."""
    layer.fill((0, 0, 0, 0))
    glow_large = pygame.Surface(layer.get_size(), pygame.SRCALPHA)
    glow_small = pygame.Surface(layer.get_size(), pygame.SRCALPHA)

    # Soft breathing aura, drawn beneath the individual particles.
    pulse = 0.5 + 0.5 * math.sin(time_s * 1.3)
    aura_radius = int(176 + pulse * 14)
    for radius, alpha in ((aura_radius, 7), (125, 10), (82, 15)):
        pygame.draw.circle(glow_large, (255, 15, 142, alpha), HEART_CENTER, radius)

    for particle in particles:
        x, y = int(particle.position.x), int(particle.position.y)
        if not (-20 < x < WIDTH + 20 and -20 < y < HEIGHT + 20):
            continue
        flicker = 0.78 + 0.22 * math.sin(time_s * 4.0 + particle.phase)
        energy = max(0.25, particle.brightness * flicker)
        core = int(148 + 107 * energy)
        radius = max(1, int(particle.size))

        pygame.draw.circle(glow_large, (255, 18, 139, int(10 + 19 * energy)), (x, y), radius * 7 + 3)
        pygame.draw.circle(glow_small, (255, 26, 154, int(40 + 55 * energy)), (x, y), radius * 3 + 1)
        pygame.draw.circle(layer, (255, int(38 + 82 * energy), int(157 + 82 * energy), core), (x, y), radius)

        if particle.kind == 1 and energy > 0.76:
            pygame.draw.circle(layer, (255, 224, 244, 210), (x, y), 1)

    layer.blit(glow_large, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    layer.blit(glow_small, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # A bright liquid-like core bloom.
    core_layer = pygame.Surface(layer.get_size(), pygame.SRCALPHA)
    core_center = HEART_CENTER + pygame.Vector2(0, 14)
    core_pulse = 1.0 + math.sin(time_s * 1.3) * 0.08
    pygame.draw.ellipse(
        core_layer,
        (255, 110, 205, 25),
        pygame.Rect(0, 0, 175 * core_pulse, 130 * core_pulse),
    )
    rect = core_layer.get_bounding_rect()
    # Center only the non-transparent ellipse without disturbing the main layer.
    if rect.width:
        crop = core_layer.subsurface(rect).copy()
        layer.blit(crop, crop.get_rect(center=core_center), special_flags=pygame.BLEND_RGBA_ADD)


def save_frame(surface: pygame.Surface, name: str) -> None:
    out = Path(__file__).resolve().parent / name
    pygame.image.save(surface, out)
    print(f"Saved: {out}")


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Neon Heart / Scrolling Python")
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    canvas = pygame.Surface((WIDTH, HEIGHT)).convert()
    heart_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    font = pygame.font.SysFont("consolas,menlo,monospace", 16)
    clock = pygame.time.Clock()
    particles = make_particles()

    running = True
    paused = False
    time_s = 0.0
    scroll = 0.0

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.033)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    particles = make_particles()
                    time_s = 0.0
                elif event.key == pygame.K_s:
                    save_frame(canvas, "neon_heart_frame.png")
                elif event.key == pygame.K_t:
                    save_frame(heart_layer, "neon_heart_transparent.png")

        if not paused:
            time_s += dt
            scroll += 24.0 * dt
            update_particles(particles, time_s, dt)

        draw_code_background(canvas, font, scroll)
        draw_heart_layer(heart_layer, particles, time_s)
        canvas.blit(heart_layer, (0, 0))

        window_w, window_h = screen.get_size()
        scale = min(window_w / WIDTH, window_h / HEIGHT)
        view_size = (max(1, int(WIDTH * scale)), max(1, int(HEIGHT * scale)))
        view = pygame.transform.smoothscale(canvas, view_size)
        screen.fill((2, 3, 7))
        screen.blit(view, ((window_w - view_size[0]) // 2, (window_h - view_size[1]) // 2))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
