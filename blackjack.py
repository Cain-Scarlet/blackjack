from hoshino import Service
from hoshino.typing import HoshinoBot, CQEvent
from hoshino.util import silence
from nonebot import MessageSegment

from .game import Game
from .datasave import *
from .poker import *

sv = Service('blackjack')
game = Game()
poker = Poker()


@sv.on_fullmatch('21点')
async def black_jack(bot: HoshinoBot, ev: CQEvent):
    if game.status:
        await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 当前游戏还没有结束')
    else:
        game.status = True
        await bot.send(ev, f"{MessageSegment.at(ev.user_id)} 游戏创建成功，请发送‘加入游戏’")


@sv.on_fullmatch('加入游戏')
async def join_game(bot: HoshinoBot, ev: CQEvent):
    if not player_exist(ev.user_id):
        player_init(ev.user_id)
    if not game.in_game and game.status:
        if len(game.players) > 6:
            await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 游戏人数已达上限')
        elif ev.user_id in game.players:
            await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 你已经加入游戏了')
        elif len(game.players) <= 6:
            if get_coin(ev.user_id) > 0:
                game.add_player(ev.user_id)
                await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 加入游戏成功，'
                                   f'当前游戏人数为{len(game.players)}')
            else:
                await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 加入游戏失败，你的筹码不足')


@sv.on_fullmatch(('all in', '梭哈'))
async def last_stand(bot: HoshinoBot, ev: CQEvent):
    if not game.in_game and game.status:
        if ev.user_id not in game.players:
            await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 你没有加入游戏')
        elif ev.user_id in game.bets:
            await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 你已经下注了')
        else:
            game.bet(ev.user_id, get_coin(ev.user_id))
            await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 背水一战！！！')


@sv.on_prefix('下注')
async def bet(bot: HoshinoBot, ev: CQEvent):
    if not game.in_game and game.status:
        player_bet = int(ev.message.extract_plain_text().strip())
        if ev.user_id not in game.players:
            await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 你没有加入游戏')
        elif ev.user_id in game.bets:
            await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 你已经下注了')
        elif ev.user_id not in game.bets:
            try:
                if player_bet > 0:
                    if get_coin(ev.user_id) >= player_bet:
                        game.bet(ev.user_id, player_bet)
                        await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 下注成功')
                    else:
                        await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 下注失败，你的筹码不足')
                else:
                    game.remove_player(ev.user_id)
                    # await silence(ev, 240)
                    # await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 投机取巧，给你一份禁言套餐')
                    await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 投机取巧，爬')
            except:
                return
                # await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 你用什么东西下的注')


@sv.on_fullmatch('开始游戏')
async def game_start(bot: HoshinoBot, ev: CQEvent):
    if game.status and not game.in_game:
        if ev.user_id not in game.players:
            await silence(ev, 120)
        elif len(game.players) != len(game.bets):
            statement = f''
            for qq in game.players:
                if qq not in game.bets:
                    statement = statement + f'{MessageSegment.at(qq)} '
            statement = statement + '还没有下注'
            await bot.send(ev, statement)
        elif len(game.players) == len(game.bets):
            game.dealer = poker.deal(2)
            statement = f"庄家的手牌是{[game.dealer[0], '?']}\n"
            for qq in game.players:
                game.cards[qq] = poker.deal(2)
                statement = statement + f'{MessageSegment.at(qq)} 的手牌是{game.cards[qq]}\n'
            await bot.send(ev, statement)
            game.player_next()
            await doing(bot, ev)
            game.in_game = True
    elif game.in_game:
        await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 游戏已经开始了')


async def doing(bot: HoshinoBot, ev: CQEvent):
    if len(game.in_game_player) > 0:
        if len(game.cards[game.current_player]) == 2:
            await bot.send(ev, f'{MessageSegment.at(game.current_player)} '
                               f'轮到你了：\n'
                               f'【看自己，看庄家，加注，拿牌，停牌，投降】')
        else:
            await bot.send(ev, f'{MessageSegment.at(game.current_player)} '
                               f'轮到你了：\n'
                               f'【看自己，看庄家，拿牌，停牌，投降】')
    else:
        game.current_player = 0
        await settle(bot, ev)


