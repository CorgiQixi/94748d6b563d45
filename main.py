import streamlit as st
from openai import OpenAI
import pandas as pd
import os
import edge_tts
import asyncio

# 使用环境变量存储 API 密钥
API_KEY = 'sk-wnYQhNW8w4uX3MN1BYGp9ApHxqunu5fTr5peZc9B2GwoiYCB'

st.set_page_config(page_title="Qixi English", page_icon='favicon.png', menu_items=None)
st.title("Qixi English")

st.write('用之前必须先拜几下七喜')


# 使用 Edge TTS 生成音频文件
async def generate_tts(word, voice="en-US-JennyNeural"):
    output_file = f"{word}.mp3"
    communicate = edge_tts.Communicate(word, voice)
    await communicate.save(output_file)
    return output_file


def chat(key, message):
    client = OpenAI(
        api_key=key,
        base_url="https://api.moonshot.cn/v1",
    )

    try:
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system",
                 "content": '你是ChatGPT4o，由 OpenAI 提供的人工智能助手。你需要为用户生成相应英语，并且以Python列表的形式返回。如，用户输入：“水果”，你需要返回：["apple","pear"]///["ˈap(ə)l","per"]///["苹果","梨子"]。当然，实际上会有更多水果。'},
                {"role": "user", "content": f"{message}"}
            ],
            temperature=0.3,
        )
        result = completion.choices[0].message.content
        return result
    except Exception as e:
        st.error(f"请求失败: {e}")
        return None


user_input = st.text_input("输入你要说的话：")
check = st.button("确认")

# 检查用户输入是否有效
if check and user_input:
    output = chat(key=API_KEY, message=user_input)
    if output:
        # 分割输出
        parts = output.split('///')
        words = eval(parts[0])
        phonetics = eval(parts[1])
        translations = eval(parts[2])

        # 创建数据框
        data = {
            "单词": words,
            "音标": phonetics,
            "中文翻译": translations
        }
        df = pd.DataFrame(data)

        # 将数据保存到会话状态
        st.session_state['df'] = df

# 确保在重绘页面时保持数据框
if 'df' in st.session_state:
    df = st.session_state['df']

    # 显示为表格
    for index, row in df.iterrows():
        st.write(f"{row['单词']}  {row['音标']}  {row['中文翻译']}")

        # 添加发音按钮
        if st.button(f"发音: {row['单词']}", key=f"pronounce-{index}"):
            # 生成音频文件
            audio_file = asyncio.run(generate_tts(row['单词']))
            audio_bytes = open(audio_file, "rb").read()
            st.audio(audio_bytes, format="audio/mp3")
