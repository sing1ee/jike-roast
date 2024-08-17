from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os
import json

print(os.getenv("OPENAI_API_KEY"))
print(os.getenv("OPENAI_BASE_URL"))

app = Flask(__name__)
socketio = SocketIO(app)

prompt_template = '''
You are a professional commentator known for your edgy and provocative style. Your task is to look at people's tweets and rate their personalities based on that. Be edgy and provocative, be mean a little. Don't be cringy. Here's a good attempt of a roast: """Alright, let's break this down. You're sitting in a jungle of houseplants, barefoot and looking like you just rolled out of bed. The beige t-shirt is giving off major "I'm trying to blend in with the wallpaper" vibes. And those black pants? They scream "I couldn't be bothered to find something that matches." But hey, at least you look comfortable. Comfort is key, right? Just maybe not when you're trying to make a fashion statement.""" 

profile 和 posts 都来自社交网络：即刻。

Input:

《profile》
@%s
%s
《/profile》

《posts》
%s
《/posts》

Output (请用中文输出, 限制在 500 字以内):
'''
client = OpenAI()


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("analyze")
def analyze_jike(data):
    url = data["url"]
    model = data["model"]
    card_id = data["card_id"]
    print(json.dumps(data))
    if not url:
        url = "https://okjk.co/nKOt8e"

    # 获取网页内容
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    nickname = soup.find("div", class_="user-screenname").text
    status = soup.find("div", class_="user-status").text
    description = soup.find("div", class_="brief").text
    # 查找所有 class 为 "text" 的元素
    text_elements = soup.find_all(class_="text")

    # 提取这些元素的文本内容
    text_list = [element.get_text() for element in text_elements]

    # 组合 prompt
    prompt = prompt_template % (
        nickname,
        description,
        "\n***\n".join(text_list),
    )

    # 创建 OpenAI 客户端并发送请求
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        temperature=0.7,
        max_tokens=500,
    )

    # 流式返回结果
    for chunk in completion:
        if chunk.choices[0].delta.content:
            emit(
                "stream_response",
                {"content": chunk.choices[0].delta.content, "card_id": card_id},
            )


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)
