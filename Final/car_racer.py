import pygame
import math
import sys
import os
from pathlib import Path
from typing import Tuple, List, Optional
from dataclasses import dataclass
from enum import Enum, auto


# ==================== 工具函数 ====================

def scale_image(img: pygame.Surface, factor: float) -> pygame.Surface:
    """按比例缩放图像"""
    size = (round(img.get_width() * factor), round(img.get_height() * factor))
    return pygame.transform.scale(img, size)


def blit_rotate_center(win: pygame.Surface, image: pygame.Surface, 
                       top_left: Tuple[float, float], angle: float) -> pygame.Rect:
    """在中心点旋转并绘制图像"""
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)
    return new_rect


def blit_text_center(win: pygame.Surface, font: pygame.font.Font, 
                     text: str, color: Tuple[int, int, int] = (255, 255, 255)) -> None:
    """在屏幕中央绘制文本"""
    render = font.render(text, True, color)
    x = (win.get_width() - render.get_width()) // 2
    y = (win.get_height() - render.get_height()) // 2
    
    # 添加半透明背景使文字更清晰
    padding = 20
    bg_rect = pygame.Rect(x - padding, y - padding, 
                          render.get_width() + padding * 2, 
                          render.get_height() + padding * 2)
    bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    bg_surface.fill((0, 0, 0, 180))
    win.blit(bg_surface, bg_rect.topleft)
    win.blit(render, (x, y))


def get_resource_path(relative_path: str) -> str:
    """获取资源文件的绝对路径，支持打包后运行"""
    base_path = Path(__file__).parent
    return str(base_path / relative_path)


# ==================== 游戏状态 ====================

class GameState(Enum):
    """游戏状态枚举"""
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    LEVEL_COMPLETE = auto()
    GAME_OVER = auto()
    GAME_WON = auto()


@dataclass
class GameConfig:
    """游戏配置"""
    FPS: int = 60
    MAX_LEVELS: int = 10
    TRACK_SCALE: float = 0.9
    CAR_SCALE: float = 0.55
    GRASS_SCALE: float = 2.5
    PLAYER_MAX_VEL: float = 4.0
    PLAYER_ROTATION_VEL: float = 4.0
    COMPUTER_BASE_VEL: float = 2.0
    COMPUTER_ROTATION_VEL: float = 4.0
    LEVEL_VEL_INCREMENT: float = 0.2


# ==================== 游戏类 ====================

class GameInfo:
    """游戏信息管理类"""
    
    def __init__(self, config: GameConfig):
        self.config = config
        self.level = 1
        self.started = False
        self.level_start_time = 0
        self.best_times: List[float] = []
        self.total_time = 0.0
        
    def next_level(self) -> None:
        """进入下一关"""
        if self.started:
            level_time = self.get_level_time()
            self.best_times.append(level_time)
            self.total_time += level_time
        self.level += 1
        self.started = False
        
    def reset(self) -> None:
        """重置游戏"""
        self.level = 1
        self.started = False
        self.level_start_time = 0
        self.best_times = []
        self.total_time = 0.0
        
    def game_finished(self) -> bool:
        """检查是否完成所有关卡"""
        return self.level > self.config.MAX_LEVELS
    
    def start_level(self) -> None:
        """开始当前关卡"""
        self.started = True
        self.level_start_time = pygame.time.get_ticks()
        
    def get_level_time(self) -> float:
        """获取当前关卡用时（秒）"""
        if not self.started:
            return 0.0
        return (pygame.time.get_ticks() - self.level_start_time) / 1000.0


