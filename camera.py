import pygame
from pygame.math import Vector2

class Camera:
    def __init__(self, pos, size, zoom):
        self.pos = Vector2(pos)
        self.size = Vector2(size)
        self.zoom = zoom
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.zoom_speed = 0.1
        self.move_speed = 5

    def process(self, event):
        if event.type == pygame.MOUSEWHEEL:
            # Изменение зума колесиком мыши
            zoom_change = self.zoom_speed * event.y
            new_zoom = self.zoom + zoom_change
            
            # Ограничение зума
            if self.min_zoom <= new_zoom <= self.max_zoom:
                self.zoom = new_zoom
                    
        keys = pygame.key.get_pressed()
        
        # Движение вверх (W)
        if keys[pygame.K_w]:
            self.pos.y -= self.move_speed / self.zoom
        
        # Движение вниз (S)
        if keys[pygame.K_s]:
            self.pos.y += self.move_speed / self.zoom
        
        # Движение влево (A)
        if keys[pygame.K_a]:
            self.pos.x -= self.move_speed / self.zoom
        
        # Движение вправо (D)
        if keys[pygame.K_d]:
            self.pos.x += self.move_speed / self.zoom


    def world_to_screen(self, world_pos):
        """Преобразование мировых координат в экранные"""
        screen_pos = Vector2(world_pos) - self.pos
        screen_pos *= self.zoom
        return screen_pos

    def screen_to_world(self, screen_pos):
        """Преобразование экранных координат в мировые"""
        world_pos = Vector2(screen_pos) - Vector2(self.size) * 0.5
        world_pos /= self.zoom
        world_pos += self.pos
        return world_pos

    def get_transform_matrix(self):
        """Получить матрицу трансформации для отрисовки"""
        matrix = pygame.Surface((self.size[0], self.size[1]), pygame.SRCALPHA)
        
        # Масштабирование
        scaled_width = int(self.size[0] * self.zoom)
        scaled_height = int(self.size[1] * self.zoom)
        
        return {
            'surface': matrix,
            'scale': self.zoom,
            'offset': self.pos,
            'scaled_size': (scaled_width, scaled_height)
        }

    def get_view_rect(self):
        """Получить прямоугольник видимой области в мировых координатах"""
        half_width = self.size[0] / (2 * self.zoom)
        half_height = self.size[1] / (2 * self.zoom)
        
        return pygame.Rect(
            self.pos.x - half_width,
            self.pos.y - half_height,
            half_width * 2,
            half_height * 2
        )

    def follow(self, target_pos, smoothness=0.1):
        """Плавное следование за целью"""
        self.pos = self.pos.lerp(target_pos, smoothness)

    def zoom_to_point(self, point, zoom_change):
        """Увеличение/уменьшение с фиксацией на определенной точке"""
        # Сохраняем мировую позицию точки до изменения зума
        world_point_before = self.screen_to_world(point)
        
        # Изменяем зум
        new_zoom = self.zoom + zoom_change
        if self.min_zoom <= new_zoom <= self.max_zoom:
            self.zoom = new_zoom
            
            # Корректируем позицию камеры чтобы точка оставалась на месте
            world_point_after = self.screen_to_world(point)
            self.pos += world_point_after - world_point_before

    def reset(self, pos=None, zoom=1.0):
        """Сброс камеры к начальным параметрам"""
        if pos:
            self.pos = Vector2(pos)
        self.zoom = zoom