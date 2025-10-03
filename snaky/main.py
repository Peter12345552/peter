import pygame
import sys
import random
import time
import math  # 添加math模块导入

# 初始化Pygame
pygame.init()

# 设置常量
CELL_SIZE = 12  # 每个格子的大小
GRID_SIZE = 50  # 网格大小 (50x50)
PADDING = 20    # 边距
OBSTACLE_MOVE_INTERVAL = 5000  # 障碍物移动间隔（毫秒）

# 计算窗口大小
WINDOW_SIZE = CELL_SIZE * GRID_SIZE + 2 * PADDING
WINDOW_COLOR = (0, 0, 0)      # 黑色背景
GRID_COLOR = (40, 40, 40)     # 深灰色网格线
GRID_BOLD_COLOR = (60, 60, 60)  # 加粗网格线颜色
SNAKE_COLOR = (50, 205, 50)     # 蛇的颜色（绿色）
SNAKE_HEAD_COLOR = (34, 139, 34)  # 蛇头的颜色（深绿色）
NORMAL_FOOD_COLOR = (255, 50, 50)  # 普通食物颜色（亮红色）
SUPER_FOOD_COLOR = (255, 255, 50)  # 大食物颜色（亮黄色）
SLOW_FOOD_COLOR = (50, 50, 255)    # 减速食物颜色（亮蓝色）
OBSTACLE_COLOR = (128, 128, 128)   # 障碍物颜色（灰色）
TEXT_COLOR = (255, 255, 255)       # 文字颜色（白色）
BUTTON_COLOR = (60, 60, 60)        # 按钮颜色（深灰色）
BUTTON_HOVER_COLOR = (80, 80, 80)  # 按钮悬停颜色（较亮的灰色）

# 方向
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# 所有可能的移动方向
ALL_DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

# 食物类型
NORMAL_FOOD = 'normal'  # 普通食物
SUPER_FOOD = 'super'    # 大食物
SLOW_FOOD = 'slow'      # 减速食物

# 创建窗口
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("贪吃蛇游戏")

# 创建字体
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