class AbstractCar:
    """汽车基类"""
    
    IMG: pygame.Surface = None
    START_POS: Tuple[int, int] = (0, 0)
    
    def __init__(self, max_vel: float, rotation_vel: float):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0.0
        self.rotation_vel = rotation_vel
        self.angle = 0.0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1
        self._mask: Optional[pygame.mask.Mask] = None
        
    @property
    def mask(self) -> pygame.mask.Mask:
        """懒加载碰撞遮罩"""
        if self._mask is None:
            self._mask = pygame.mask.from_surface(self.img)
        return self._mask
        
    def rotate(self, left: bool = False, right: bool = False) -> None:
        """旋转车辆"""
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel
            
    def draw(self, win: pygame.Surface) -> None:
        """绘制车辆"""
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)
        
    def move_forward(self) -> None:
        """向前移动"""
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()
        
    def move_backward(self) -> None:
        """向后移动"""
        self.vel = max(self.vel - self.acceleration, -self.max_vel / 2)
        self.move()
        
    def move(self) -> None:
        """根据当前速度和角度移动"""
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel
        self.y -= vertical
        self.x -= horizontal
        
    def collide(self, mask: pygame.mask.Mask, x: int = 0, y: int = 0) -> Optional[Tuple[int, int]]:
        """检测与指定遮罩的碰撞"""
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        return mask.overlap(car_mask, offset)
    
    def reset(self) -> None:
        """重置到起始位置"""
        self.x, self.y = self.START_POS
        self.angle = 0.0
        self.vel = 0.0


class PlayerCar(AbstractCar):
    """玩家控制的车辆"""
    
    def reduce_speed(self) -> None:
        """自然减速"""
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()
        
    def bounce(self) -> None:
        """碰撞反弹"""
        self.vel = -self.vel * 0.5  # 反弹时损失一些速度
        self.move()


class ComputerCar(AbstractCar):
    """电脑AI控制的车辆"""
    
    def __init__(self, max_vel: float, rotation_vel: float, path: List[Tuple[int, int]]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel
        
    def draw_points(self, win: pygame.Surface) -> None:
        """绘制路径点（调试用）"""
        for i, point in enumerate(self.path):
            color = (255, 0, 0) if i == self.current_point else (128, 128, 128)
            pygame.draw.circle(win, color, point, 5)
            
    def draw(self, win: pygame.Surface, debug: bool = False) -> None:
        """绘制车辆"""
        super().draw(win)
        if debug:
            self.draw_points(win)
            
    def calculate_angle(self) -> None:
        """计算朝向目标点需要的角度"""
        if self.current_point >= len(self.path):
            return
            
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y
        
        if y_diff == 0:
            desired_radian_angle = math.pi / 2 if x_diff > 0 else -math.pi / 2
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)
            
        if target_y > self.y:
            desired_radian_angle += math.pi
            
        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        
        # 标准化角度差到 [-180, 180]
        while difference_in_angle > 180:
            difference_in_angle -= 360
        while difference_in_angle < -180:
            difference_in_angle += 360
            
        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))
            
    def update_path_point(self) -> None:
        """更新当前目标点"""
        if self.current_point >= len(self.path):
            return
            
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1
            
    def move(self) -> None:
        """AI移动逻辑"""
        if self.current_point >= len(self.path):
            return
            
        self.calculate_angle()
        self.update_path_point()
        super().move()
        
    def next_level(self, level: int) -> None:
        """进入下一关，提升AI速度"""
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.2
        self.current_point = 0


# ==================== 游戏主类 ====================

