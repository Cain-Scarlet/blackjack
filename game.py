import math


class Game:
    def __init__(self):
        self.dealer: list = []  # 庄家的手牌
        self.players = []  # 参与的玩家
        self.in_game_player = []
        self.bets = {}  # 筹码
        self.cards = {}
        self.status = False
        self.in_game = False
        self.current_player = 0
        self.current_player_index = 0

    def add_player(self, qq):  # 添加玩家
        self.players.append(qq)
        self.in_game_player.append(qq)

    def remove_player(self, qq):  # 移除玩家
        self.players.remove(qq)
        self.in_game_player.remove(qq)
        try:
            del self.bets[qq]
        except:
            return

    def bet(self, qq, bet):  # 下注
        self.bets[qq] = bet

    def double(self, qq):  # 加注
        self.bets[qq] = self.bets[qq] * 2
        self.in_game_player.remove(qq)

    def stand(self, qq):  # 停牌
        self.in_game_player.remove(qq)

    def surrender(self, qq):  # 投降
        self.bets[qq] = -math.ceil(self.bets[qq] / 2)
        self.in_game_player.remove(qq)

    def bust(self, qq):
        self.bets[qq] = -self.bets[qq]
        self.in_game_player.remove(qq)

    def lose(self, qq):
        self.bets[qq] = -self.bets[qq]

    def push(self, qq):
        self.bets[qq] = 0

    def black_jack_win(self, qq):
        self.bets[qq] = self.bets[qq] * 2

    def player_next(self):
        if self.current_player == 0 and self.current_player_index == 0:
            self.current_player = self.in_game_player[0]
        else:
            try:
                if self.players[self.current_player_index - 1] == self.current_player:
                    self.current_player = self.players[self.current_player_index + 1]
                else:
                    self.current_player = self.players[self.current_player_index]
            except:
                self.current_player_index = 0
                self.current_player = self.in_game_player[0]
