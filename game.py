import tkinter as tk
from tkinter import messagebox
import random
import tkinter.ttk as ttk


# Класс карты
class Map:
    def __init__(self, canvas):
        self.canvas = canvas
        self.rooms = []
        self.obstacles = []
        self.generate_map()

    def generate_map(self):
        for room in self.rooms:
            self.canvas.delete(room)
        for obstacle in self.obstacles:
            self.canvas.delete(obstacle)
        self.rooms.clear()
        self.obstacles.clear()

        map_layout = self.get_random_map_layout()
        for room_coords in map_layout["rooms"]:
            room = self.canvas.create_rectangle(*room_coords, fill="gray", outline="", tags="map")
            self.rooms.append(room)
        for obstacle_coords in map_layout["obstacles"]:
            obstacle = self.canvas.create_rectangle(*obstacle_coords, fill="brown", outline="", tags="map")
            self.obstacles.append(obstacle)

        self.canvas.tag_lower("map")

    def get_random_map_layout(self):
        layouts = [
            {
                "rooms": [
                    (50, 50, 350, 250),
                    (450, 50, 750, 250),
                    (50, 350, 350, 550),
                    (450, 350, 750, 550)
                ],
                "obstacles": [
                    (200, 200, 250, 250),
                    (600, 400, 650, 450)
                ]
            },
            {
                "rooms": [
                    (100, 100, 300, 300),
                    (500, 100, 700, 300),
                    (100, 400, 300, 600),
                    (500, 400, 700, 600)
                ],
                "obstacles": [
                    (350, 150, 400, 200),
                    (450, 450, 500, 500)
                ]
            }
        ]
        return random.choice(layouts)

    def check_collision(self, position, size):
        x, y = position
        for room in self.rooms:
            coords = self.canvas.coords(room)
            if (coords[0] < x - size < coords[2] and
                coords[1] < y - size < coords[3]):
                return False
        for obstacle in self.obstacles:
            coords = self.canvas.coords(obstacle)
            if (coords[0] < x + size < coords[2] and
                coords[1] < y + size < coords[3]):
                return True
        return False


