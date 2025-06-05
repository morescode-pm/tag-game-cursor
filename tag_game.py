import pygame
import random
import math
import time

WIDTH, HEIGHT = 640, 480
PLAYER_SIZE = 40
SPEED = 5
AI_SPEED = 4
FPS = 60

PLAYER_COLOR = (0, 128, 255)
AI_COLOR = (255, 100, 0)
IT_COLOR = (255, 0, 0)
BG_COLOR = (30, 30, 30)

# Add corner barriers
CORNER_SIZE = 60
OBSTACLES = [
    pygame.Rect(0, 0, CORNER_SIZE, CORNER_SIZE),  # Top-left
    pygame.Rect(WIDTH - CORNER_SIZE, 0, CORNER_SIZE, CORNER_SIZE),  # Top-right
    pygame.Rect(0, HEIGHT - CORNER_SIZE, CORNER_SIZE, CORNER_SIZE),  # Bottom-left
    pygame.Rect(WIDTH - CORNER_SIZE, HEIGHT - CORNER_SIZE, CORNER_SIZE, CORNER_SIZE),  # Bottom-right
    pygame.Rect(200, 150, 80, 180),
    pygame.Rect(400, 100, 60, 60),
    pygame.Rect(320, 350, 120, 40)
]

CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
EDGE_MARGIN = 40
EDGE_ESCAPE_TIME = 60  # frames

NUM_AI = 2  # Number of AI players

class Player:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.is_it = False
        self.frozen_until = 0  # timestamp until which player is frozen
        self.edge_timer = 0

    def move(self, dx, dy):
        if time.time() < self.frozen_until:
            return
        new_x = (self.x + dx * SPEED) % WIDTH
        new_y = (self.y + dy * SPEED) % HEIGHT
        future_rect = pygame.Rect(new_x, new_y, PLAYER_SIZE, PLAYER_SIZE)
        if not any(future_rect.colliderect(ob) for ob in OBSTACLES):
            self.x = new_x
            self.y = new_y

    def rect(self):
        return pygame.Rect(self.x, self.y, PLAYER_SIZE, PLAYER_SIZE)

    def at_edge(self):
        return (
            self.x < EDGE_MARGIN or self.x > WIDTH - PLAYER_SIZE - EDGE_MARGIN or
            self.y < EDGE_MARGIN or self.y > HEIGHT - PLAYER_SIZE - EDGE_MARGIN
        )

class AIPlayer(Player):
    def move_ai(self, target, chasing):
        if time.time() < self.frozen_until:
            return
        # 23% chance to make a suboptimal move or pause
        if random.random() < 0.23:
            # 50% chance to pause, 50% chance to move in a random direction
            if random.random() < 0.5:
                return  # Pause this frame
            else:
                angle = random.uniform(0, 2 * math.pi)
                move_x = math.cos(angle)
                move_y = math.sin(angle)
        else:
            dx = target.x - self.x
            dy = target.y - self.y
            dist = math.hypot(dx, dy)
            if dist == 0:
                return
            # Normalize
            dx /= dist
            dy /= dist
            if chasing:
                move_x, move_y = dx, dy
            else:
                # Evasion logic: move away from player
                move_x, move_y = -dx, -dy
                # If at edge for too long, move toward center
                if self.at_edge():
                    self.edge_timer += 1
                    if self.edge_timer > EDGE_ESCAPE_TIME:
                        cx, cy = CENTER_X - self.x, CENTER_Y - self.y
                        cdist = math.hypot(cx, cy)
                        if cdist > 0:
                            move_x, move_y = cx / cdist, cy / cdist
                else:
                    self.edge_timer = 0
        # Try to move, but avoid obstacles
        best_x, best_y = self.x, self.y
        best_dist = -1
        for angle in [0, math.pi/4, -math.pi/4, math.pi/2, -math.pi/2]:
            test_dx = math.cos(math.atan2(move_y, move_x) + angle)
            test_dy = math.sin(math.atan2(move_y, move_x) + angle)
            new_x = (self.x + test_dx * AI_SPEED) % WIDTH
            new_y = (self.y + test_dy * AI_SPEED) % HEIGHT
            future_rect = pygame.Rect(new_x, new_y, PLAYER_SIZE, PLAYER_SIZE)
            if not any(future_rect.colliderect(ob) for ob in OBSTACLES):
                d = math.hypot(target.x - new_x, target.y - new_y)
                if chasing:
                    d = -d  # minimize distance if chasing
                if best_dist == -1 or d > best_dist:
                    best_x, best_y = new_x, new_y
                    best_dist = d
        self.x = best_x
        self.y = best_y

def check_tag(p1, p2):
    return p1.rect().colliderect(p2.rect())

def separate_players(p1, p2):
    # Move p2 a short distance away in a random direction
    angle = random.uniform(0, 2 * math.pi)
    for _ in range(10):
        new_x = (p2.x + math.cos(angle) * 60) % WIDTH
        new_y = (p2.y + math.sin(angle) * 60) % HEIGHT
        future_rect = pygame.Rect(new_x, new_y, PLAYER_SIZE, PLAYER_SIZE)
        if not any(future_rect.colliderect(ob) for ob in OBSTACLES) and not future_rect.colliderect(p1.rect()):
            p2.x = new_x
            p2.y = new_y
            return
        angle += math.pi / 5  # try another direction

