import re
from datetime import datetime
import pickle

message = """EURNZD SELL 1.67120
TP 1.66000 | SL 1.67800
(Note: Last Entry Hit Breakeven)
"""

reply_message = "30+ Pips Running ✅✅ Close Half & Set B BE."

def af_transform(msg, timestamp):
    cmd = re.compile(r'^([A-Z]*) ((BUY|SELL) ?(LIMIT|STOP)?) ([\w\.]*)', re.MULTILINE)
    cmt = cmd.search(msg)
    # print(cmt.group(3))
    if not cmt:
        return None
    if cmt.group(2) in ['BUY', 'SELL']:
        op = 'OP_' + cmt.group(2)
    else:
        op = cmt.group(2).replace(' ', '')
    
    tpsl = re.compile(r'^TP ([\w\.]*) \| SL ([\w\.]*)', re.MULTILINE)
    tmt = tpsl.search(msg)
    # print(tmt.group(1), tmt.group(2))
    if not tmt:
        return None
    
    # print(timestamp.strftime('%d.%m.%Y.%H:%M'))
    result = '${}#{}@{}SL{}TP{}ID{}\n'.format(
        cmt.group(1),
        op,
        cmt.group(3),
        tmt.group(2),
        tmt.group(1),
        timestamp.strftime('%d.%m.%Y.%H:%M')
    )
    actions = []
    action_dict = {
        'result_str': result,
        'op': op,
        'open': cmt.group(3),
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

def af_reply_transform(msg_string, replied):
    actions = []
    
    # CLOSEHALF
    chre = re.compile(r'(close *half)', re.IGNORECASE | re.MULTILINE)
    chmo = chre.search(msg_string)
    if chmo:
        result_str = '${}#CLOSEHALF@ID{}\n'.format(replied.get('pair', ''), replied.get('id', ''))
        action = {
            'result_str': result_str,
            'op': 'CLOSEHALF'
        }
        actions.append(action)

    # BREAKEVEN
    bere = re.compile(r'(set *(breakeven|be))', re.IGNORECASE | re.MULTILINE)
    bemo = chre.search(msg_string)
    if chmo:
        result_str = '${}#MODIFY@ID{}\n'.format(replied.get('pair', ''), replied.get('id', ''))
        action = {
            'result_str': result_str,
            'op': 'CLOSEHALF'
        }
        actions.append(action)
    
        
    result_dict = {
        'pair': replied.get('pair', ''),
        'id': replied.get('id', ''),
        'actions': actions
    }
    return result_dict

with open('message.pickle', 'rb') as msgf:
    messages = pickle.load(msgf)
    print(messages)
    print(len(messages))

replied = messages[6]
print(replied)

print(af_reply_transform(reply_message, replied))
