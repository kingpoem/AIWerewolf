"""
狼人类，继承自Player类
"""

import player
import streamlit as st

class Werewolf(player.Player):
    """
    狼人玩家的类，继承自Player类

    输入：
        werewolves: 列表，狼人玩家的编号列表
    """
    def __init__(self,id,game_state, message_histories, big_prompt):
        super().__init__(id,game_state, message_histories, big_prompt)
        self.werewolves = []
        self.big_prompt = big_prompt
    # 此函数的传参有重大问题，需要修改
    def werewolf_vote(self, game_state, message_histories,players)->tuple[int, list[list]]:
        """
        狼人投票阶段的逻辑，只有达成共识才会返回kill_target，否则一直循环下去

        输入：
            game_state: 字典，游戏状态
            message_histories: 列表的列表，消息历史
            players: 列表，玩家列表

        输出：
            kill_target: 整数，被杀死的玩家编号
            message_histories: 列表的列表，消息历史
        """
        kill_target = None
        while not kill_target:
            votes = []  # 列表，用于存储所有狼人玩家的投票结果
            # werewolf 为狼人编号
            # werewolves 为狼人编号列表 0到5
            self.werewolves = []  # 重置狼人列表
            self.werewolves.extend([i for i, player in enumerate(players) if isinstance(player, Werewolf)])
            for werewolf in self.werewolves:
                # content 为1到6
                content = f"玩家{werewolf+1}，你的身份是狼人。你们已知的同伴是 {[f'玩家{i+1}' for i in self.werewolves]}。现在是夜晚，你需要与其他狼人一起决定消灭哪位玩家。请投票决定消灭哪位玩家。请只返回1-6的数字，不能返回自己和同伴的编号，也不能返回已经消灭的玩家的编号，严禁输出任何其它内容。"
                message_histories[werewolf].append({"role": "user", "content": content})
                response = self.api_request(message_histories[werewolf])  # response 为字符串型1到6
                #print(response)
                #print(message_histories[werewolf])
                if response is None:
                    content = "我没有输出有效的数字，将重新开始投票。"
                    message_histories[werewolf].append({"role": "assistant", "content": content})
                    return self.werewolf_vote(game_state, message_histories, players)
                # vote 为0到5，临时变量，用于存储狼人投票结果
                vote = self.extract_first_number(response) - 1  # 如果response为None，则vote为-1
                message_histories[werewolf].append({"role": "assistant", "content": str(vote + 1)})
                votes.append(vote)
            kill_target = votes[0]
        
        print(f"狼人决定杀死玩家 {kill_target + 1}。")
        colors = ["grey","green","orange"]
        if self.game_state["player_roles"][kill_target] == "狼人":
            st.markdown(f":grey[狼人]决定杀死:{colors[0]}[玩家{kill_target+1}]")
        elif self.game_state["player_roles"][kill_target] == "预言家" or self.game_state["player_roles"][kill_target] == "女巫":
            st.markdown(f":grey[狼人]决定杀死:{colors[2]}[玩家{kill_target+1}]")
        else:
            st.markdown(f":grey[狼人]决定杀死:{colors[1]}[玩家{kill_target+1}]")
    
        return kill_target, message_histories
    