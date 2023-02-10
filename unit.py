from __future__ import annotations
from abc import ABC, abstractmethod
from equipment import Equipment, Weapon, Armor
from classes import UnitClass
from random import randint
from typing import Optional


class BaseUnit(ABC):
    """
    Базовый класс
    """
    def __init__(self, name: str, unit_class: UnitClass):
        """
        Инициализируем класса Unit используем свойства класса UnitClass
        """
        self.name = name
        self.unit_class = unit_class
        self.hp = unit_class.max_health
        self.stamina = unit_class.max_stamina
        self.weapon = None
        self.armor = None
        self._is_skill_used = False

    @property
    def health_points(self):
        """Возвращает уровень hp"""
        return round(self.hp, 1)

    @property
    def stamina_points(self):
        """Возвращает уровень  stamina"""
        return round(self.stamina, 1)

    def equip_weapon(self, weapon: Weapon):
        """ Даем оружие"""
        self.weapon = weapon
        return f"{self.name} Вооружен оружием {self.weapon.name}"

    def equip_armor(self, armor: Armor):
        """Даем броню"""
        self.armor = armor
        return f"{self.name} Экипирован броней {self.weapon.name}"

    def _count_damage(self, target: BaseUnit) -> int:
        """Рассчитываем урон, нанесенный игроком"""
        damage = self.weapon.damage * self.unit_class.attack

        #"""Понижаем выносливость атакующего после удара""
        self.stamina -= self.weapon.stamina_per_hit

        #  если у защищающегося надостаточно stamoina, его броня игнорируется
        #  рассчитываем наносимый - target.get_damage(damage)
        #  и возвращаем предполагаемый урон для последующего вывода пользователю
        if target.stamina >= target.armor.stamina_per_turn:
            target_armor = target.armor.defence * target.unit_class.armor
            target.stamina -= target.armor.stamina_per_turn
            damage -= target_armor

        return target.get_damage(damage)

    def get_damage(self, damage: int) -> Optional[int]:
        """получение урона целью"""
        damage = round(damage, 1)
        if damage > 0:
            self.hp -= damage
            return damage
        return None

    @abstractmethod
    def hit(self, target: BaseUnit) -> str:
        """
        этот метод будет переопределен ниже
        """
        pass

    def use_skill(self, target: BaseUnit) -> str:
        """
        метод использования умения.
        если умение уже использовано возвращаем Навык использован
        Если же умение не использовано тогда выполняем функцию
        self.unit_class.skill.use(user=self, target=target)
        и уже эта функция вернем нам строку которая характеризует выполнение умения
        """
        if self._is_skill_used:
            return 'Навык использован'
        self._is_skill_used = True
        return self.unit_class.skill.use(user=self, target=target)


class PlayerUnit(BaseUnit):

    def hit(self, target: BaseUnit) -> str:
        """
        функция удар игрока:
        здесь происходит проверка достаточно ли выносливости для нанесения удара.
        вызывается функция self._count_damage(target)
        а также возвращается результат в виде строки
        """

        if self.stamina < self.weapon.stamina_per_hit:
            return f"{self.name} Попытался использовать {self.weapon.name}, но у него не хватило выносливости."

        damage = self._count_damage(target)
        if damage > 0:
            return f"{self.name} Используя {self.weapon.name} пробивает {target.armor.name} соперника и наносит {damage} урона."

        if damage == 0:
            return f"{self.name} Используя {self.weapon.name} наносит удар, но {target.armor.name} cоперника его останавливает."


class EnemyUnit(BaseUnit):

    def hit(self, target: BaseUnit) -> str:
        """
        функция удар соперника
        должна содержать логику применения соперником умения
        (он должен делать это автоматически и только 1 раз за бой).
        Например, для этих целей можно использовать функцию randint из библиотеки random.
        Если умение не применено, противник наносит простой удар, где также используется
        функция _count_damage(target)
        """
        stamina_to_hit = self.weapon.stamina_per_hit * self.unit_class.stamina
        damage = self._count_damage(target)

        # умение можно использовать только 1 раз за бой при достаточном уровне выносливости
        # вероятность успешного использования умения противником составляет 10%
        if not self._is_skill_used and self.stamina >= self.unit_class.skill.stamina and randint(0, 100) < 10:
            self.use_skill(target)


        if damage > 0:
            return f"{self.name} используя {self.weapon.name} пробивает {target.armor.name} и наносит Вам {damage} урона."

        if damage == 0:
            return f"{self.name} используя {self.weapon.name} наносит удар, но Ваш(а) {target.armor.name} его останавливает."

        if self.stamina < stamina_to_hit:
            return f"{self.name} попытался использовать {self.weapon.name}, но у него не хватило выносливости."

