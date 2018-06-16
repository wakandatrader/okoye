from os import environ
from functools import reduce
from telethon import TelegramClient, events
from yaml import load, YAMLError
from langdetect import detect
import re

import logging
logging.basicConfig(level=logging.INFO)
# logging.debug('dbg')
logging.info('info')

def filter_out(message):

    patterns = [
        't.me/joinchat'
    ]

    regexes = [ re.compile(pat, re.IGNORECASE) for pat in patterns ]

    results = [ reg.search(message) for reg in regexes ]

    is_filtered_out = reduce(lambda x, y: y if y else x, results)

    if is_filtered_out:
        return is_filtered_out

    lang = detect(message)

    if lang == 'ru':
        return lang

    return None

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

    print(channel_ids)

    print(target_channel.id)

    @client.on(events.NewMessage(chats=channel_ids))
    def new_message_handler(update):
        print(update.stringify())
        message_string = update.message.message
        print('main message: {}'.format(message_string))
        filtered = filter_out(message_string)
        if filtered:
            print('filtered: {}'.format(filtered))
            return
        client.forward_messages(target_channel, update.message)

    print('(Press Ctrl+C to stop this)')
    client.idle()

if __name__ == '__main__':
    main()
