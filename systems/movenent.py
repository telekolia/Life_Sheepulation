import random

class Movement:
    @staticmethod
    def _can_move_to(x, y, entities, map):
        # print(f"=== DEBUG _can_move_to ===")
        # print(f"x={x}, y={y}")
        # print(f"Тип map: {type(map)}")
        # print(f"Длина map: {len(map) if isinstance(map, (list, dict)) else 'N/A'}")
        
        # if isinstance(map, list):
        #     print(f"map существует? {x < len(map)}")
        #     if x < len(map):
        #         print(f"map[{x}] тип: {type(map[x])}")
        #         print(f"map[{x}] длина: {len(map[x]) if isinstance(map[x], (list, dict)) else 'N/A'}")
        #         print(f"y={y} в пределах? {y < len(map[x]) if isinstance(map[x], list) else y in map[x] if isinstance(map[x], dict) else 'N/A'}")
        
        # elif isinstance(map, dict):
        #     print(f"Ключи в map: {list(map.keys())}")
        #     print(f"x={x} есть в map? {x in map}")
        #     if x in map:
        #         print(f"map[{x}] тип: {type(map[x])}")
        #         if isinstance(map[x], dict):
        #             print(f"Ключи в map[{x}]: {list(map[x].keys())}")
        #             print(f"y={y} есть в map[{x}]? {y in map[x]}")


        if x < 0 or y < 0 or x >= len(map) or y >= len(map):
            return False

        if not map[x][y]['Tile'].is_passable:
            print('Да я сука')
            return False

        for other in entities.values():
            if 'Position' in other and 'Tile' not in other:
                if (other['Position'].x == x and other['Position'].y == y and 'Plant' not in other):
                    print('сюда')
                    return False
        print('Успешно')
        return True

    @staticmethod
    def _move_towards(entity, entities, target_pos, map):
        pos = entity['Position']
        # Вычисляем направление
        dx = 0
        dy = 0

        if pos.x < target_pos.x:
            dx = 1
        elif pos.x > target_pos.x:
            dx = -1

        if pos.y < target_pos.y:
            dy = 1
        elif pos.y > target_pos.y:
            dy = -1

        # Чтобы глазки не болели не двигаемся по диагонали
        new_x = pos.x
        new_y = pos.y

        if dx != 0 and Movement._can_move_to(pos.x + dx, pos.y, entities, map):
            new_x = pos.x + dx
        elif dy != 0 and Movement._can_move_to(pos.x, pos.y + dy, entities, map):
            new_y = pos.y + dy

        # Обновляем позицию
        if new_x != pos.x or new_y != pos.y:
            entity['Position'].x = new_x
            entity['Position'].y = new_y

            # Тратим энергию на движение
            if 'Hunger' in entity:
                entity['Hunger'].current_satiety -= 0.1

    @staticmethod
    def _random_move(entity, entities, map):
        """Случайное блуждание"""
        print('пытаюсь')
        pos = entity['Position']
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)

        for dx, dy in directions:
            (new_x, new_y) = (pos.x + dx, pos.y + dy)

            if Movement._can_move_to(new_x, new_y, entities, map):
                (pos.x, pos.y) = (new_x, new_y)
            else:
                print('пиздец нахуй')

                # Тратим энергию
                if 'Hunger' in entity:
                    entity['Hunger'].current_satiety -= 0.05
                break