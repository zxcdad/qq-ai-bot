
import os
import json
import asyncio
import urllib.request
import urllib.error
import botpy

from botpy.message import C2CMessage

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openrouter/free"

# 保存每位用户最近的对话
chat_histories = {}

SYSTEM_PROMPT = (
    "你是一个友好、聪明的QQ AI助手。"
    "请使用中文回答，表达自然，回答清晰。"
)

def ask_ai(history):
    api_key = os.environ["OPENROUTER_API_KEY"]

    payload = {
        "model": MODEL,
        "messages": history,
        "max_tokens": 600
    }

    request = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=90) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["choices"][0]["message"]["content"]


class MyClient(botpy.Client):

    async def on_c2c_message_create(self, message: C2CMessage):
        user_id = message.author.user_openid
        user_text = (message.content or "").strip()

        if not user_text:
            return

        history = chat_histories.setdefault(
            user_id,
            [{"role": "system", "content": SYSTEM_PROMPT}]
        )

        history.append({
            "role": "user",
            "content": user_text[:3000]
        })

        # 只保留最近6轮对话
        history[:] = [history[0]] + history[-12:]

        try:
            answer = await asyncio.to_thread(ask_ai, history)

            if not answer:
                answer = "抱歉，我暂时没有生成有效回复。"

            history.append({
                "role": "assistant",
                "content": answer
            })

            # QQ消息长度控制
            answer = answer[:1800]

        except urllib.error.HTTPError as e:
            print("AI API HTTP错误：", e.code)
            answer = "AI服务暂时繁忙，请稍后再试。"

        except Exception as e:
            print("AI请求失败：", type(e).__name__)
            answer = "AI暂时无法回答，请稍后再试。"

        await message._api.post_c2c_message(
            openid=user_id,
            msg_type=0,
            msg_id=message.id,
            content=answer
        )


intents = botpy.Intents(public_messages=True)

client = MyClient(intents=intents)

client.run(
    appid=os.environ["QQ_APP_ID"],
    secret=os.environ["QQ_APP_SECRET"]
)
