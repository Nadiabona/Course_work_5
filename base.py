from unit import BaseUnit


class BaseSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Arena(metaclass=BaseSingleton):
    STAMINA_PER_ROUND = 1
    player = None
    enemy = None
    game_is_running = False
    battle_result = None

    def game_start(self, player: BaseUnit, enemy: BaseUnit):
        self.player = player
        self.enemy = enemy
        self.game_is_running = True

    def _check_players_hp(self):
        """Проверка здоровья игроков"""

        if self.player.hp <= 0 and self.enemy.hp <= 0:
            self.battle_result = 'Ничья'

        if self.player.hp <= 0:
            self.battle_result = 'Игрок повержен! Враг победил!'

        if self.enemy.hp <= 0:
            self.battle_result = 'Враг повержен! Игрок победил!'

        if self.battle_result:
            return self._end_game()

    def _stamina_regeneration(self):
        """Регенерация здоровья и стамины (выносливость) для игрока и врага за ход"""

        if self.player.stamina + self.STAMINA_PER_ROUND > self.player.unit_class.max_stamina:
            self.player.stamina = self.player.unit_class.max_stamina

        elif self.player.stamina < self.player.unit_class.max_stamina:
            self.player.stamina += self.STAMINA_PER_ROUND

        if self.enemy.stamina + self.STAMINA_PER_ROUND > self.enemy.unit_class.max_stamina:
            self.enemy.stamina = self.enemy.unit_class.max_stamina

        elif self.enemy.stamina < self.enemy.unit_class.max_stamina:
            self.enemy.stamina += self.STAMINA_PER_ROUND

    def next_turn(self):
        """Следующий ход срабатывает если игрок пропускает ход или когда игрок наносит удар."""

        #  проверяем здоровье игрока
        result = self._check_players_hp()

        # если result -> возвращаем его
        if result:
            return result

        # если же результата пока нет и после завершения хода игра может быть продожена,
        # тогда запускаем процесс регенирации стамины и здоровья для игроков (self._stamina_regeneration)
        # и вызываем функцию self.enemy.hit(self.player) - ответный удар врага

        self._stamina_regeneration()

        return self.enemy.hit(self.player)

    def _end_game(self) -> str:
        """Кнопка завершения игры"""

        # очищаем синглтон
        self._instances = {}

        # останавливаем игру
        result = self.battle_result
        self.game_is_running = False
        return result

    def player_hit(self) -> str:
        """Кнопка удара игрока"""

        result = self.player.hit(self.enemy)
        return f"{result} {self.next_turn()}"

    def player_use_skill(self):
        """Кнопка использования умения """

        result = self._check_players_hp()
        if result:
            return result

        return f"{result} {self.next_turn()}"