class Button:
    def __init__(self, x, y, width, height, text, direction=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.direction = direction
        self.hovered = False

    def draw(self):
        # 绘制按钮背景
        color = BUTTON_HOVER_COLOR if self.hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect)
        
        # 绘制按钮边框（加粗）
        pygame.draw.rect(screen, TEXT_COLOR, self.rect, 3)
        
        # 绘制按钮文字（放大）
        text_surface = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return self.direction
        return None

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.position = [(GRID_SIZE // 2, GRID_SIZE // 2)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.length = 1
        self.speed_multiplier = 1.0
        self.last_update_time = pygame.time.get_ticks()
        
    def update(self, obstacles):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time < 50:  # 添加最小更新间隔
            return False
            
        self.last_update_time = current_time
        self.direction = self.next_direction
        
        new_head = (
            (self.position[0][0] + self.direction[0]) % GRID_SIZE,
            (self.position[0][1] + self.direction[1]) % GRID_SIZE
        )
        
        # 检查是否撞到自己或障碍物
        if new_head in self.position[:-1] or new_head in obstacles:  # 修改碰撞检测
            return True
            
        self.position.insert(0, new_head)
        if len(self.position) > self.length:
            self.position.pop()
            
        return False
        
    def grow(self):
        self.length += 1

class Game:
    def __init__(self):
        self.create_direction_buttons()
        self.wall_mode = True  # True表示撞墙死亡，False表示穿墙模式
        self.reset()
        
    def create_direction_buttons(self):
        button_size = 50  # 增大按钮尺寸
        spacing = 15     # 增加按钮间距
        
        # 计算按钮组的总宽度和高度
        total_width = 3 * button_size + 2 * spacing
        total_height = 3 * button_size + 2 * spacing
        
        # 计算按钮组的左上角位置，使其位于右下角
        base_x = WINDOW_SIZE - total_width - PADDING
        base_y = WINDOW_SIZE - total_height - PADDING
        
        self.buttons = [
            # 上按钮
            Button(base_x + button_size + spacing, base_y, 
                  button_size, button_size, "↑", UP),
            # 下按钮
            Button(base_x + button_size + spacing, base_y + 2 * (button_size + spacing), 
                  button_size, button_size, "↓", DOWN),
            # 左按钮
            Button(base_x, base_y + button_size + spacing, 
                  button_size, button_size, "←", LEFT),
            # 右按钮
            Button(base_x + 2 * (button_size + spacing), base_y + button_size + spacing, 
                  button_size, button_size, "→", RIGHT)
        ]
        
    def reset(self):
        self.snake = Snake()
        self.score = 0
        self.foods = []
        self.obstacles = []
        self.obstacle_directions = {}  # 存储每个障碍物的移动方向
        self.last_obstacle_move_time = pygame.time.get_ticks()
        self.game_over = False
        self.paused = False
        self.base_speed = 8  # 降低基础速度，使控制更容易
        self.generate_obstacles()
        self.generate_foods()
        
    def generate_obstacles(self):
        self.obstacles = []
        self.obstacle_directions = {}
        for _ in range(10):  # 生成10个障碍物
            while True:
                pos = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
                if pos not in self.obstacles and pos not in self.snake.position:
                    self.obstacles.append(pos)
                    # 为每个障碍物随机分配一个移动方向
                    self.obstacle_directions[pos] = random.choice(ALL_DIRECTIONS)
                    break
    
    def move_obstacles(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_obstacle_move_time >= OBSTACLE_MOVE_INTERVAL:
            self.last_obstacle_move_time = current_time
            
            new_obstacles = []
            new_directions = {}
            
            # 移动每个障碍物
            for obstacle in self.obstacles:
                direction = self.obstacle_directions[obstacle]
                new_pos = (
                    (obstacle[0] + direction[0]) % GRID_SIZE,
                    (obstacle[1] + direction[1]) % GRID_SIZE
                )
                
                # 如果新位置与其他障碍物或食物冲突，随机选择新方向
                if new_pos in new_obstacles or new_pos in [f[0] for f in self.foods]:
                    direction = random.choice(ALL_DIRECTIONS)
                    new_pos = (
                        (obstacle[0] + direction[0]) % GRID_SIZE,
                        (obstacle[1] + direction[1]) % GRID_SIZE
                    )
                
                new_obstacles.append(new_pos)
                new_directions[new_pos] = direction
            
            self.obstacles = new_obstacles
            self.obstacle_directions = new_directions
    
    def generate_foods(self):
        self.foods = []
        # 随机决定食物数量（5-10个）
        num_foods = random.randint(5, 10)
        
        # 根据食物总数调整各类食物的比例
        num_normal = int(num_foods * 0.6)  # 60%是普通食物
        num_super = int(num_foods * 0.2)   # 20%是大食物
        num_slow = num_foods - num_normal - num_super  # 剩余的是减速食物
        
        food_types = ([NORMAL_FOOD] * num_normal + 
                     [SUPER_FOOD] * num_super + 
                     [SLOW_FOOD] * num_slow)
        random.shuffle(food_types)
        
        while len(self.foods) < num_foods:
            pos = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
            if (pos not in [f[0] for f in self.foods] and 
                pos not in self.snake.position and 
                pos not in self.obstacles):
                food_type = food_types[len(self.foods)]
                self.foods.append((pos, food_type))
    
    def get_current_speed(self):
        # 每20分增加10%的速度，最高速度限制在原始速度的1.5倍
        speed_increase_factor = min(1 + (self.score // 20) * 0.1, 1.5)
        return self.base_speed * speed_increase_factor * self.snake.speed_multiplier
    
    def update(self):
        if self.game_over or self.paused:
            return
            
        # 更新障碍物位置
        self.move_obstacles()
            
        # 获取蛇的新头部位置
        head_x = self.snake.position[0][0] + self.snake.direction[0]
        head_y = self.snake.position[0][1] + self.snake.direction[1]
        
        # 根据边界模式处理位置
        if self.wall_mode:
            # 撞墙模式：如果碰到边界就死亡
            if head_x < 0 or head_x >= GRID_SIZE or head_y < 0 or head_y >= GRID_SIZE:
                self.game_over = True
                return
        else:
            # 穿墙模式：从另一侧出现
            head_x = head_x % GRID_SIZE
            head_y = head_y % GRID_SIZE
            
        # 更新蛇的位置
        new_head = (head_x, head_y)
        
        # 检查是否撞到自己或障碍物
        if new_head in self.snake.position[:-1] or new_head in self.obstacles:
            self.game_over = True
            return
            
        # 更新蛇的位置
        self.snake.position.insert(0, new_head)
        if len(self.snake.position) > self.snake.length:
            self.snake.position.pop()
            
        # 检查是否吃到食物
        for food in self.foods[:]:
            if new_head == food[0]:
                self.foods.remove(food)
                self.snake.grow()
                
                # 根据食物类型给予不同效果
                if food[1] == NORMAL_FOOD:
                    self.score += 10
                elif food[1] == SUPER_FOOD:
                    self.score += 20
                elif food[1] == SLOW_FOOD:
                    self.score += 5
                    self.snake.speed_multiplier = 0.8  # 减速效果
                
                if not self.foods:
                    self.generate_foods()
                    self.snake.speed_multiplier = 1.0  # 重置速度
                break

    def draw(self):
        # 填充背景
        screen.fill(WINDOW_COLOR)
        
        # 绘制网格
        for x in range(GRID_SIZE + 1):
            # 每5条线加粗一次
            color = GRID_BOLD_COLOR if x % 5 == 0 else GRID_COLOR
            width = 2 if x % 5 == 0 else 1
            
            # 绘制垂直线
            pygame.draw.line(screen, color,
                           (x * CELL_SIZE + PADDING, PADDING),
                           (x * CELL_SIZE + PADDING, WINDOW_SIZE - PADDING),
                           width)
            
            # 绘制水平线
            pygame.draw.line(screen, color,
                           (PADDING, x * CELL_SIZE + PADDING),
                           (WINDOW_SIZE - PADDING, x * CELL_SIZE + PADDING),
                           width)
        
        # 绘制障碍物
        for obstacle in self.obstacles:
            x = obstacle[0] * CELL_SIZE + PADDING
            y = obstacle[1] * CELL_SIZE + PADDING
            # 绘制小山丘形状
            hill_points = [
                (x, y + CELL_SIZE),                    # 左下角
                (x + CELL_SIZE//2, y + CELL_SIZE//4), # 山顶
                (x + CELL_SIZE, y + CELL_SIZE)        # 右下角
            ]
            pygame.draw.polygon(screen, OBSTACLE_COLOR, hill_points)
            # 添加山丘轮廓
            pygame.draw.lines(screen, (100, 100, 100), False, hill_points, 2)

        # 绘制食物
        for food in self.foods:
            x = food[0][0] * CELL_SIZE + PADDING
            y = food[0][1] * CELL_SIZE + PADDING
            center_x = x + CELL_SIZE // 2
            center_y = y + CELL_SIZE // 2
            
            if food[1] == NORMAL_FOOD:
                 # 普通食物：绘制一个苹果形状（红色圆形加绿色叶子）
                 pygame.draw.circle(screen, NORMAL_FOOD_COLOR, (center_x, center_y), CELL_SIZE // 2 - 1)
                 # 绘制叶子
                 leaf_points = [
                     (center_x, center_y - CELL_SIZE // 2),
                     (center_x + CELL_SIZE // 4, center_y - CELL_SIZE // 3),
                     (center_x + CELL_SIZE // 3, center_y - CELL_SIZE // 2)
                 ]
                 pygame.draw.polygon(screen, (34, 139, 34), leaf_points)
                 
             elif food[1] == SUPER_FOOD:
                 # 超级食物：绘制一个星星形状
                 points = []
                 for i in range(5):
                     # 外部点
                     angle = i * 2 * math.pi / 5 - math.pi / 2
                     points.append((
                         center_x + int(CELL_SIZE/2 * 0.9 * math.cos(angle)),
                         center_y + int(CELL_SIZE/2 * 0.9 * math.sin(angle))
                     ))
                     # 内部点
                     angle += math.pi / 5
                     points.append((
                         center_x + int(CELL_SIZE/4 * math.cos(angle)),
                         center_y + int(CELL_SIZE/4 * math.sin(angle))
                     ))
                 pygame.draw.polygon(screen, SUPER_FOOD_COLOR, points)
                 
             else:  # SLOW_FOOD
                 # 减速食物：绘制一个雪花形状
                 size = CELL_SIZE // 2 - 1
                 # 绘制主体菱形
                 diamond_points = [
                     (center_x, center_y - size),  # 上
                     (center_x + size, center_y),  # 右
                     (center_x, center_y + size),  # 下
                     (center_x - size, center_y)   # 左
                 ]
                 pygame.draw.polygon(screen, SLOW_FOOD_COLOR, diamond_points)
                 # 绘制交叉线
                 pygame.draw.line(screen, SLOW_FOOD_COLOR, 
                                (center_x - size//2, center_y - size//2),
                                (center_x + size//2, center_y + size//2), 2)
                 pygame.draw.line(screen, SLOW_FOOD_COLOR,
                                (center_x - size//2, center_y + size//2),
                                (center_x + size//2, center_y - size//2), 2)
        
        # 绘制蛇
        for i, segment in enumerate(self.snake.position):
            x = segment[0] * CELL_SIZE + PADDING
            y = segment[1] * CELL_SIZE + PADDING
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_COLOR
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))
        
        # 绘制方向按钮
        for button in self.buttons:
            button.draw()
        
        # 显示分数、当前食物数量和边界模式
        score_text = font.render(f'分数: {self.score}', True, TEXT_COLOR)
        food_count_text = small_font.render(f'当前食物: {len(self.foods)}个', True, TEXT_COLOR)
        mode_text = small_font.render(f'边界模式: {"撞墙死亡" if self.wall_mode else "穿墙"}', True, TEXT_COLOR)
        screen.blit(score_text, (PADDING, 5))
        screen.blit(food_count_text, (PADDING, 35))
        screen.blit(mode_text, (PADDING, 65))
        
        # 显示操作说明
        if self.paused:
            instructions = [
                "游戏已暂停",
                "按 P 键继续游戏",
                "按 M 键切换边界模式",
                "方向键控制蛇的移动",
                "红色食物: +10分",
                "黄色食物: +20分",
                "蓝色食物: +5分并减速",
                "灰色方块: 移动的障碍物",
                f"当前速度: {int(self.get_current_speed())}",
                f"边界模式: {'撞墙死亡' if self.wall_mode else '穿墙'}"
            ]
            
            for i, text in enumerate(instructions):
                instruction_text = small_font.render(text, True, TEXT_COLOR)
                screen.blit(instruction_text, 
                          (WINDOW_SIZE//2 - 100, WINDOW_SIZE//2 - 100 + i*25))
        
        # 如果游戏结束，显示游戏结束对话框
        if self.game_over:
            # 绘制半透明背景
            dialog_surface = pygame.Surface((300, 150))
            dialog_surface.fill((240, 240, 240))
            dialog_surface.set_alpha(230)
            dialog_rect = dialog_surface.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2))
            screen.blit(dialog_surface, dialog_rect)
            
            # 绘制对话框边框
            pygame.draw.rect(screen, TEXT_COLOR, dialog_rect, 2)
            
            # 显示游戏结束文本
            game_over_text = font.render('游戏结束!', True, TEXT_COLOR)
            score_final_text = font.render(f'最终得分: {self.score}', True, TEXT_COLOR)
            restart_text = font.render('按空格键重新开始', True, TEXT_COLOR)
            
            # 计算文本位置
            text_y = WINDOW_SIZE//2 - 40
            screen.blit(game_over_text, game_over_text.get_rect(center=(WINDOW_SIZE//2, text_y)))
            screen.blit(score_final_text, score_final_text.get_rect(center=(WINDOW_SIZE//2, text_y + 35)))
            screen.blit(restart_text, restart_text.get_rect(center=(WINDOW_SIZE//2, text_y + 70)))
        
        pygame.display.flip()

def main():
    clock = pygame.time.Clock()
    game = Game()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if game.game_over and event.key == pygame.K_SPACE:
                    game.reset()
                elif event.key == pygame.K_p:  # P键暂停/继续
                    game.paused = not game.paused
                elif event.key == pygame.K_m:  # M键切换边界模式
                    game.wall_mode = not game.wall_mode
                elif not game.game_over and not game.paused:
                    if event.key == pygame.K_UP and game.snake.direction != DOWN:
                        game.snake.next_direction = UP
                    elif event.key == pygame.K_DOWN and game.snake.direction != UP:
                        game.snake.next_direction = DOWN
                    elif event.key == pygame.K_LEFT and game.snake.direction != RIGHT:
                        game.snake.next_direction = LEFT
                    elif event.key == pygame.K_RIGHT and game.snake.direction != LEFT:
                        game.snake.next_direction = RIGHT
            
            # 处理方向按钮点击
            if not game.game_over and not game.paused:
                for button in game.buttons:
                    direction = button.handle_event(event)
                    if direction and direction != (-game.snake.direction[0], -game.snake.direction[1]):
                        game.snake.next_direction = direction
        
        # 检查按键状态，实现持续按键响应
        if not game.game_over and not game.paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and game.snake.direction != DOWN:
                game.snake.next_direction = UP
            elif keys[pygame.K_DOWN] and game.snake.direction != UP:
                game.snake.next_direction = DOWN
            elif keys[pygame.K_LEFT] and game.snake.direction != RIGHT:
                game.snake.next_direction = LEFT
            elif keys[pygame.K_RIGHT] and game.snake.direction != LEFT:
                game.snake.next_direction = RIGHT
        
        game.update()
        game.draw()
        clock.tick(60)  # 固定帧率为60FPS，使移动更流畅

if __name__ == "__main__":
    main()