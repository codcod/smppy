import logging
import threading
import time

import smpplib.client
import smpplib.consts
import smpplib.gsm

# if you want to know what's happening
logging.basicConfig(
    level='DEBUG', handlers=[logging.FileHandler('client.log')]
)


def message_sent(pdu):
    logging.debug(f'sent {pdu.sequence} {pdu.message_id}\n')


def message_received(pdu):
    logging.debug(f'received: {pdu.short_message}\n')


def send_message(message: str, sender: str, receiver: str):
    # Two parts, UCS2, SMS with UDH
    parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(message)
    print(f'PARTS = {parts}')
    print(f'ENCODING_FLAG = {encoding_flag}')
    print(f'MSG_TYPE_FLAG = {msg_type_flag}')

    for part in parts:
        pdu = client.send_message(
            source_addr_ton=smpplib.consts.SMPP_TON_INTL,
            # source_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
            # Make sure it is a byte string, not unicode:
            source_addr=sender,
            dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
            # dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
            # Make sure thease two params are byte strings, not unicode:
            destination_addr=receiver,
            short_message=part,
            data_coding=encoding_flag,
            esm_class=msg_type_flag,
            registered_delivery=True,
        )
        print(pdu.sequence)


if __name__ == '__main__':
    client = smpplib.client.Client('localhost', 2775)
    client.set_message_sent_handler(message_sent)
    client.set_message_received_handler(message_received)
    client.connect()
    client.bind_transceiver(system_id='login', password='secret')

    t = threading.Thread(target=client.listen)
    t.start()

    for _ in range(3):
        send_message('Hellołą', 'Me', 'You')

    t.join()
    client.unbind()
    time.sleep(1)
    client.disconnect()

    print('Done')