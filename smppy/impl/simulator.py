import asyncio
import logging
from typing import Union, List

from smppy.app import Application
from smppy.connection import Connection

logging.basicConfig(level=logging.DEBUG)


class Simulator(Application):
    def __init__(self, name: str, logger):
        self.connections: List[Connection] = []
        super(Simulator, self).__init__(name=name, logger=logger)

    async def connection_bound(
        self, conn: Connection
    ) -> Union[Connection, None]:
        self.connections.append(conn)
        self.logger.debug(f'Client {conn.system_id} connected.')
        return conn

    async def connection_unbound(self, conn: Connection):
        self.connections.remove(conn)

    async def text_received(
        self, conn: Connection, source_number: str, dest_number: str, text: str
    ):
        self.logger.debug(f'Received {text} from {source_number}')
        await conn.send_text(source=dest_number, dest=source_number, text=text)


loop = asyncio.get_event_loop()

app = Simulator(name='smppy', logger=logging.getLogger('smppy'))

app.run(loop=loop, host='localhost', port=2775)
