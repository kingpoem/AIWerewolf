import player
import streamlit as st

class Seer(player.Player):
    """
    先知玩家的类，继承自Player类
    """
    def __init__(self,id,game_state, message_history, big_prompt):
        super().__init__(id,game_state, message_history, big_prompt)
        self.big_prompt = big_prompt

    def seer_action(self, game_state, message_history) -> tuple[dict, list]:
        """
        先知行动阶段的逻辑
        
        输入：
            1. game_state: 当前的游戏状态
            2. message_history: 列表
        
        输出：
            1. game_state: 更新后的游戏状态
            2. message_history: 列表
        """
        content = f"玩家{self.id + 1}，你是预言家。你要查验哪位玩家的身份？请只返回1-6的数字，严禁输出任何其它内容。"
        message_history.append({"role": "user", "content": content})
        response = self.api_request(message_history)

        # 设置先决随机查询
        # print(f"预言家选择查验：{response}")     # None

        check_target = int(self.extract_first_number(response))-1  # 0-5
        message_history.append({"role": "assistant", "content": str(check_target+1)})
        role_revealed = game_state["player_roles"][check_target]
        game_state["seer_result"][check_target] = role_revealed
        print(f"预言家查验了玩家 {check_target+1} 的身份，他的身份是 {role_revealed}。")
    
        colors = ["grey","green","orange"]
        if self.game_state["player_roles"][check_target] == "狼人":
            st.markdown(f":orange[预言家]查验了:{colors[0]}[玩家 {check_target+1}]的身份，他的身份是:{colors[0]}[{role_revealed}]。")
        elif self.game_state["player_roles"][check_target] == "预言家" or self.game_state["player_roles"][check_target] == "女巫":
            st.markdown(f":orange[预言家]查验了:{colors[2]}[玩家 {check_target+1}]的身份，他的身份是:{colors[2]}[{role_revealed}]。")
        else:
            st.markdown(f":orange[预言家]查验了:{colors[1]}[玩家 {check_target+1}]的身份，他的身份是:{colors[1]}[{role_revealed}]。")
            


        return game_state, message_history