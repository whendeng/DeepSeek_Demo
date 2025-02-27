import tkinter as tk
from tkinter import scrolledtext
import json
import time
from datetime import datetime
from openai import OpenAI


# 模拟处理逻辑
def demo_function(query):
    print(f"Processing query: {query}")
    response = {"choices": [{"message": {"content": f"Processed: {query}"}}]}
    return response


def save_to_file(file, content, is_question=False):
    """保存对话内容到文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if is_question:
        file.write(f"\n[{timestamp}] Question:\n{content}\n\n[{timestamp}] Answer:\n")
    else:
        file.write(content)


def send_query_to_openai(query, conversation_history, file, chat_history):
    # 配置 OpenAI 客户端
    client = OpenAI(api_key="sk-d80371b5c89a4f79ab6e86ed39b16c8b", base_url="https://api.deepseek.com")

    # 将问题加入历史对话
    conversation_history.append({"role": "user", "content": query})

    # 保存问题到文件
    save_to_file(file, query, is_question=True)

    try:
        # 使用 OpenAI 客户端发送请求，保持上下文
        response1 = client.chat.completions.create(
            model="deepseek-chat",  # 使用 DeepSeek 的聊天模型
            messages=[{"role": "system", "content": "你是一个助手"}] + conversation_history,
            max_tokens=1024,
            temperature=0.7,
            stream=True  # 启用流式返回结果
        )

        # 流式返回数据处理
        answer = ""
        for chunk in response1:
            content = chunk.choices[0].delta.content
            if content:  # 如果 content 不为空
                print(content)  # 输出 content
                answer += content  # 拼接返回内容
                # 更新聊天框
                chat_history.insert(tk.END, f"{content}")
                chat_history.yview(tk.END)
                chat_history.update()  # 更新界面显示

        # 保存回答到文件
        save_to_file(file, answer)
        conversation_history.append({"role": "assistant", "content": answer})

        return answer

    except Exception as e:
        error_msg = f"请求错误: {str(e)}\n"
        print(error_msg)
        save_to_file(file, error_msg)
        return error_msg


def create_gui():
    # 创建主窗口
    root = tk.Tk()
    root.title("deepseek 查询助手")
    root.geometry("500x400")

    # 创建聊天历史区域
    chat_history = scrolledtext.ScrolledText(root, width=60, height=15, wrap=tk.WORD)
    chat_history.pack(pady=10)

    # 创建用户输入框
    user_input = tk.Entry(root, width=60)
    user_input.pack(pady=10)

    # 保存对话历史
    with open("docling.txt", "a", encoding="utf-8") as file:
        conversation_history = []

        def on_send_button_click():
            query = user_input.get().strip()
            if query:
                # 显示问题到聊天框
                chat_history.insert(tk.END, f"你: {query}\n\n")
                chat_history.yview(tk.END)
                # 清空输入框
                user_input.delete(0, tk.END)

                # 调用 OpenAI 接口并获取回答
                answer = send_query_to_openai(query, conversation_history, file, chat_history)

                # 最终显示回答
                # 这里会在流式返回过程中实时显示内容，因此这部分可以选择不再插入最终回答。

        # 创建发送按钮
        send_button = tk.Button(root, text="发送", width=20, command=on_send_button_click)
        send_button.pack()

        # 绑定回车键提交
        user_input.bind("<Return>", lambda event: on_send_button_click())

        # 启动主循环
        root.mainloop()


if __name__ == "__main__":
    create_gui()