class CarRacerGame:
    """赛车游戏主类"""
    
    # AI路径点
    AI_PATH = [
        (175, 119), (110, 70), (56, 133), (70, 481), (318, 731), (404, 680),
        (418, 521), (507, 475), (600, 551), (613, 715), (736, 713), (734, 399),
        (611, 357), (409, 343), (433, 257), (697, 258), (738, 123), (581, 71),
        (303, 78), (275, 377), (176, 388), (178, 260)
    ]
    
    FINISH_POSITION = (130, 250)
    
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("赛车游戏 - Car Racer")
        
        self.config = GameConfig()
        self.load_resources()
        self.setup_display()
        self.setup_game_objects()
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        self.debug_mode = False
        
    def load_resources(self) -> None:
        """加载游戏资源"""
        imgs_path = get_resource_path("imgs")
        
        # 加载并缩放图像
        self.grass = scale_image(
            pygame.image.load(os.path.join(imgs_path, "grass.jpg")),
            self.config.GRASS_SCALE
        )
        self.track = scale_image(
            pygame.image.load(os.path.join(imgs_path, "track.png")),
            self.config.TRACK_SCALE
        )
        self.track_border = scale_image(
            pygame.image.load(os.path.join(imgs_path, "track-border.png")),
            self.config.TRACK_SCALE
        )
        self.finish = pygame.image.load(os.path.join(imgs_path, "finish.png"))
        
        # 加载车辆图像
        self.red_car = scale_image(
            pygame.image.load(os.path.join(imgs_path, "red-car.png")),
            self.config.CAR_SCALE
        )
        self.green_car = scale_image(
            pygame.image.load(os.path.join(imgs_path, "green-car.png")),
            self.config.CAR_SCALE
        )
        
        # 创建碰撞遮罩
        self.track_border_mask = pygame.mask.from_surface(self.track_border)
        self.finish_mask = pygame.mask.from_surface(self.finish)
        
        # 加载字体
        self.main_font = pygame.font.SysFont("microsoftyahei", 40)
        self.small_font = pygame.font.SysFont("microsoftyahei", 28)
        self.title_font = pygame.font.SysFont("microsoftyahei", 60)
        
    def setup_display(self) -> None:
        """设置显示窗口"""
        self.width = self.track.get_width()
        self.height = self.track.get_height()
        self.win = pygame.display.set_mode((self.width, self.height))
        
        # 设置背景图像列表
        self.images = [
            (self.grass, (0, 0)),
            (self.track, (0, 0)),
            (self.finish, self.FINISH_POSITION),
            (self.track_border, (0, 0))
        ]
        
    def setup_game_objects(self) -> None:
        """设置游戏对象"""
        # 设置车辆类属性
        PlayerCar.IMG = self.red_car
        PlayerCar.START_POS = (180, 200)
        ComputerCar.IMG = self.green_car
        ComputerCar.START_POS = (150, 200)
        
        # 创建游戏对象
        self.game_info = GameInfo(self.config)
        self.player_car = PlayerCar(
            self.config.PLAYER_MAX_VEL,
            self.config.PLAYER_ROTATION_VEL
        )
        self.computer_car = ComputerCar(
            self.config.COMPUTER_BASE_VEL,
            self.config.COMPUTER_ROTATION_VEL,
            self.AI_PATH
        )
        
    def handle_events(self) -> None:
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                    else:
                        self.running = False
                        
                elif event.key == pygame.K_r:
                    self.reset_game()
                    
                elif event.key == pygame.K_F3:
                    self.debug_mode = not self.debug_mode
                    
                elif self.state == GameState.MENU:
                    self.state = GameState.PLAYING
                    self.game_info.start_level()
                    
                elif self.state in (GameState.GAME_OVER, GameState.GAME_WON):
                    self.reset_game()
                    
    def handle_input(self) -> None:
        """处理玩家输入"""
        if self.state != GameState.PLAYING:
            return
            
        keys = pygame.key.get_pressed()
        moved = False
        
        # 支持 WASD 和方向键
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player_car.rotate(left=True)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player_car.rotate(right=True)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            moved = True
            self.player_car.move_forward()
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            moved = True
            self.player_car.move_backward()
            
        if not moved:
            self.player_car.reduce_speed()
            
    def handle_collision(self) -> None:
        """处理碰撞检测"""
        if self.state != GameState.PLAYING:
            return
            
        # 检测玩家与边界碰撞
        if self.player_car.collide(self.track_border_mask) is not None:
            self.player_car.bounce()
            
        # 检测电脑到达终点
        if self.computer_car.collide(self.finish_mask, *self.FINISH_POSITION) is not None:
            self.state = GameState.GAME_OVER
            
        # 检测玩家到达终点
        player_finish_collide = self.player_car.collide(self.finish_mask, *self.FINISH_POSITION)
        if player_finish_collide is not None:
            if player_finish_collide[1] == 0:
                # 从错误方向到达终点线
                self.player_car.bounce()
            else:
                # 正确到达终点
                self.game_info.next_level()
                self.player_car.reset()
                self.computer_car.next_level(self.game_info.level)
                
                if self.game_info.game_finished():
                    self.state = GameState.GAME_WON
                else:
                    self.state = GameState.MENU
                    
    def update(self) -> None:
        """更新游戏状态"""
        if self.state == GameState.PLAYING:
            self.computer_car.move()
            
    def draw(self) -> None:
        """绘制游戏画面"""
        # 绘制背景
        for img, pos in self.images:
            self.win.blit(img, pos)
            
        # 绘制车辆
        self.player_car.draw(self.win)
        self.computer_car.draw(self.win, self.debug_mode)
        
        # 绘制HUD
        self.draw_hud()
        
        # 绘制状态覆盖层
        self.draw_overlay()
        
        pygame.display.update()
        
    def draw_hud(self) -> None:
        """绘制抬头显示信息"""
        # 创建半透明背景
        hud_surface = pygame.Surface((200, 120), pygame.SRCALPHA)
        hud_surface.fill((0, 0, 0, 128))
        self.win.blit(hud_surface, (5, self.height - 125))
        
        # 关卡信息
        level_text = self.small_font.render(
            f"关卡: {self.game_info.level}/{self.config.MAX_LEVELS}",
            True, (255, 255, 255)
        )
        self.win.blit(level_text, (10, self.height - 120))
        
        # 时间信息
        time_text = self.small_font.render(
            f"用时: {self.game_info.get_level_time():.1f}s",
            True, (255, 255, 255)
        )
        self.win.blit(time_text, (10, self.height - 85))
        
        # 速度信息
        vel_text = self.small_font.render(
            f"速度: {abs(self.player_car.vel):.1f}",
            True, (255, 255, 255)
        )
        self.win.blit(vel_text, (10, self.height - 50))
        
        # 控制提示（右下角）
        hint_surface = pygame.Surface((180, 30), pygame.SRCALPHA)
        hint_surface.fill((0, 0, 0, 128))
        self.win.blit(hint_surface, (self.width - 185, self.height - 35))
        
        hint_text = self.small_font.render("R:重开 ESC:暂停", True, (200, 200, 200))
        self.win.blit(hint_text, (self.width - 180, self.height - 32))
        
    def draw_overlay(self) -> None:
        """绘制状态覆盖层"""
        if self.state == GameState.MENU:
            blit_text_center(
                self.win, self.main_font,
                f"按任意键开始第 {self.game_info.level} 关"
            )
            
        elif self.state == GameState.PAUSED:
            blit_text_center(self.win, self.main_font, "游戏暂停 - 按ESC继续")
            
        elif self.state == GameState.GAME_OVER:
            blit_text_center(self.win, self.title_font, "你输了！", (255, 100, 100))
            # 绘制提示文字
            hint = self.small_font.render("按任意键重新开始", True, (200, 200, 200))
            hint_x = (self.win.get_width() - hint.get_width()) // 2
            hint_y = self.win.get_height() // 2 + 50
            self.win.blit(hint, (hint_x, hint_y))
            
        elif self.state == GameState.GAME_WON:
            blit_text_center(self.win, self.title_font, "恭喜通关！", (100, 255, 100))
            # 显示总用时
            total_time = self.small_font.render(
                f"总用时: {self.game_info.total_time:.1f}秒",
                True, (255, 255, 255)
            )
            time_x = (self.win.get_width() - total_time.get_width()) // 2
            time_y = self.win.get_height() // 2 + 50
            self.win.blit(total_time, (time_x, time_y))
            
    def reset_game(self) -> None:
        """重置游戏"""
        self.game_info.reset()
        self.player_car.reset()
        self.computer_car.reset()
        self.computer_car.current_point = 0
        self.computer_car.vel = self.config.COMPUTER_BASE_VEL
        self.state = GameState.MENU
        
    def run(self) -> None:
        """运行游戏主循环"""
        while self.running:
            self.clock.tick(self.config.FPS)
            self.handle_events()
            self.handle_input()
            self.update()
            self.handle_collision()
            self.draw()
            
        pygame.quit()
        sys.exit()


# ==================== 程序入口 ====================

def main():
    """主函数入口"""
    game = CarRacerGame()
    game.run()


if __name__ == "__main__":
    main()