@sv.on_fullmatch('看自己')
async def watch_self(bot: HoshinoBot, ev: CQEvent):
    if game.in_game and game.current_player == ev.user_id:
        await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 你当前的手牌是\n{game.cards[ev.user_id]}')


@sv.on_fullmatch('看庄家')
async def watch_dealer(bot: HoshinoBot, ev: CQEvent):
    if game.in_game:
        await bot.send(ev, f"庄家的手牌是\n{[game.dealer[0], '?']}")


@sv.on_fullmatch('加注')
async def double(bot: HoshinoBot, ev: CQEvent):
    if game.in_game and game.current_player == ev.user_id:
        if get_coin(ev.user_id) >= game.bets[ev.user_id] * 2:
            game.double(ev.user_id)
            game.cards[ev.user_id].append(poker.deal(1)[0])
            if get_point_sum(game.cards[ev.user_id]) > 21:
                game.player_next()
                game.bust(ev.user_id)
                await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 加注成功，你拿了一张牌\n'
                                   f'你当前的手牌是{game.cards[ev.user_id]}'
                                   f'点数超过21点，你爆掉了')
            else:
                await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 加注成功，你拿了一张牌\n'
                                   f'你当前的手牌是{game.cards[ev.user_id]}')
                game.player_next()
            await doing(bot, ev)
        else:
            await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 加注失败，你的筹码不足')


@sv.on_fullmatch('拿牌')
async def hit(bot: HoshinoBot, ev: CQEvent):
    if game.in_game and game.current_player == ev.user_id:
        game.cards[ev.user_id].append(poker.deal(1)[0])
        if get_point_sum(game.cards[ev.user_id]) > 21:
            game.player_next()
            game.bust(ev.user_id)
            await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 你拿了一张牌\n'
                               f'你当前的手牌是{game.cards[ev.user_id]}'
                               f'点数超过21点，你爆掉了')
        else:
            await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 你拿了一张牌\n'
                               f'你当前的手牌是{game.cards[ev.user_id]}')
            game.player_next()
        await doing(bot, ev)


@sv.on_fullmatch('停牌')
async def stand(bot: HoshinoBot, ev: CQEvent):
    if game.in_game and game.current_player == ev.user_id:
        game.stand(ev.user_id)
        await bot.send(ev, f"{MessageSegment.at(ev.user_id)} Σ(☉▽☉\"a")
        game.player_next()
        await doing(bot, ev)


@sv.on_fullmatch('投降')
async def surrender(bot: HoshinoBot, ev: CQEvent):
    if game.in_game and game.current_player == ev.user_id:
        game.surrender(ev.user_id)
        await bot.send(ev, f"{MessageSegment.at(ev.user_id)} ヾ(๑╹◡╹)ﾉ\"")
        game.player_next()
        await doing(bot, ev)


