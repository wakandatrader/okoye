import re
from datetime import datetime
import pickle

def transform(msg, timestamp):
    cmd = re.compile(r'^([A-Z]*) ((BUY|SELL) ?(LIMIT|STOP)?) (\d+\.?\d*)', re.MULTILINE)
    cmt = cmd.search(msg)
    # print(cmt.group(3))
    if not cmt:
        return None
    if cmt.group(2) in ['BUY', 'SELL']:
        op = 'OP_' + cmt.group(2)
    else:
        op = cmt.group(2).replace(' ', '')

    tpsl = re.compile(r'^TP (\d+\.?\d*) \| SL (\d+\.?\d*)', re.MULTILINE)
    tmt = tpsl.search(msg)
    # print(tmt.group(1), tmt.group(2))
    if not tmt:
        return None

    # print(timestamp.strftime('%d.%m.%Y.%H:%M'))
    result = '${}#{}@{}SL{}TP{}ID{}\n'.format(
        cmt.group(1),
        op,
        cmt.group(5),
        tmt.group(2),
        tmt.group(1),
        timestamp.strftime('%d.%m.%Y.%H:%M')
    )
    actions = []
    action_dict = {
        'result_str': result,
        'op': op,
        'open': cmt.group(5),
        'sl': tmt.group(2),
        'tp': tmt.group(1),
    }
    actions.append(action_dict)
    res_dict = {
        'pair': cmt.group(1),
        'id': timestamp.strftime('%d.%m.%Y.%H:%M'),
        'actions': actions
    }
    return res_dict

def reply_transform(msg_string, replied):
    actions = []

    # CLOSEFULL
    cfre = re.compile(r'close(d)? *full', re.IGNORECASE | re.MULTILINE)
    cfmo = cfre.search(msg_string)
    if cfmo:
        result_str = '${}#CLOSEFULLID{}\n'.format(replied.get('pair', ''), replied.get('id', ''))
        action = {
            'result_str': result_str,
            'op': 'CLOSEFULL'
        }
        actions.append(action)

    # CLOSEHALF
    chre = re.compile(r'close(d)? *half', re.IGNORECASE | re.MULTILINE)
    chmo = chre.search(msg_string)
    if chmo:
        result_str = '${}#CLOSEHALFID{}\n'.format(replied.get('pair', ''), replied.get('id', ''))
        action = {
            'result_str': result_str,
            'op': 'CLOSEHALF'
        }
        actions.append(action)

    # BREAKEVEN
    bere = re.compile(r'(set *(breakeven|be))', re.IGNORECASE | re.MULTILINE)
    bemo = bere.search(msg_string)

    if bemo:
        past_actions = replied.get('actions', [])
        first_action = None
        if past_actions:
            first_action = past_actions[0]
        if first_action:
            new_sl = first_action.get('open', 0)
        else:
            new_sl = 0

        result_str = '${}#MODIFYSL{}ID{}\n'.format(replied.get('pair', ''), new_sl, replied.get('id', ''))
        action = {
            'result_str': result_str,
            'op': 'MODIFY',
            'sl': new_sl
        }
        actions.append(action)

    # SET SL
    ssre = re.compile(r'((set|move|shift|sl) +)+(\d+\.?\d*)', re.IGNORECASE | re.MULTILINE)
    ssmo = ssre.search(msg_string)

    if ssmo:
        print(ssmo.group(2))
        new_sl = ssmo.group(3)

        result_str = '${}#MODIFYSL{}ID{}\n'.format(replied.get('pair', ''), new_sl, replied.get('id', ''))
        action = {
            'result_str': result_str,
            'op': 'MODIFY',
            'sl': new_sl
        }
        actions.append(action)

    result_dict = {
        'pair': replied.get('pair', ''),
        'id': replied.get('id', ''),
        'actions': actions
    }
    return result_dict

if __name__ == '__main__':
    message = """EURNZD SELL 1.67120
TP 1.66000 | SL 1.67800
(Note: Last Entry Hit Breakeven)
"""

    reply_message = "30+ Pips Running ✅✅ Close Half & Set BE."

    with open('message.pickle', 'rb') as msgf:
        messages = pickle.load(msgf)
        print(messages)
        print(len(messages))

    replied = messages[6]
    print(replied)

    print(reply_transform(reply_message, replied))