def repel_players_from(new_it, all_players, repel_dist=80):
    for p in all_players:
        if p is new_it:
            continue
        angle = math.atan2(p.y - new_it.y, p.x - new_it.x)
        for _ in range(10):
            new_x = (p.x + math.cos(angle) * repel_dist) % WIDTH
            new_y = (p.y + math.sin(angle) * repel_dist) % HEIGHT
            future_rect = pygame.Rect(new_x, new_y, PLAYER_SIZE, PLAYER_SIZE)
            if not any(future_rect.colliderect(ob) for ob in OBSTACLES) and not future_rect.colliderect(new_it.rect()):
                # Also avoid overlapping with other players
                overlap = False
                for other in all_players:
                    if other is not p and other is not new_it and future_rect.colliderect(other.rect()):
                        overlap = True
                        break
                if not overlap:
                    p.x = new_x
                    p.y = new_y
                    break
            angle += math.pi / 5  # try another direction

def draw_rabbit(screen, x, y, is_it):
    # Body
    pygame.draw.ellipse(screen, (220, 220, 220), (x, y+10, PLAYER_SIZE, PLAYER_SIZE-10))
    # Head
    pygame.draw.ellipse(screen, (220, 220, 220), (x+8, y-10, PLAYER_SIZE-16, PLAYER_SIZE-10))
    # Ears
    pygame.draw.ellipse(screen, (220, 220, 220), (x+10, y-28, 8, 24))
    pygame.draw.ellipse(screen, (220, 220, 220), (x+PLAYER_SIZE-18, y-28, 8, 24))
    # Nose
    pygame.draw.ellipse(screen, (255, 128, 128), (x+PLAYER_SIZE//2-4, y-2, 8, 6))
    # Eyes
    pygame.draw.ellipse(screen, (0,0,0), (x+16, y-2, 4, 4))
    pygame.draw.ellipse(screen, (0,0,0), (x+PLAYER_SIZE-20, y-2, 4, 4))
    # Tag highlight
    if is_it:
        pygame.draw.ellipse(screen, (255, 0, 0), (x+4, y+14, PLAYER_SIZE-8, PLAYER_SIZE-18), 3)

def draw_hunter(screen, x, y, is_it):
    # Body
    pygame.draw.rect(screen, (139, 69, 19), (x+8, y+18, PLAYER_SIZE-16, PLAYER_SIZE-18))
    # Head
    pygame.draw.ellipse(screen, (222, 184, 135), (x+10, y, PLAYER_SIZE-20, PLAYER_SIZE-16))
    # Hat
    pygame.draw.rect(screen, (0, 128, 0), (x+12, y-8, PLAYER_SIZE-24, 10))
    pygame.draw.ellipse(screen, (0, 128, 0), (x+18, y-14, PLAYER_SIZE-36, 12))
    # Face details
    pygame.draw.ellipse(screen, (0,0,0), (x+18, y+6, 4, 4))
    pygame.draw.ellipse(screen, (0,0,0), (x+PLAYER_SIZE-22, y+6, 4, 4))
    # Tag highlight
    if is_it:
        pygame.draw.rect(screen, (255, 0, 0), (x+8, y+18, PLAYER_SIZE-16, PLAYER_SIZE-18), 3)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Tag: Player vs AI')
    clock = pygame.time.Clock()

    player = Player(100, HEIGHT // 2, PLAYER_COLOR)
    ai_players = []
    for i in range(NUM_AI):
        angle = 2 * math.pi * i / NUM_AI
        x = int(WIDTH // 2 + 180 * math.cos(angle))
        y = int(HEIGHT // 2 + 180 * math.sin(angle))
        ai_players.append(AIPlayer(x, y, AI_COLOR))

    all_players = [player] + ai_players
    # Randomly choose who is it
    it_index = random.randint(0, len(all_players) - 1)
    for i, p in enumerate(all_players):
        p.is_it = (i == it_index)
        if p.is_it:
            p.frozen_until = time.time() + 2

    last_tag_time = 0
    last_tagged = None  # index of last tagged
    NO_TAG_BACK_TIME = 3

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_RIGHT]: dx += 1
        if keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_DOWN]: dy += 1
        player.move(dx, dy)

        # Find who is 'it' and who are not
        it_player = next(p for p in all_players if p.is_it)
        not_it_players = [p for p in all_players if not p.is_it]

        # AI logic
        for ai in ai_players:
            if ai.is_it:
                # Chase nearest not-it player
                target = min(not_it_players, key=lambda p: math.hypot(p.x - ai.x, p.y - ai.y))
                ai.move_ai(target, chasing=True)
            else:
                # Run from 'it' player
                ai.move_ai(it_player, chasing=False)

        # Tag check with no tag backs
        now = time.time()
        for i, p in enumerate(all_players):
            if p.is_it:
                for j, other in enumerate(all_players):
                    if i != j and not other.is_it and check_tag(p, other):
                        if not (last_tagged == i and now - last_tag_time < NO_TAG_BACK_TIME):
                            p.is_it = False
                            other.is_it = True
                            other.frozen_until = now + 2
                            separate_players(p, other)
                            repel_players_from(other, all_players)
                            last_tag_time = now
                            last_tagged = j
                        break

        # Draw
        screen.fill(BG_COLOR)
        # Draw obstacles
        for ob in OBSTACLES:
            pygame.draw.rect(screen, (80, 80, 80), ob)
        # Draw all players
        for i, p in enumerate(all_players):
            if p == player:
                draw_rabbit(screen, p.x, p.y, p.is_it)
            else:
                draw_hunter(screen, p.x, p.y, p.is_it)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main() 