"""
玩家类，即普通村民
构造函数包含9个函数

函数功能：
1. get_access_token()：获取百度API的access_token                                 已完成
2. api_request(messages)：调用百度API接口返回回复内容                             等出问题再看,messages是嵌套列表
3. extract_first_number(text)：从文本中提取第一个数字                             已完成
4. discussion(game_state, message_history)：玩家讨论阶段的发言                    已修改id
5. vote(game_state, message_history)：玩家投票阶段的选择                          已修改id    另外逻辑可能会有问题
6. update_deaths(game_state, kill_target, message_histories)：更新玩家的死亡状态  已完成
7. handle_voting_deaths(game_state, message_histories)：处理白天投票后的玩家死亡   已完成
8. get_last_words(game_state, message_history)：处理玩家的遗言                    已修改id
"""

import requests
import json
import ollama
import streamlit as st
# response = ollama.chat(
#     model='llama3.1',
#     messages=

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    API_KEY = data['API_KEY']
    SECRET_KEY = data['SECRET_KEY']


def get_substring_after_colon(input_string):
    # 查找英文冒号和中文冒号的位置
    english_colon_index = input_string.find(':')
    chinese_colon_index = input_string.find('：')

    # 获取第一个出现的冒号位置
    if english_colon_index == -1 and chinese_colon_index == -1:
        return input_string
    elif english_colon_index == -1:
        colon_index = chinese_colon_index
    elif chinese_colon_index == -1:
        colon_index = english_colon_index
    else:
        colon_index = min(english_colon_index, chinese_colon_index)

    # 返回冒号后面的字符串
    return input_string[colon_index + 1:]

