import os
import botpy
from botpy.message import C2CMessage

class MyClient(botpy.Client):

    async def on_c2c_message_create(
        self, message: C2CMessage
    ):
        await message._api.post_c2c_message(
            openid=message.author.user_openid,
            msg_type=0,
            msg_id=message.id,
            content="你好！我是你的QQ AI机器人，连接成功！"
        )

intents = botpy.Intents(public_messages=True)

client = MyClient(intents=intents)

client.run(
    appid=os.environ["QQ_APP_ID"],
    secret=os.environ["QQ_APP_SECRET"]
)
