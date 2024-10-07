import game
import streamlit as st


def main():
    game_state, message_histories,players = game.initialize_game()
    st.title("2024-狼人杀AI挑战赛")
    st.markdown(f"本次比赛使用本地大模型：Llama3")
    while not game.check_game_end(game_state):
        print(f"第{game_state['round']}回合开始。")
        st.write(f"第{game_state['round']}回合开始。")
        print(f"{game_state['player_roles']}")
        st.write(f"{game_state['player_roles']}")
        # 夜晚行动
        kill_target = None
        for i, alive in enumerate(game_state["players_alive"]):
            if alive:
                role = game_state["player_roles"][i]
                player_module = players[i]
                if role == '狼人':
                    kill_target, message_histories = player_module.werewolf_vote(game_state, message_histories, players)
                    break  # 找到第一个狼人后退出循环

        for i, alive in enumerate(game_state["players_alive"]):
            if alive:
                role = game_state["player_roles"][i]
                player_module = players[i]
                if role == '女巫':
                    game_state, message_histories[i] = player_module.witch_action(game_state, kill_target, message_histories[i])
                    game_state, message_histories = player_module.update_deaths(game_state, kill_target, message_histories)
                elif role == '预言家':
                    game_state, message_histories[i] = player_module.seer_action(game_state, message_histories[i])

        # 检查夜晚行动后的状态
        if game.check_game_end(game_state):
            break

        # 白天发言与投票
        game_state["discussions"] = []  # 每天清空讨论记录
        for i, alive in enumerate(game_state["players_alive"]): # i从0开始
            if alive:
                player_module = players[i]  # player_module 是一个对象
                game_state, message_histories[i] = player_module.discussion(game_state, message_histories[i])
        
        # 投票处理
        votes = [0] * len(game_state["players_alive"])
        for i, alive in enumerate(game_state["players_alive"]):
            if alive:
                player_module = players[i]
                # vote表示被投票的玩家编号0到5，message_histories[i]表示玩家的消息历史
                # votes[vote]表示被投票玩家的票数
                vote, message_histories[i] = player_module.vote(game_state, message_histories[i])
                votes[vote-1] += 1
        
        # 确定被投票出局的玩家
        max_votes = max(votes)  # 最大票数
        voted_out = votes.index(max_votes)  # 票数最多的玩家编号    0-5
        game_state["players_alive"][voted_out] = False  # 被投票出局
        game_state["deaths"].append(f"玩家{voted_out + 1}被投票出局。")
        
        # 处理遗言
        player_module = players[int(f'{voted_out}')]
        last_words = f"玩家{voted_out+1}的遗言：" + f"{player_module.get_last_words(game_state, message_histories[voted_out])}"
        game_state["discussions"].append(last_words)
        print(last_words)
        st.write(last_words)
        
        # 检查白天投票后的状态
        if game.check_game_end(game_state):
            break
        
        game_state["round"] += 1
    
    print("游戏结束。胜利者是:", game.determine_winner(game_state))
    st.markdown(f":red[游戏结束。胜利者是:{game.determine_winner(game_state)}]")
    st.markdown(f"''':red[游戏结束。胜利者是:{game.determine_winner(game_state)}]'''")
    st.html(f"<h2 style='color:red;'>游戏结束。胜利者是:{game.determine_winner(game_state)}</h1>")
    


if __name__ == "__main__":
    main()
