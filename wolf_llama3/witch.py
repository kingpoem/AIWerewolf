import player
import re
import streamlit as st

class Witch(player.Player):
    """
    女巫玩家的类，继承自Player类
    """
    def __init__(self,id,game_state, message_history, big_prompt):
        super().__init__(id,game_state, message_history, big_prompt)
        self.big_prompt = big_prompt

    def witch_action(self, game_state, kill_target, message_history)->tuple[dict, list]:
        """
        女巫行动阶段的逻辑
        
        输入：
            game_state: 当前的游戏状态
            kill_target: 狼人要杀死的玩家的id
            message_history: 列表
        
        输出：
            game_state: 更新后的游戏状态
            message_history: 列表
        """
        # 女巫使用解药
        if game_state["player_roles"][self.id] == '女巫' and game_state["witch_has_potion"]["heal"] and kill_target != self.id:
            content = f"玩家{self.id + 1}，你是女巫。玩家 {kill_target + 1} 被狼人攻击。你要使用解药救他吗？（yes or no）"
            # print(f"对女巫的请求：{content}")
            message_history.append({"role": "user", "content": content})
            decision = self.api_request(message_history)

            if decision == None:
                decision = "no"
            regex = re.compile(r'yes')
            match = regex.search(decision)
            message_history.append({"role": "assistant", "content": decision})
            if match == None:  # 检查匹配对象是否为 None
                game_state["players_alive"][kill_target] = False
                print(f"女巫决定不使用解药。")
                st.markdown(f":orange[女巫]决定不使用解药。")
            elif match.group() == "yes":
                game_state["witch_has_potion"]["heal"] = False
                game_state["players_alive"][kill_target] = True
                game_state["last_night_kill"] = None
                game_state["witch_has_potion"]["poison"] = False
                game_state["save_target"] = kill_target
                print(f"女巫救了玩家 {kill_target + 1}。")
                colors = ["grey","green","orange"]
                if self.game_state["player_roles"][kill_target] == "狼人":
                    st.markdown(f":orange[女巫]救了:{colors[0]}[玩家{kill_target+1}]")
                elif self.game_state["player_roles"][kill_target] == "预言家" or self.game_state["player_roles"][kill_target] == "女巫":
                    st.markdown(f":orange[女巫]救了:{colors[2]}[玩家{kill_target+1}]")
                else:
                    st.markdown(f":orange[女巫]救了:{colors[1]}[玩家{kill_target+1}]")

        else:
            content = f"玩家{self.id + 1}，你是女巫。玩家 {kill_target + 1} 被狼人攻击。很抱歉，你不能用解药救自己，但是你可以临死之前毒死一个人。"
            message_history.append({"role": "user", "content": content})
            decision = self.api_request(message_history)
            message_history.append({"role": "assistant", "content": decision})
            game_state["players_alive"][self.id] = False
        
        # 女巫使用毒药
        if game_state["player_roles"][self.id] == '女巫' and game_state["witch_has_potion"]["poison"]:
            content = f"玩家{self.id + 1}，你是女巫。你要使用毒药毒死其他玩家吗？（yes/no）"
            message_history.append({"role": "user", "content": content})
            decision = self.api_request(message_history)
            

            if decision == None:
                decision = "no"
            regex = re.compile(r'yes')
            match = regex.search(decision)
            message_history.append({"role": "assistant", "content": decision})
            if match == None:  # 检查匹配对象是否为 None
                print(f"女巫没有毒死任何玩家。")
                st.markdown(f":orange[女巫]没有毒死任何玩家。")
            elif match.group() == "yes":  # 检查匹配对象是否为 None
                content = f"既然你已经决定要毒死其他玩家，那么你要毒死哪位玩家？请只返回1-6的数字，严禁输出任何其它内容。"
                message_history.append({"role": "user", "content": content})
                response = self.api_request(message_history)
                if self.extract_first_number(response) == None:
                    print(f"女巫没有毒死任何玩家。")
                    st.markdown(f":orange[女巫]没有毒死任何玩家。")
                else:
                    poison_target = self.extract_first_number(response) - 1
                    message_history.append({"role": "assistant", "content": str(poison_target + 1)})
                    game_state["players_alive"][poison_target] = False
                    game_state["witch_has_potion"]["poison"] = False
                    print(f"女巫毒死了玩家 {poison_target + 1}。")
                    colors = ["grey","green","orange"]
                    if self.game_state["player_roles"][kill_target] == "狼人":
                        st.markdown(f":orange[女巫]毒死了:{colors[0]}[玩家{kill_target+1}]")
                    elif self.game_state["player_roles"][kill_target] == "预言家" or self.game_state["player_roles"][kill_target] == "女巫":
                        st.markdown(f":orange[女巫]毒死了:{colors[2]}[玩家{kill_target+1}]")
                    else:
                        st.markdown(f":orange[女巫]毒死了:{colors[1]}[玩家{kill_target+1}]")
        return game_state, message_history
