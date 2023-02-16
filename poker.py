from random import randint


class Poker:
    def __init__(self):
        self.unused_cards = []  # 未使用的牌
        suits = ['♤', '♡', '♢', '♧']  # 花色
        points = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']  # 点数
        for suit in suits:
            for point in points:
                self.unused_cards.append(suit + point)

    def deal(self, count: int) -> list[str]:  # 发牌
        cards = []
        for i in range(0, count):
            rand_num = randint(0, len(self.unused_cards) - 1)
            cards.append(self.unused_cards[rand_num])
            self.unused_cards.pop(rand_num)
        return cards


def get_point_sum(cards: list[str]) -> int:  # 计算点数合计
    point = 0
    for card in cards:
        try:
            point = point + int(card.replace(card[0], ''))
        except:
            point = point + 10 \
                if card.replace(card[0], '') in ['J', 'Q', 'K'] \
                else point + 11
    for card in cards:
        if 'A' in card and point > 21:
            point = point - 10
    return point


def is_black_jack(cards: list[str]) -> bool:  # 判断是否是黑杰克
    return len(cards) == 2 and get_point_sum(cards) == 21
