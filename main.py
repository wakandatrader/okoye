from os import environ
from functools import reduce
from telethon import sync, TelegramClient, events
from yaml import load, YAMLError, FullLoader
from langdetect import detect, lang_detect_exception
import re
from datetime import datetime
import pickle

from okoye import af_transform

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
        'join',
        'V_ipman'
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
            channels = load(stream, Loader=FullLoader)
        except YAMLError as exc:
            print(exc)
            return

    session_name = environ.get('TG_SESSION', 'session')
    client = TelegramClient(session_name,
                            int(environ['TG_API_ID']),
                            environ['TG_API_HASH'],
                            proxy=None)

    print('phone: {}', format(environ['TG_PHONE']))
    # if 'TG_PHONE' in environ:
    #     client.start(phone=environ['TG_PHONE'])
    # else:
    #     client.start()
    with client:

        print(channels)
        source_channels = channels['source']

        def get_entity_id(url):
            channel = client.get_entity(url)
            return channel.id

        channel_ids = list(map(get_entity_id, source_channels))

        target_channel = client.get_entity(channels['target'])

        if channels['reject']:
            reject_channel = client.get_entity(channels['reject'])
        else:
            reject_channel = None

        print(channel_ids)

        print(target_channel.id)

        @client.on(events.NewMessage(chats=channel_ids))
        async def new_message_handler(update):
            global reject_reason
            reject_reason = ''

            # to_id=PeerChannel(
            #                        channel_id=1377311260
            #                                        ),
            print(update.message.to_id)

            print(update.message.stringify())
            message_string = update.message.message
            print('main message: {}'.format(message_string))
            print('channel_id: {}, author: {}'.format(update.message.to_id, update.message.post_author))

            channel = None
            try:
                channel = await client.get_entity(update.message.to_id.channel_id)
            except ValueError as err:
                print(err)

            if channel:
                print(channel.title)
            # filtered = filter_out(message_string)

            filtered = False

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

            # forward = filter_in(message_string)
            forward = True if channel else False
            if forward:
                msg_obj = {}
                with open('message.pickle', 'rb') as msgf:
                    messages = pickle.load(msgf)
                    print(messages)

                if message_string:
                    sent = None
                    replied = None

                    if update.message.reply_to_msg_id:
                        replied = next((m for m in messages if m['channel_id'] == update.message.to_id.channel_id and
                                       m['source_msg_id'] == update.message.reply_to_msg_id), None)
                        if replied:
                            print(replied)
                            original_message = await client.get_messages(target_channel, ids=replied['msg_id'])

                            if original_message:
                                sent = await original_message.reply(message_string)
                    if not sent:
                        sent = await client.send_message(target_channel, message_string)

                    print(sent.stringify())
                        # $GBPUSD#OP_BUY@1.30505SL1.31005TP1.30205ID08.04.2019.18:26

                    if update.message.to_id.channel_id == channel_ids[0]:
                        # afinito
                        af_res = None
                        if replied:
                            af_res = af_transform.reply_transform(message_string, replied)
                        else:
                            af_res = af_transform.transform(message_string, update.message.date)

                        if af_res:
                            with open('afinito.txt', 'a') as af:
                                for action in af_res['actions']:
                                    af.write(action.result_str)

                                msg_obj = af_res
                        else:
                            print('Error parsing\n{}'.format(message_string))

                    elif update.message.to_id.channel_id == channel_ids[3]:
                        # okoye_private
                        ok_res = None
                        if replied:
                            ok_res = af_transform.reply_transform(message_string, replied)
                        else:
                            ok_res = af_transform.transform(message_string, update.message.date)

                        if ok_res:
                            with open('okoye.txt', 'a') as okf:
                                for action in af_res['actions']:
                                    okf.write(action.result_str)

                                msg_obj = ok_res
                        else:
                            print('Error parsing\n{}'.format(message_string))

                    msg_obj['msg_id'] = sent.id
                    msg_obj['reply_to_msg_id'] = sent.reply_to_msg_id
                    msg_obj['message_string'] = message_string

                else:
                    await client.forward_messages(target_channel, update.message)
                    print(update.message.stringify())
                    # client.send_message(target_channel, 'DEBUG: panjang pesan: {}'.format(len(message_string)))
                    # save in general file for analysis:

                with open('raw.txt', 'a') as raw_f:
                    raw_f.write('{}\n{}\n'.format(channel.title, message_string))

                msg_obj['channel'] = channel.title
                msg_obj['channel_id'] = update.message.to_id.channel_id
                msg_obj['source_msg_id'] = update.message.id
                msg_obj['source_reply_to_msg_id'] = update.message.reply_to_msg_id
                if update.message.media:
                    msg_obj['media'] = update.message.media
                msg_obj['date'] = update.message.date
                messages.append(msg_obj)
                with open('message.pickle', 'w+b') as msgf:
                    print('dumping messages')
                    pickle.dump(messages, msgf)
            # else:
            #     if reject_channel:
            #         client.forward_messages(reject_channel, update.message)
            #         debug_message = 'DEBUG: panjang pesan: {}'.format(len(message_string))
            #         print(debug_message)
            #         client.send_message(reject_channel, debug_message)
            #         client.send_message(reject_channel, 'DEBUG: Reject reason: no signal keywords')
            return

        print('(Press Ctrl+C to stop this)')
        client.run_until_disconnected()

if __name__ == '__main__':
    main()
