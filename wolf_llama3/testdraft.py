def get_substring_after_colon(input_string):
    # 查找英文冒号和中文冒号的位置
    english_colon_index = input_string.find(':')
    chinese_colon_index = input_string.find('：')

    # 获取第一个出现的冒号位置
    if english_colon_index == -1 and chinese_colon_index == -1:
        return "No colon found in the string."
    elif english_colon_index == -1:
        colon_index = chinese_colon_index
    elif chinese_colon_index == -1:
        colon_index = english_colon_index
    else:
        colon_index = min(english_colon_index, chinese_colon_index)

    # 返回冒号后面的字符串
    return input_string[colon_index + 1:]

# 示例
input_string = "这是一个例子：后面的内容"
result = get_substring_after_colon(input_string)
print(result)  # 输出：后面的内容











# 示例
input_string = "这是一个例子：后面的内容"
result = get_substring_after_colon(input_string)
print(result)  # 输出：后面的内容