class Player:
    def __init__(self,id,game_state,message_history,big_prompt):
        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY
        self.id = id    # 唯一标识符
        self.game_state = game_state
        self.message_history = message_history
        self.big_prompt = big_prompt
        self.message_history.append({"role": "user", "content": self.big_prompt})
        self.message_history.append({"role": "assistant", "content": "明白了，我会记住的。"})

    def get_access_token(self) -> str:
        """
        获取百度API的access_token

        返回：字符串，access_token
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": self.API_KEY, "client_secret": self.SECRET_KEY}
        return str(requests.post(url, params=params).json().get("access_token"))

    def api_request(self, message_history) -> str:
        
        
        try:
            response = ollama.chat(model='llama3',messages=message_history)
            response_json = response
            #if "message" in response_json:
            # print(response_json)
            return response_json["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            return None

    def extract_first_number(self, text) -> None | int:
        """
        从文本中提取第一个数字，没有数字，返回0，意即弃权
        
        输入：
            text: 字符串，待提取的文本，传进去的多是字符串型数字

        返回：
            整数，第一个数字
        """
        if text is None:
            return None  # 如果text是None，返回0，意即弃权
        
        for char in text:
            if char.isdigit():
                return int(char)



    def discussion(self, game_state, message_history)->tuple[dict, list]:
        """
        玩家讨论阶段的发言
        
        输入：
            game_state: 字典，游戏状态
            message_history: 列表，玩家发言历史，但怎么传了个字典？？？

        返回：
            game_state: 字典，游戏状态
            message_history: 列表，玩家发言历史
        """
        
        # 玩家讨论逻辑
        content = f"玩家{self.id+1}，你的身份是 {game_state['player_roles'][int(self.id)]}。现在是狼人杀的白天阶段，以下是当前玩家的发言内容: {[f'玩家{i+1}发言：' + discussion for i, discussion in enumerate(game_state['discussions'])]}. 请根据当前的游戏状态和之前玩家的发言内容做出发言，如果你是狼人，请说自己是预言家或是村民，并预言出某个玩家为狼人；如果你是预言家，请说出自己预言的情况，并引导其他村民相信你，但不要有事实性错误，比如预言家一次只能查验一个玩家身份；如果你是村民，请根据其他玩家的发言，判断谁是狼人，并投票给他，让它出局。可以使用一些狼人杀游戏中的术语，比如“刀”，夜里被狼人杀死。踩：发言时指出某玩家的发言和状态不好的地方，而怀疑某玩家可能是狼人。尽量用简短的语句来表达，多用攻击性语言，如果你是村民，请多用感叹句和疑问句。"
        message_history.append({"role": "user", "content": content})
        response = self.api_request(message_history)
        message_history.append({"role": "assistant", "content": response})
        game_state["discussions"].append(f"玩家{self.id+1}发言：{response}")
        print(f"玩家{self.id+1}发言: {response}")

        response = get_substring_after_colon(response)
        colors = ["grey","green","orange"]
        if self.game_state["player_roles"][self.id] == "狼人":
            st.markdown(f":{colors[0]}[玩家{self.id+1}发言:] {response}")
        elif self.game_state["player_roles"][self.id] == "预言家" or self.game_state["player_roles"][self.id] == "女巫":
            st.markdown(f":{colors[2]}[玩家{self.id+1}发言:] {response}")
        else:
            st.markdown(f":{colors[1]}[玩家{self.id+1}发言:] {response}")    
        return game_state, message_history

    def vote(self, game_state, message_history) -> tuple[int, list]:
        """
        玩家投票阶段的选择

        输入：
            game_state: 字典，游戏状态
            message_history: 列表，玩家发言历史

        返回：
            vote: 整数，玩家投票的玩家编号，1到6
            message_history: 列表，玩家发言历史
        """

        # 玩家投票逻辑
        content = f"玩家{self.id+1}，你的身份是 {game_state['player_roles'][int(self.id)]}。现在是投票阶段，如果你是狼人，请先投预言家，然后投女巫或村民；如果你是预言家，村民或女巫，请投给狼人。请只返回1-6的数字，且不能投已经出局的人的票，不能给自己投票。"
        message_history.append({"role": "user", "content": content})
        vote = self.api_request(message_history)    # 1-6的数字
        if vote is None:
            content = "抱歉，我会再认真考虑局势，从1到6的数字中选出一个最可能是敌人的投票，如果敌人已经出局了，我将不会给它投票，也不会投已经出局的同伴的票，并且只回答数字。"
            print(f"玩家{self.id + 1}投票无效。")
            message_history.append({"role": "assistant", "content": content})
            return self.vote(game_state, message_history)  # 重新投票
        else:
            try:
                vote = self.extract_first_number(vote)    # 1-6的数字
                if vote == self.id+1 or not game_state["players_alive"][vote - 1]:
                    # 不能给自己投票或投票给已经出局的玩家
                    print(f"玩家{self.id + 1}尝试投票给无效的玩家 {vote}，投票无效。")
                    content = "抱歉，我会再认真考虑局势，从1到6的数字中选出一个最可能是敌人的投票，如果敌人已经出局了，我将不会给它投票，也不会投已经出局的同伴的票，不能给自己投票，并且只回答数字。"
                    message_history.append({"role": "assistant", "content": content})
                    return self.vote(game_state, message_history)  # 重新投票
                else:
                    message_history.append({"role": "assistant", "content": str(vote)})
                    print(f"玩家{self.id + 1}投票给玩家 {vote}。")
                    st.write(f"玩家{self.id + 1}投票给玩家 {vote}。")
                    return vote, message_history
            except ValueError:
                print(f"玩家{self.id + 1}投票无效。vote={vote}")
                content = "抱歉，我会再认真考虑局势，从1到6的数字中选出一个最可能是敌人的投票，如果敌人已经出局了，我将不会给它投票，也不会投已经出局的同伴的票，并且只回答数字。"
                message_history.append({"role": "assistant", "content": content})
                return self.vote(game_state, message_history)  # 重新投票



    def update_deaths(self,game_state, kill_target, message_histories)->tuple[dict, list[list]]:
        """
        更新玩家的死亡状态

        输入：
            game_state: 字典，游戏状态
            kill_target: 整数，玩家被杀死的玩家编号
            message_histories: 列表，玩家发言历史

        输出：
            game_state: 字典，游戏状态
            message_histories: 列表的列表，玩家发言历史
        """
        if game_state["players_alive"][kill_target] and game_state["witch_has_potion"]["heal"] == False and kill_target != game_state["save_target"]:
            game_state["players_alive"][kill_target] = False
            game_state["deaths"].append(f"玩家{kill_target + 1}在夜晚被杀死。")
        # 如果玩家有遗言，记录在讨论中
        if game_state["witch_has_potion"]["heal"] == False and kill_target != game_state["save_target"]:
            message_histories[kill_target].append({"role": "user", "content": "你已经被杀死，请说出你的遗言。如果你是狼人，请到死都不要说自己是狼人，说自己是一个无害的村民。如果你是预言家，请至死都要把正确情报传递给其他人，如果有队友攻击你，请对你的队友进行攻击。如果你是女巫，请说出自己毒杀了谁，救了谁。"})
            last_words = f"玩家{kill_target + 1}的遗言：{self.api_request(message_histories[kill_target])}" 
            game_state["discussions"].insert(0, last_words)
            print(last_words)
        # print(game_state["players_alive"])
        
        return game_state, message_histories
    
    def handle_voting_deaths(self,game_state, message_histories)->tuple[dict, list]:
        """
        处理白天投票后的玩家死亡

        输入：
            game_state: 字典，游戏状态
            message_histories: 列表，玩家发言历史

        输出：
            game_state: 字典，游戏状态
            message_histories: 列表，玩家发言历史
        """
        votes = [0] * 6
        for i in range(6):
            if game_state["players_alive"][i]:
                vote, message_histories[i] = vote(game_state, message_histories[i])
                votes[vote-1] += 1
        
        majority = max(votes)
        voted_out = votes.index(majority)   # 0-5的数字
        game_state["players_alive"][voted_out] = False
        game_state["deaths"].append(f"玩家{voted_out + 1}被投票出局。")
        
        # 处理遗言
        last_words = f"玩家{voted_out + 1}的遗言：{self.api_request(message_histories[voted_out])}"
        game_state["discussions"].append(last_words)
        print(last_words)
    
        return game_state, message_histories
    
    def get_last_words(self,game_state, message_history)->str:
        """
        处理玩家的遗言

        输入：
            game_state: 字典，游戏状态
            message_history: 列表，玩家发言历史

        输出：
            response: 字符串，玩家的遗言
        """
        self.id = self.id  # 获取玩家编号
        
        # 生成遗言内容
        content = str(f"玩家{self.id}，你的身份是 {game_state['player_roles'][int(self.id) - 1]}。你已经被投票出局，请说出你的遗言。如果你是狼人，请到死都不要说自己是狼人，说自己是一个无害的村民。")
        message_history.append({"role": "user", "content": content})
        # 调用API生成遗言
        response = self.api_request(message_history)
        message_history.append({"role": "assistant", "content": response})
        
        return response
