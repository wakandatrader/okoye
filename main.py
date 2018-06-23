from os import environ
from functools import reduce
from telethon import TelegramClient, events
from yaml import load, YAMLError
from langdetect import detect, lang_detect_exception
import re

import logging
logging.basicConfig(level=logging.INFO)
# logging.debug('dbg')
logging.info('info')

reject_reason = ''

def filter_out(message):

    global reject_reason

    if (len(message) > 500):
        reject_reason = 'length: {} chars'.format(len(message))
        return

    patterns = [
        't.me/joinchat',
        't.me',
        'join'
    ]

    regexes = [ re.compile(pat, re.IGNORECASE) for pat in patterns ]

    results = [ reg.search(message) for reg in regexes ]

    is_filtered_out = reduce(lambda x, y: y if y else x, results)

    if is_filtered_out:
        reject_reason = 'contains invitation'
        return is_filtered_out

    numbers = re.search(r'\d+', message)
    if not numbers:
        reject_reason = 'no number'
        return reject_reason

    try:
        lang = detect(message)
    except lang_detect_exception.LangDetectException as exc:
        print(exc)

    if lang == 'ru':
        reject_reason = 'russian'
        return lang

    return None

def filter_in(message):

    patterns = [
        'buy',
        'entry',
        'sell'
    ]

    regexes = [ re.compile(pat, re.IGNORECASE) for pat in patterns ]

    results = [ reg.search(message) for reg in regexes ]

    is_filtered_in = reduce(lambda x, y: y if y else x, results)

    return is_filtered_in


def main():

    # read channel config from channels.yml
    with open('channels.yml', 'r') as stream:
        try:
            channels = load(stream)
        except YAMLError as exc:
            print(exc)
            return

    session_name = environ.get('TG_SESSION', 'session')
    client = TelegramClient(session_name,
                            int(environ['TG_API_ID']),
                            environ['TG_API_HASH'],
                            proxy=None,
                            update_workers=4,
                            spawn_read_thread=False)

    if 'TG_PHONE' in environ:
        client.start(phone=environ['TG_PHONE'])
    else:
        client.start()

    print(channels)
    source_channels = channels['source']

    def get_entity_id(url):
        channel = client.get_entity(url)
        return channel.id

    channel_ids = list(map(get_entity_id, source_channels))

    target_channel = client.get_entity(channels['target'])

    if channels['reject']:
        reject_channel = client.get_entity(channels['reject'])

    print(channel_ids)

    print(target_channel.id)

    @client.on(events.NewMessage(chats=channel_ids))
    def new_message_handler(update):
        global reject_reason
        reject_reason = ''

        print(update.stringify())
        message_string = update.message.message
        print('main message: {}'.format(message_string))
        filtered = filter_out(message_string)
        if filtered:
            print('filtered: {}'.format(filtered))
            if reject_channel:
                client.forward_messages(reject_channel, update.message)
                debug_message = 'DEBUG: panjang pesan: {}'.format(len(message_string))
                print(debug_message)
                client.send_message(reject_channel, debug_message)
                print('reject_reason: {}'.format(reject_reason))
                if reject_reason:
                    client.send_message(reject_channel, 'DEBUG: Reject reason: {}'.format(reject_reason))

            return

        forward = filter_in(message_string)
        if forward:
            client.forward_messages(target_channel, update.message)
            # client.send_message(target_channel, 'DEBUG: panjang pesan: {}'.format(len(message_string)))

        else:
            if reject_channel:
                client.forward_messages(reject_channel, update.message)
                debug_message = 'DEBUG: panjang pesan: {}'.format(len(message_string))
                print(debug_message)
                client.send_message(reject_channel, debug_message)
                if reject_reason:
                    client.send_message(reject_channel, 'DEBUG: Reject reason: {}'.format(reject_reason))
        return

    print('(Press Ctrl+C to stop this)')
    client.idle()

if __name__ == '__main__':
    main()
