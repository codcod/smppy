import abc
import asyncio
import io
import logging
from typing import Optional, List
from typing import Union

from smpp.pdu.operations import (
    BindTransceiver,
    SubmitSM,
    EnquireLink,
    Unbind,
    DeliverSM,
    DeliverSMResp,
    BindTransceiverResp,
    UnbindResp,
)
from smpp.pdu.pdu_encoding import PDUEncoder
from smpp.pdu.pdu_types import (
    CommandId,
    PDUResponse,
    PDU,
    AddrTon,
    AddrNpi,
    EsmClassMode,
    EsmClass,
    EsmClassType,
    RegisteredDelivery,
    PriorityFlag,
    RegisteredDeliveryReceipt,
    ReplaceIfPresentFlag,
    DataCodingDefault,
    DataCoding,
    PDURequest,
    MoreMessagesToSend,
    CommandStatus,
)
from smpp.pdu.sm_encoding import SMStringEncoder

logger = logging.getLogger(__name__)

from .connection import Connection
from .protocol import SMPPProtocol


class Application(abc.ABC):
    def __init__(self, name: str, logger=None):
        self.name = name

        if not logger:
            logger = logging.getLogger('smpp-app')
        self.logger = logger

    @abc.abstractmethod
    async def connection_bound(
        self, conn: Connection
    ) -> Union[Connection, None]:
        """
        Here is the right place for authenticating the client. If this method does not
        return the (same) connectio instance, the connection will be disconnected

        Args:
            conn: a newly connected client which sent a bind_transceiver request

        Returns:
            the received `Connection` instance to accept the client, or `None` to refuse it

        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def connection_unbound(self, conn: Connection):
        """
        Handle an unbound connection.

        Args:
            conn: the smpp client who sent the unbound command

        Returns:
            the returned value of this handler method is ignored

        """
        raise NotImplementedError()

    @abc.abstractmethod
    async def text_received(
        self,
        conn: Connection,
        source_number: str,
        dest_number: str,
        text: str,
    ):
        """
        This is triggered when a submit_sm is received from the smpp client.

        Args:
            conn: the smpp client from which the sms has been received
            source_number: the phone number of the sender
            dest_number: the phone number of the recipient
            text: the content of the sms

        Returns:
            the returned value of this handler method is ignored

        """
        raise NotADirectoryError()

    def create_server(
        self, loop: asyncio.AbstractEventLoop = None, host='0.0.0.0', port=2775
    ):
        factory = loop.create_server(
            lambda: SMPPProtocol(app=self), host=host, port=port
        )
        server = loop.run_until_complete(factory)
        return server

    def run(
        self, loop: asyncio.AbstractEventLoop = None, host='0.0.0.0', port=2775
    ):
        if loop is None:
            loop = asyncio.get_event_loop()

        server = self.create_server(loop=loop, host=host, port=port)

        self.logger.info(f'Starting server on {host}:{port} ...')

        try:
            loop.run_forever()
        finally:
            self.logger.info('closing server...')
            server.close()
            loop.run_until_complete(server.wait_closed())
            self.logger.info('closing event loop')
            loop.close()
