import pygame
from math import floor

class HUD():

    def __init__(self, tile_size=64):
        self.tile_size = tile_size
        self.bar_width = tile_size - 12  # Чуть уже чем тайл
        self.bar_height = 5
        self.bar_spacing = 1
        self.offset_y = -4  # Насколько выше сущности рисовать

        # Цвета
        self.health_color = (220, 50, 50)      # Красный
        self.satiety_color = (240, 200, 30)    # Ярко-желтый
        self.growth_color = (50, 200, 50)      # Зелёный
        self.background_color = (40, 40, 40)   # Темно-серый фон
        self.border_color = (20, 20, 20)       # Черная граница
        self.dead_color = (100, 100, 100)      # Серый для мертвых

        # Для анимации
        self.anim_values = {}  # entity_id -> текущее анимированное значение

    def draw(self, surface, entities):
        for entity in entities:
            self._draw_entity_hud(surface, entity)

    def _draw_entity_hud(self, surface, entity):
        if 'Position' not in entity:
            return

        pos = entity['Position']
        screen_x = pos.x * self.tile_size
        screen_y = pos.y * self.tile_size

        # Для овец
        if entity.get('type') == 'sheep':
            self._draw_sheep_hud(surface, entity, screen_x, screen_y)
        # Для кустов
        elif 'Plant' in entity:
            self._draw_plant_hud(surface, entity, screen_x, screen_y)

    def _draw_sheep_hud(self, surface, entity, x, y):
        entity_id = id(entity)

        if 'state' in entity:
            state = entity['state']
            state_font = pygame.font.Font(None, 20)  # Очень маленький шрифт
            state_text = state_font.render(state.upper(), True, (220, 220, 220))

            # Позиция: выше полосок здоровья
            text_x = x + (self.tile_size - state_text.get_width()) // 2
            text_y = y + self.offset_y - 20
            surface.blit(state_text, (text_x, text_y))

    # Отображаем target_id слева от овцы
        if 'target_id' in entity and entity['target_id'] is not None:
            target_font = pygame.font.Font(None, 14)
            target_text = target_font.render(f"target: {entity['target_id']}", True, (180, 220, 255))
            # Позиция слева от овцы
            target_x = x + (self.tile_size - target_text.get_width()) / 2
            target_y = y + 4
            surface.blit(target_text, (target_x, target_y))

        # Рисуем здоровье
        if 'Health' in entity:
            health = entity['Health']

            # Для мертвых овец рисуем серую полоску
            if not health.is_alive:
                bar_y = y + self.offset_y
                self._draw_simple_bar(surface, x, bar_y, 0, 1, self.dead_color, "DEAD")
                return

            # Анимированное значение здоровья
            anim_key = f"{entity_id}_health"
            if anim_key not in self.anim_values:
                self.anim_values[anim_key] = health.current_hp

            # Плавное изменение
            target = health.current_hp
            current = self.anim_values[anim_key]
            if abs(current - target) > 0.1:
                if current < target:
                    self.anim_values[anim_key] = min(current + 1, target)
                else:
                    self.anim_values[anim_key] = max(current - 1, target)

            current_hp = health.current_hp
            # Рисуем шкалу здоровья
            bar_y = y + self.offset_y
            self._draw_simple_bar(surface, x, bar_y, current_hp, health.max_hp, self.health_color)

        # Рисуем сытость
        if 'Hunger' in entity:
            hunger = entity['Hunger']

            # Анимированное значение сытости
            anim_key = f"{entity_id}_hunger"
            if anim_key not in self.anim_values:
                self.anim_values[anim_key] = hunger.current_satiety

            # Плавное изменение
            target = hunger.current_satiety
            current = self.anim_values[anim_key]
            if abs(current - target) > 0.1:
                if current < target:
                    self.anim_values[anim_key] = min(current + 0.5, target)
                else:
                    self.anim_values[anim_key] = max(current - 0.5, target)

            current_satiety = self.anim_values[anim_key]

            # Рисуем шкалу сытости выше здоровья
            bar_y = y + self.offset_y - self.bar_height - self.bar_spacing
            self._draw_simple_bar(surface, x, bar_y, current_satiety, hunger.max_satiety, self.satiety_color)

        # Индикатор беременности
        if ('State' in entity and entity['State'].state == "pregnant" and
            'Health' in entity and entity['Health'].is_alive):
            self._draw_pregnancy_indicator(surface, x, y)

    def _draw_plant_hud(self, surface, entity, x, y):
        """Отрисовать HUD для растения"""
        if 'Plant' in entity:
            plant = entity['Plant']

            # Рисуем прогресс роста
            if not plant.is_mature:
                # Зеленая шкала роста
                growth_percent = min(plant.growth_stage / plant.growth_time, 1.0)
                bar_y = y + 38
                self._draw_simple_bar(surface, x, bar_y,
                                     plant.growth_stage, plant.growth_time,
                                     self.growth_color, "Growing")

    def _draw_simple_bar(self, surface, x, y, current, maximum, color, label=""):
        """Нарисовать простую шкалу без анимации"""
        # Центрируем
        bar_x = x + (self.tile_size - self.bar_width) // 2

        # Фон
        bg_rect = pygame.Rect(bar_x, y, self.bar_width, self.bar_height)
        pygame.draw.rect(surface, self.background_color, bg_rect)

        # Заполнение
        if maximum > 0:
            fill_width = int((current / maximum) * self.bar_width)
            fill_width = max(0, min(fill_width, self.bar_width))

            if fill_width > 0:
                fill_rect = pygame.Rect(bar_x, y, fill_width, self.bar_height)
                pygame.draw.rect(surface, color, fill_rect)

        # Текст метки (если место есть и нужен)
        if label and self.bar_width > 40:
            font = pygame.font.Font(None, 10)
            text = font.render(label, True, (255, 255, 255))
            text_rect = text.get_rect(center=bg_rect.center)
            surface.blit(text, text_rect)

    def _draw_pregnancy_indicator(self, surface, x, y):
        """Нарисовать индикатор беременности"""
        indicator_y = y + self.offset_y - (self.bar_height + self.bar_spacing) * 3
        center_x = x + self.tile_size // 2

        # Розовый сердечок
        pygame.draw.circle(surface, (255, 105, 180), (center_x, indicator_y), 4)
        pygame.draw.circle(surface, (255, 255, 255), (center_x, indicator_y), 4, 1)

    def draw_stats(self, surface, entities, x, y):
        """Отрисовать статистику в углу экрана"""
        stats = self._calculate_stats(entities)

        # Фон
        bg_width = 180
        bg_height = 130
        bg_rect = pygame.Rect(x, y, bg_width, bg_height)
        pygame.draw.rect(surface, (30, 30, 30, 220), bg_rect, border_radius=5)
        pygame.draw.rect(surface, (80, 80, 80), bg_rect, 1, border_radius=5)

        # Заголовок
        font = pygame.font.Font(None, 22)
        title = font.render("СТАТИСТИКА", True, (255, 255, 200))
        surface.blit(title, (x + 10, y + 5))

        # Статистика
        font = pygame.font.Font(None, 18)
        lines = [
            f"Овец всего: {stats['total']}",
            f"Живых: {stats['alive']}",
            f"Голодных: {stats['hungry']}",
            f"Беременных: {stats['pregnant']}",
            f"Кустов: {stats['bushes']}",
            f"С ягодами: {stats['with_berries']}"
        ]

        for i, line in enumerate(lines):
            text = font.render(line, True, (220, 220, 220))
            surface.blit(text, (x + 10, y + 30 + i * 16))

    def _calculate_stats(self, entities):
        """Посчитать статистику по сущностям"""
        stats = {
            'total': 0,
            'alive': 0,
            'hungry': 0,
            'pregnant': 0,
            'bushes': 0,
            'with_berries': 0
        }

        for entity in entities:
            # Овцы
            if entity.get('type') == 'sheep':
                stats['total'] += 1

                if 'Health' in entity and entity['Health'].is_alive:
                    stats['alive'] += 1

                    # Голодные (сытость < 30%)
                    if 'Hunger' in entity:
                        hunger = entity['Hunger']
                        if hunger.current_satiety < hunger.max_satiety * 0.3:
                            stats['hungry'] += 1

                    # Беременные
                    if 'State' in entity and entity['State'].state == "pregnant":
                        stats['pregnant'] += 1

            # Кусты
            elif 'Plant' in entity:
                stats['bushes'] += 1
                if entity['Plant'].is_mature:
                    stats['with_berries'] += 1

        return stats
