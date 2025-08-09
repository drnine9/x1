import random
from database import get_balance, update_balance, get_win_rate

def play_game(user_id, bet_amount, win_chance):
    balance = get_balance(user_id)
    if balance < bet_amount:
        return "❌ رصيدك غير كافي."
    
    if random.random() < win_chance:
        balance += bet_amount
        result = "🎉 فزت!"
    else:
        balance -= bet_amount
        result = "💔 خسرت!"
    
    update_balance(user_id, balance)
    return f"{result}\n💰 رصيدك الآن: {balance}"

def game_plane(user_id, bet_amount):
    return play_game(user_id, bet_amount, get_win_rate() * 0.8)

def game_blackjack(user_id, bet_amount):
    return play_game(user_id, bet_amount, get_win_rate() * 0.7)

def game_crystal(user_id, bet_amount):
    return play_game(user_id, bet_amount, get_win_rate() * 0.6)

def game_texas(user_id, bet_amount):
    return play_game(user_id, bet_amount, get_win_rate() * 0.5)

def game_roulette(user_id, bet_amount, choice):
    return play_game(user_id, bet_amount, get_win_rate() * 0.4)