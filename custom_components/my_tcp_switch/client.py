import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

class TCPClient:
    """TCP通信客户端"""
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None

    async def connect(self):
        """建立TCP连接"""
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port
            )
            return True
        except Exception as e:
            _LOGGER.error("连接失败: %s", e)
            return False

    async def send_command(self, command: str):
        """发送控制指令"""
        if not self.writer:
            return False
        try:
            self.writer.write(command.encode())
            await self.writer.drain()
            return True
        except Exception as e:
            _LOGGER.error("指令发送失败: %s", e)
            return False