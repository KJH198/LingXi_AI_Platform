import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NodeOutputConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 将客户端添加到组
        await self.channel_layer.group_add(
            "node_output",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # 从组中移除客户端
        await self.channel_layer.group_discard(
            "node_output",
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            node_name = data.get('node_name')
            output = data.get('output')
            
            # 广播消息到所有连接的客户端
            await self.channel_layer.group_send(
                "node_output",
                {
                    "type": "node.output",
                    "message": {
                        "node_name": node_name,
                        "output": output
                    }
                }
            )
        except Exception as e:
            print(f"处理WebSocket消息时出错: {e}")

    async def node_output(self, event):
        try:
            await self.send(text_data=json.dumps(event["message"]))
        except Exception as e:
            print(f"发送WebSocket消息时出错: {e}") 