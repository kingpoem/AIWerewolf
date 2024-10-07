"""
该文档共有4个函数分别
初始化游戏状态(initialize_game())           到底给狼人对象传什么进去？
检查游戏是否结束(check_game_end())          完成
确定游戏的胜利者(determine_winner())        完成
夜晚行动(night_actions())。
"""

import random
import player
import werewolf
import seer
import witch
import json

def initialize_game()->tuple[dict, list[list], list]:
    """
    初始化游戏 
    
    输出：
        game_state：字典，游戏状态
        message_histories：列表的列表，消息历史列表
        players：列表，玩家对象列表
    """
    # 游戏状态
    roles = ['预言家', '女巫', '平民', '平民', '狼人', '狼人']
    random.shuffle(roles)
    game_state = {
        "round": 1,
        "players_alive": [True] * 6,
        "player_roles": roles,
        "votes": [0] * 6,
        "witch_has_potion": {"heal": True, "poison": True},
        "seer_result": [None] * 6,
        "last_night_kill": None,
        "discussions": [],
        "deaths": [],
        "save_target": None
    }

    # 每个玩家有独立的消息历史
    message_histories = [[] for message_history in range(6)]  # 6个玩家的消息历史列表，是一个列表的列表


    with open("prompt.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        witch_prompt = data["女巫"]
        seer_prompt = data["预言家"]
        player_prompt = data["平民"]
        werewolf_prompt = data["狼人"]

    # 玩家对象列表
    players = []    
    for i, role in enumerate(roles):
        if role == '狼人':
            players.append(werewolf.Werewolf(i, game_state, message_histories[i], werewolf_prompt))
        elif role == '预言家':
            players.append(seer.Seer(i, game_state, message_histories[i], seer_prompt))
        elif role == '女巫':
            players.append(witch.Witch(i, game_state, message_histories[i], witch_prompt))
        else:
            players.append(player.Player(i, game_state, message_histories[i], player_prompt))

    return game_state, message_histories, players

def check_game_end(game_state)->bool:
    """
    检查游戏是否结束，狼人全灭或者非狼人全灭
    """
    #  存活的狼人数量
    alive_werewolves = sum([1 for i, role in enumerate(game_state["player_roles"]) if role == '狼人' and game_state["players_alive"][i]])   
    #  存活的普通人数量
    alive_villagers = sum([1 for i, role in enumerate(game_state["player_roles"]) if role != '狼人' and game_state["players_alive"][i]])    
    
    if alive_werewolves == 0:
        return True  # 大好人胜利
    elif alive_werewolves >= alive_villagers:
        return True  # 狼人胜利
    
    return False

def determine_winner(game_state)->str:
    """
    确定游戏的胜利者
    """
    alive_werewolves = sum([1 for i, role in enumerate(game_state["player_roles"]) if role == '狼人' and game_state["players_alive"][i]])
    if alive_werewolves == 0:
        return "好人阵营"
    else:
        return "狼人阵营"

def night_actions(game_state, message_histories)->tuple[dict,list[list]]:
    """
    夜晚行动
    狼人行动    决定杀人目标，确定kill_target
    女巫行动    查找游戏中活着的女巫角色，并调用对应玩家模块中的 witch_action 方法来执行女巫的行动，更新游戏状态。
    预言家行动
    
    输入：
        game_state：字典，游戏状态
        message_histories：列表的列表，消息历史列表
        
    
    输出：
        game_state：字典，游戏状态
        message_histories：列表的列表，消息历史列表
    """
    # 狼人投票决定杀人目标
    werewolves = [i for i, role in enumerate(game_state["player_roles"]) if role == '狼人' and game_state["players_alive"][i]]  # 活着的狼人玩家的索引
    kill_target = None

    if werewolves:
        # 调用任意一位狼人玩家的模块执行狼人投票
        player_module = globals()[f'player{werewolves[0] + 1}']
        kill_target, message_histories = player_module.werewolf_vote(game_state, werewolves, message_histories)
        game_state, message_histories = player_module.update_deaths(game_state, kill_target, message_histories)

    # 女巫行动
    witch_index = next((i for i, role in enumerate(game_state["player_roles"]) if role == '女巫' and game_state["players_alive"][i]), None)
    if witch_index is not None:
        player_module = globals()[f'player{witch_index + 1}']
        game_state = player_module.witch_action(game_state, kill_target, message_histories[witch_index])

    # 预言家行动
    seer_index = next((i for i, role in enumerate(game_state["player_roles"]) if role == '预言家' and game_state["players_alive"][i]), None)
    if seer_index is not None:
        player_module = globals()[f'player{seer_index + 1}']
        game_state = player_module.seer_action(game_state, message_histories[seer_index])

    return game_state, message_histories