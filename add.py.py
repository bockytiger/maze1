import pygame
import random
import sys
from collections import deque

# 初期設定
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 20
ROWS, COLS = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE
WHITE, BLACK, GREEN, RED, BLUE, GRAY = (255,255,255), (0,0,0), (0,255,0), (255,0,0), (0,0,255), (200,200,200)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("壁伸ばし法迷路")
font = pygame.font.SysFont("meiryo", 12)

# 壁伸ばし法による迷路生成
def generate_maze():
    maze = [[1 for _ in range(COLS)] for _ in range(ROWS)]

    def extend_wall(r, c):
        directions = [(0,2), (0,-2), (2,0), (-2,0)]
        random.shuffle(directions)
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 1 <= nr < ROWS-1 and 1 <= nc < COLS-1 and maze[nr][nc] == 1:
                maze[nr][nc] = 0
                maze[r + dr//2][c + dc//2] = 0
                extend_wall(nr, nc)

    maze[1][1] = 0
    extend_wall(1,1)
    return maze

# スタートから通路をたどる（BFS）
def bfs_path(maze, start):
    visited = set()
    queue = deque([start])
    path = []

    while queue:
        r, c = queue.popleft()
        if (r, c) in visited:
            continue
        visited.add((r, c))
        path.append((r, c))
        for dr, dc in [(0,1),(1,0),(0,-1),(-1,0)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and (nr, nc) not in visited:
                queue.append((nr, nc))
    return path

# UIボタン描画
def draw_button(text, x, y, w, h, color):
    pygame.draw.rect(screen, color, (x, y, w, h))
    label = font.render(text, True, BLACK)
    screen.blit(label, (x + 10, y + 10))
    return pygame.Rect(x, y, w, h)

# メインループ
def main():
    maze = generate_maze()
    start = (1,1)
    path = bfs_path(maze, start)

    # スタートから順に距離を空けて①〜⑤とゴールを配置
    step = len(path) // 7
    checkpoints = [path[i*step] for i in range(1,6)]
    goal = path[6*step]

    player = list(start)
    checkpoint_index = 0
    game_started = False
    game_over = False
    clock = pygame.time.Clock()

    while True:
        screen.fill(WHITE)

        # 迷路描画
        for r in range(ROWS):
            for c in range(COLS):
                color = BLACK if maze[r][c] == 1 else WHITE
                pygame.draw.rect(screen, color, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # スタート・ゴール・チェックポイント描画
        pygame.draw.rect(screen, GREEN, (start[1]*CELL_SIZE, start[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, RED, (goal[1]*CELL_SIZE, goal[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        for i, (r, c) in enumerate(checkpoints):
            pygame.draw.rect(screen, BLUE, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            label = font.render(str(i+1), True, WHITE)
            screen.blit(label, (c*CELL_SIZE+5, r*CELL_SIZE+5))

        # プレイヤー描画
        pygame.draw.rect(screen, GRAY, (player[1]*CELL_SIZE, player[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # UI描画
        if not game_started:
            start_btn = draw_button("スタート", WIDTH//2 - 60, HEIGHT//2 - 30, 120, 50, GREEN)
        elif game_over:
            end_btn = draw_button("終わる", WIDTH//2 - 130, HEIGHT//2 - 30, 100, 50, RED)
            retry_btn = draw_button("もう一度", WIDTH//2 + 30, HEIGHT//2 - 30, 120, 50, GREEN)

        pygame.display.flip()

        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game_started and start_btn.collidepoint(event.pos):
                    game_started = True
                elif game_over:
                    if end_btn.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                    elif retry_btn.collidepoint(event.pos):
                        main()

            elif event.type == pygame.KEYDOWN and game_started and not game_over:
                dr, dc = 0, 0
                if event.key == pygame.K_UP: dr = -1
                elif event.key == pygame.K_DOWN: dr = 1
                elif event.key == pygame.K_LEFT: dc = -1
                elif event.key == pygame.K_RIGHT: dc = 1
                nr, nc = player[0] + dr, player[1] + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0:
                    player = [nr, nc]
                    # チェックポイント通過判定
                    if checkpoint_index < len(checkpoints) and (nr, nc) == checkpoints[checkpoint_index]:
                        checkpoint_index += 1
                    # ゴール判定
                    if (nr, nc) == goal and checkpoint_index == len(checkpoints):
                        game_over = True

        clock.tick(30)

main()