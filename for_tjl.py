import math
import random
import sys
import pygame

W, H = 980, 680
FPS = 60

PINKS = [
    (255, 105, 180),
    (255, 182, 193),
    (255, 20, 147),
    (255, 160, 205),
    (255, 210, 235),
]

BG_TOP = (18, 2, 20)
BG_BOTTOM = (5, 0, 12)

TITLE_TEXT = "I love JiaLin Tang"
SUBTITLE_TEXT = "This is a special gift from Xxxwj"

def pick_font(size, bold=False):
    for name in (
        "Avenir Next",
        "Avenir",
        "SF Pro Display",
        "SF Pro Text",
        "Helvetica Neue",
        "Helvetica",
        "Segoe UI",
        "DejaVu Sans",
        "Liberation Sans",
        "Arial",
    ):
        f = pygame.font.SysFont(name, size, bold=bold)
        if f:
            return f
    return pygame.font.Font(None, size)

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def heart_point(t):
    x = 16 * math.sin(t) ** 3
    y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
    return x, y

def draw_vertical_gradient(surf, top, bottom):
    for y in range(H):
        t = y / (H - 1)
        r = int(lerp(top[0], bottom[0], t))
        g = int(lerp(top[1], bottom[1], t))
        b = int(lerp(top[2], bottom[2], t))
        pygame.draw.line(surf, (r, g, b), (0, y), (W, y))

class Particle:
    __slots__ = ("x","y","vx","vy","r","life","maxlife","color","spark")
    def __init__(self, x, y, vx, vy, r, life, color, spark=False):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.r = r
        self.life = life
        self.maxlife = life
        self.color = color
        self.spark = spark

    def update(self, mx, my):
        dx = mx - self.x
        dy = my - self.y
        dist2 = dx*dx + dy*dy + 80.0
        pull = 220.0 / dist2
        self.vx += dx * pull
        self.vy += dy * pull

        self.vx *= 0.985
        self.vy = self.vy * 0.985 - 0.02

        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surf):
        if self.life <= 0:
            return
        a = int(255 * (self.life / self.maxlife))
        a = clamp(a, 0, 255)

        glow_layers = [(10, 0.10), (6, 0.18), (3, 0.35), (0, 1.0)]
        for add, mul in glow_layers:
            rr = max(1, int(self.r + add))
            aa = int(a * mul)
            s = pygame.Surface((rr*2+2, rr*2+2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, aa), (rr+1, rr+1), rr)
            surf.blit(s, (self.x - rr - 1, self.y - rr - 1))

        if self.spark and random.random() < 0.18:
            rr = max(1, self.r)
            s = pygame.Surface((rr*8, rr*8), pygame.SRCALPHA)
            c = (*self.color, min(255, a+60))
            pygame.draw.line(s, c, (0, rr*4), (rr*8, rr*4), 2)
            pygame.draw.line(s, c, (rr*4, 0), (rr*4, rr*8), 2)
            surf.blit(s, (self.x - rr*4, self.y - rr*4))

def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Pink Heart")
    clock = pygame.time.Clock()

    font_title = pick_font(54)
    font_sub = pick_font(22)

    bg = pygame.Surface((W, H))
    draw_vertical_gradient(bg, BG_TOP, BG_BOTTOM)

    fade = pygame.Surface((W, H), pygame.SRCALPHA)

    cx, cy = W * 0.5, H * 0.55
    tx, ty = cx, cy

    scale = 19.0
    t = 0.0
    particles = []

    phase = 0.0

    while True:
        dt = clock.tick(FPS) / 1000.0
        phase += dt

        mx, my = pygame.mouse.get_pos()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for _ in range(280):
                    ang = random.random() * math.tau
                    spd = random.uniform(1.0, 6.5)
                    vx = math.cos(ang) * spd
                    vy = math.sin(ang) * spd
                    r = random.randint(2, 4)
                    life = random.randint(50, 110)
                    color = random.choice(PINKS)
                    particles.append(Particle(mx, my, vx, vy, r, life, color, spark=True))

        tx = mx
        ty = my + 40
        cx = lerp(cx, tx, 0.06)
        cy = lerp(cy, ty, 0.06)

        screen.blit(bg, (0, 0))
        fade.fill((0, 0, 0, 48))
        screen.blit(fade, (0, 0))

        breath = 1.0 + 0.03 * math.sin(phase * 1.6)
        cur_scale = scale * breath

        emit = 18
        for _ in range(emit):
            t += 0.12
            x, y = heart_point(t)

            px = cx + x * cur_scale
            py = cy - y * cur_scale

            dx = px - cx
            dy = py - cy
            mag = math.hypot(dx, dy) + 1e-6
            nx, ny = dx / mag, dy / mag

            spd = random.uniform(0.7, 2.8)
            vx = nx * spd + random.uniform(-0.65, 0.65)
            vy = ny * spd + random.uniform(-0.65, 0.65)

            r = random.randint(2, 4)
            life = random.randint(55, 105)
            color = random.choice(PINKS)
            spark = (random.random() < 0.25)

            particles.append(Particle(px, py, vx, vy, r, life, color, spark=spark))

        alive = []
        for p in particles:
            p.update(mx, my)
            if p.life > 0:
                p.draw(screen)
                alive.append(p)
        particles = alive[-5200:]

        pulse = 1.0 + 0.02 * math.sin(phase * 2.0)
        title = TITLE_TEXT
        subtitle = SUBTITLE_TEXT

        txt = font_title.render(title, True, (255, 255, 255))
        txt = pygame.transform.smoothscale(txt, (int(txt.get_width()*pulse), int(txt.get_height()*pulse)))
        screen.blit(txt, (W/2 - txt.get_width()/2, 56))

        sub = font_sub.render(subtitle, True, (255, 255, 255))
        screen.blit(sub, (W/2 - sub.get_width()/2, 126))

        pygame.display.flip()

if __name__ == "__main__":
    main()