async def settle(bot: HoshinoBot, ev: CQEvent):
    statement = f'庄家的手牌是{game.dealer}\n'
    while get_point_sum(game.dealer) < 17:
        game.dealer.append(poker.deal(1)[0])
        if get_point_sum(game.dealer) > 21:
            statement = statement + f'庄家拿了一张牌\n当前的手牌是{game.dealer}，点数超过21点，爆掉了'
        else:
            statement = statement + f'庄家拿了一张牌\n当前的手牌是{game.dealer}\n'

    await bot.send(ev, statement)
    await bot.send(ev, '现在开始结算========')
    statement = f''

    dealer_point_sum = get_point_sum(game.dealer)
    if dealer_point_sum > 21:
        for qq in game.bets:
            if game.bets[qq] > 0:
                if is_black_jack(game.cards[qq]):
                    game.black_jack_win(qq)
                    statement = statement + f'{MessageSegment.at(qq)} 是黑杰克，获得2*{game.bets[qq] / 2}点筹码\n'
                else:
                    statement = statement + f'{MessageSegment.at(qq)} 获得{game.bets[qq]}点筹码\n'
            else:
                statement = statement + f'{MessageSegment.at(qq)} 失去{-game.bets[qq]}点筹码\n'
    else:
        if is_black_jack(game.dealer):
            statement = statement + '庄家是黑杰克\n'
        for qq in game.bets:
            if game.bets[qq] > 0:
                if is_black_jack(game.dealer):
                    if not is_black_jack(game.cards[qq]):
                        game.lose(qq)
                        statement = statement + f'{MessageSegment.at(qq)} 失去{-game.bets[qq]}点筹码\n'
                    else:
                        game.push(qq)
                        statement = statement + f'{MessageSegment.at(qq)} 也是黑杰克，平局\n'
                else:
                    if is_black_jack(game.cards[qq]):
                        game.black_jack_win(qq)
                        statement = statement + f'{MessageSegment.at(qq)} 是黑杰克，获得{game.bets[qq]}点筹码\n'
                    elif dealer_point_sum > get_point_sum(game.cards[qq]):
                        game.lose(qq)
                        statement = statement + f'{MessageSegment.at(qq)} 失去{-game.bets[qq]}点筹码\n'
                    elif dealer_point_sum < get_point_sum(game.cards[qq]):
                        statement = statement + f'{MessageSegment.at(qq)} 获得{game.bets[qq]}点筹码\n'
                    else:
                        game.push(qq)
                        statement = statement + f'{MessageSegment.at(qq)} 双方一样大，不输不赢\n'
            else:
                statement = statement + f'{MessageSegment.at(qq)} 失去{-game.bets[qq]}点筹码\n'
    batch_save(game.bets)
    await bot.send(ev, statement)
    await bot.send(ev, '结算完毕')

    game.__init__()
    poker.__init__()


@sv.on_fullmatch('21点帮助')
async def game_help(bot: HoshinoBot, ev: CQEvent):
    bot.send(ev, f'流程：\n'
                 f'  21点->加入游戏->下注->操作->结算\n'
                 f'杂项：\n'
                 f'  搬砖，查看筹码')


@sv.on_fullmatch('搬砖')
async def moving_bricks(bot: HoshinoBot, ev: CQEvent):
    if not game.status:
        await silence(ev, 60 * 60)
        add_coin(ev.user_id, 128)
        await bot.send(ev, f'为了筹码，{MessageSegment.at(ev.user_id)} 顶着炎炎烈日出去搬砖了，一个小时候他会回来的，所以大家一起开心的玩吧！')


@sv.on_fullmatch('查看筹码')
async def watch_coin(bot: HoshinoBot, ev: CQEvent):
    if not player_exist(ev.user_id):
        player_init(ev.user_id)
    coin = get_coin(ev.user_id)
    await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 你还有{coin}点筹码')


@sv.on_fullmatch('退出游戏')
async def exit_game(bot: HoshinoBot, ev: CQEvent):
    if game.status and not game.in_game and ev.user_id in game.players:
        try:
            game.remove_player(ev.user_id)
        finally:
            await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 退出成功')


@sv.on_fullmatch('强制脱出')
async def force_exit(bot: HoshinoBot, ev: CQEvent):
    if game.status and game.in_game and ev.user_id in game.players:
        game.__init__()
        poker.__init__()
        silence(ev, 60 * 60)
        await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 如果在游戏中○○的话，群友生涯就结束了吧')


@sv.on_fullmatch('关闭游戏')
async def close_game(bot: HoshinoBot, ev: CQEvent):
    if len(game.players) == 0:
        game.__init__()
        poker.__init__()
        await bot.send(ev, f'{MessageSegment.at(ev.user_id)} 游戏已关闭')
