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

from .protocol import SMPPProtocol

logger = logging.getLogger(__name__)


class Connection:
    def __init__(
        self,
        protocol: SMPPProtocol,
        system_id: str,
        password: str,
        system_type: str,
        interface_version: int,
        addr_ton: AddrTon,
        addr_npi: AddrNpi,
    ):
        self._protocol: SMPPProtocol = protocol
        self.system_id: str = system_id
        self.password = password
        self.system_type = system_type
        self.interface_version = interface_version
        self.addr_ton = addr_ton
        self.addr_npi = addr_npi

    async def send_text(self, source: str, dest: str, text: str) -> None:
        await self._protocol.send_deliver_sm(
            source_addr=source,
            destination_addr=dest,
            text=text,
            source_addr_npi=self.addr_npi,
            dest_addr_npi=self.addr_npi,
            source_addr_ton=self.addr_ton,
            dest_addr_ton=self.addr_ton,
        )
