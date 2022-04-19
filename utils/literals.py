class Info:
    COMMANDS_HINT = "Используйте одну из следующих команд:\n/order - сделать новый заказ\n/me - просмотреть ваш профиль"


class Symbols:
    NEXT = ">"
    PREVIOUS = "<"
    BORDER = "×"


class OrderState:
    def __init__(self, category: str, choose: str, next_category: str):
        self.category = category
        self.choose = choose
        self.next_category = next_category


class OrderStates:
    MAIN_DISH = OrderState("main_dish", "основное блюдо", "Закуски")
    SNACK = OrderState("snack", "закуску", "Напитки")
    DRINK = OrderState("drink", "напиток", "Оформление заказа")