# Класс игрока
class Player:
    def __init__(self, canvas, info_label, exp_bar):
        self.health = 100
        self.attack = 5
        self.experience = 0
        self.level = 1
        self.position = [400, 300]
        self.size = 20
        self.canvas = canvas
        self.player_id = canvas.create_oval(
            self.position[0] - self.size // 2,
            self.position[1] - self.size // 2,
            self.position[0] + self.size // 2,
            self.position[1] + self.size // 2,
            fill="black",
            tags="player"
        )
        self.shoot_cooldown = 0
        self.bullet_size = 5
        self.info_label = info_label
        self.exp_bar = exp_bar
        self.abilities = []
        self.is_leveling_up = False  # Флаг для предотвращения множественных вызовов level_up
        self.update_info()

    def move(self, dx, dy):
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy
        if not game_map.check_collision([new_x, new_y], self.size // 2):
            if 0 <= new_x <= 800 and 0 <= new_y <= 600:
                self.position = [new_x, new_y]
                self.canvas.coords(self.player_id,
                                   self.position[0] - self.size // 2,
                                   self.position[1] - self.size // 2,
                                   self.position[0] + self.size // 2,
                                   self.position[1] + self.size // 2)

    def shoot(self, x, y):
        if self.shoot_cooldown <= 0:
            mouse_x, mouse_y = x, y
            player_x, player_y = self.position
            dx = mouse_x - player_x
            dy = mouse_y - player_y
            distance = (dx**2 + dy**2)**0.5
            if distance != 0:
                direction = (dx / distance, dy / distance)
                bullet = Bullet(self.canvas, player_x, player_y, direction, self.bullet_size)
                bullets.append(bullet)
                self.shoot_cooldown = 20

    def update_cooldown(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.game_over()
        else:
            self.update_info()

    def add_experience(self, amount):
        self.experience += amount
        self.exp_bar["value"] = self.experience  # Обновляем значение шкалы опыта
        if self.experience >= 100 and not self.is_leveling_up:  # Проверяем флаг is_leveling_up
            self.level_up()

    def level_up(self):
        self.is_leveling_up = True  # Устанавливаем флаг
        self.level += 1
        self.experience = 0  # Сбрасываем опыт
        self.exp_bar["value"] = 0  # Сбрасываем шкалу опыта
        messagebox.showinfo("Level Up!", f"Вы достигли уровня {self.level}! Выберите способность:")
        self.create_ability_buttons()

    def game_over(self):
        global is_game_over
        is_game_over = True
        for widget in root.winfo_children():
            widget.destroy()
        result_label = tk.Label(root, text=f"Game Over! Level: {self.level}", font=("Arial", 16))
        result_label.pack(pady=20)
        restart_button = tk.Button(root, text="Restart", command=restart_game)
        restart_button.pack(pady=10)

    def apply_ability(self, ability):
        if ability == "Increase Health":
            self.health += 20
        elif ability == "Increase Attack":
            self.attack += 5
        elif ability == "Decrease Reload Time":
            self.shoot_cooldown = max(0, self.shoot_cooldown - 5)
        elif ability == "Increase Bullet Speed":
            for bullet in bullets:
                bullet.speed += 2
        elif ability == "Increase Bullet Size":
            self.bullet_size += 5
            for bullet in bullets:
                coords = bullet.canvas.coords(bullet.bullet_id)
                x_center = (coords[0] + coords[2]) / 2
                y_center = (coords[1] + coords[3]) / 2
                bullet.canvas.coords(bullet.bullet_id,
                                     x_center - self.bullet_size, y_center - self.bullet_size,
                                     x_center + self.bullet_size, y_center + self.bullet_size)
        elif ability == "Increase Damage":
            self.attack += 5
        self.abilities.append(ability)
        self.update_info()

    def update_info(self):
        abilities_text = ", ".join(self.abilities) if self.abilities else "None"
        self.info_label.config(text=f"Health: {self.health} | Level: {self.level} | Experience: {self.experience}/100 | Abilities: {abilities_text}")

    def create_ability_buttons(self):
        for widget in ability_frame.winfo_children():
            widget.destroy()
        abilities = ["Increase Health", "Increase Attack", "Decrease Reload Time", "Increase Bullet Speed", "Increase Bullet Size", "Increase Damage"]
        for ability in abilities:
            button = tk.Button(ability_frame, text=ability, command=lambda a=ability: self.apply_ability_and_spawn(a))
            button.pack(side=tk.LEFT, padx=5)

    def apply_ability_and_spawn(self, ability):
        self.apply_ability(ability)
        for widget in ability_frame.winfo_children():
            widget.destroy()
        spawn_new_room_and_monsters()
        self.is_leveling_up = False  # Сбрасываем флаг после выбора способности


# Класс пули
class Bullet:
    def __init__(self, canvas, x, y, direction, size):
        self.speed = 10
        self.direction = direction
        self.canvas = canvas
        self.size = size
        self.bullet_id = canvas.create_oval(x - self.size, y - self.size, x + self.size, y + self.size, fill="red", tags="bullet")

    def update(self):
        self.canvas.move(self.bullet_id, self.direction[0] * self.speed, self.direction[1] * self.speed)
        coords = self.canvas.coords(self.bullet_id)
        if not (0 <= coords[0] <= 800 and 0 <= coords[1] <= 600):
            self.canvas.delete(self.bullet_id)
            return False
        return True


# Класс монстра
class Monster:
    def __init__(self, canvas, x, y):
        self.health = 20
        self.canvas = canvas
        self.size = 20
        self.monster_id = canvas.create_oval(
            x - self.size // 2, y - self.size // 2,
            x + self.size // 2, y + self.size // 2,
            fill="green",
            tags="monster"
        )
        self.position = [x, y]
        self.speed = 2

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.canvas.delete(self.monster_id)
            return True
        return False

    def move_towards_player(self, player_position, monsters):
        target_x, target_y = player_position
        current_x, current_y = self.position
        dx = target_x - current_x
        dy = target_y - current_y
        distance = (dx**2 + dy**2)**0.5
        if distance != 0:
            direction_x = dx / distance
            direction_y = dy / distance
        else:
            direction_x = 0
            direction_y = 0

        new_x = current_x + direction_x * self.speed
        new_y = current_y + direction_y * self.speed

        if 0 <= new_x <= 800 and 0 <= new_y <= 600:
            collision = False
            for monster in monsters:
                if monster != self:
                    monster_coords = canvas.coords(monster.monster_id)
                    mx1, my1, mx2, my2 = monster_coords
                    monster_center_x = (mx1 + mx2) / 2
                    monster_center_y = (my1 + my2) / 2
                    distance_to_other_monster = ((new_x - monster_center_x)**2 + (new_y - monster_center_y)**2)**0.5
                    if distance_to_other_monster < self.size:
                        collision = True
                        break
            if not collision:
                self.position = [new_x, new_y]
                self.canvas.coords(self.monster_id,
                                   self.position[0] - self.size // 2,
                                   self.position[1] - self.size // 2,
                                   self.position[0] + self.size // 2,
                                   self.position[1] + self.size // 2)


# Генерация комнаты
def generate_room(canvas, num_monsters=10):
    monsters = []
    for _ in range(num_monsters):
        while True:
            x = random.randint(50, 750)
            y = random.randint(50, 550)
            collision = False
            for monster in monsters:
                monster_coords = canvas.coords(monster.monster_id)
                mx1, my1, mx2, my2 = monster_coords
                monster_center_x = (mx1 + mx2) / 2
                monster_center_y = (my1 + my2) / 2
                distance_to_other_monster = ((x - monster_center_x)**2 + (y - monster_center_y)**2)**0.5
                if distance_to_other_monster < 40:
                    collision = True
                    break
            if not collision:
                break
        monster = Monster(canvas, x, y)
        monsters.append(monster)
    return monsters


# Спавн новых мобов и комнаты
def spawn_new_room_and_monsters():
    global monsters
    game_map.generate_map()  # Генерация новой карты
    monsters = generate_room(canvas)  # Спавн новых мобов
    update_game()  # Продолжение игры


# Обновление игры
def update_game():
    if is_game_over:
        return

    dx, dy = 0, 0
    if keys_pressed['Up']:
        dy -= 10
    if keys_pressed['Down']:
        dy += 10
    if keys_pressed['Left']:
        dx -= 10
    if keys_pressed['Right']:
        dx += 10
    if dx != 0 or dy != 0:
        player.move(dx, dy)
    player.update_cooldown()

    for bullet in bullets[:]:
        if not bullet.update():
            bullets.remove(bullet)
        else:
            for monster in monsters[:]:
                bullet_coords = canvas.coords(bullet.bullet_id)
                bx1, by1, bx2, by2 = bullet_coords
                bullet_center_x = (bx1 + bx2) / 2
                bullet_center_y = (by1 + by2) / 2

                monster_coords = canvas.coords(monster.monster_id)
                mx1, my1, mx2, my2 = monster_coords
                monster_center_x = (mx1 + mx2) / 2
                monster_center_y = (my1 + my2) / 2

                distance_to_monster = ((bullet_center_x - monster_center_x)**2 + (bullet_center_y - monster_center_y)**2)**0.5
                if distance_to_monster < (bullet.size + monster.size // 2):
                    if monster.take_damage(player.attack):
                        monsters.remove(monster)
                        player.add_experience(10)  # Добавляем опыт за уничтожение монстра
                        bullets.remove(bullet)
                        canvas.delete(bullet.bullet_id)
                    break

    for monster in monsters:
        monster.move_towards_player(player.position, monsters)
        distance_to_player = ((monster.position[0] - player.position[0])**2 + (monster.position[1] - player.position[1])**2)**0.5
        if distance_to_player < (player.size // 2 + monster.size // 2):
            player.take_damage(5)

    if not monsters:
        player.level_up()

    root.after(50, update_game)


# Перезапуск игры
def restart_game():
    global player, bullets, monsters, keys_pressed, is_game_over, game_map
    is_game_over = False
    for widget in root.winfo_children():
        widget.destroy()
    main()


# Основная функция
def main():
    global root, canvas, info_label, ability_frame, start_button, player, bullets, monsters, keys_pressed, game_map, is_game_over, exp_bar

    root = tk.Tk()
    root.title("Roguelike Game")
    canvas = tk.Canvas(root, width=800, height=600, bg="white")
    canvas.pack()

    game_map = Map(canvas)

    info_label = tk.Label(root, text="Health: 100 | Level: 1 | Experience: 0/100 | Abilities: None", font=("Arial", 12))
    info_label.pack()

    # Шкала опыта
    exp_bar = ttk.Progressbar(root, length=200, mode="determinate", maximum=100)
    exp_bar.pack(pady=5)

    ability_frame = tk.Frame(root)
    ability_frame.pack()

    keys_pressed = {'Up': False, 'Down': False, 'Left': False, 'Right': False}
    is_game_over = False

    def on_key_press(event):
        if event.keysym in keys_pressed:
            keys_pressed[event.keysym] = True

    def on_key_release(event):
        if event.keysym in keys_pressed:
            keys_pressed[event.keysym] = False

    def shoot(event):
        player.shoot(event.x, event.y)

    def start_game():
        global player, bullets, monsters
        start_button.destroy()
        player = Player(canvas, info_label, exp_bar)
        bullets = []
        monsters = []
        root.bind("<KeyPress>", on_key_press)
        root.bind("<KeyRelease>", on_key_release)
        root.bind("<Button-1>", shoot)
        canvas.focus_set()
        spawn_new_room_and_monsters()  # Спавн первой комнаты и мобов

    start_button = tk.Button(root, text="Start Game", command=start_game)
    start_button.pack()

    root.mainloop()


if __name__ == "__main__":
    main()