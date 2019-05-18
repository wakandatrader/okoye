import re
from datetime import datetime
import pickle

def transform(msg, timestamp):
    cmd = re.compile(r'^([A-Z]{6} ).*((BUY|SELL) ?(LIMIT|STOP)?)\D*(\d+\.?\d*)', re.IGNORECASE | re.MULTILINE)
    cmt = cmd.search(msg)

    if not cmt:
        return None

    # header
    pair = cmt.group(1).strip().upper()
    optext = cmt.group(2).strip().upper()
    if optext in ['BUY', 'SELL']:
        op = 'OP_' + optext
    else:
        op = optext.replace(' ', '')
    price = cmt.group(5)
    header = '${}#{}@{}'.format(pair, op, price)

    # footer
    idstr = timestamp.strftime('%d.%m.%Y.%H:%M')
    footer = 'ID{}\n'.format(idstr)

    #tp
    tpp = re.compile(r'TP (\d+\.?\d*)', re.IGNORECASE)
    tpt = tpp.search(msg)
    if tpt:
        tp = tpt.group(1)
        tpstr = 'TP{}'.format(tp)
    else:
        tp = None
        tpstr = ''

    # sl
    slp = re.compile(r'SL (\d+\.?\d*)', re.IGNORECASE)
    slt = slp.search(msg)
    if slt:
        sl = slt.group(1)
        slstr = 'SL{}'.format(sl)
    else:
        sl = None
        slstr = ''

    # result
    result = header + slstr + tpstr + footer

    actions = []
    action_dict = {
        'result_str': result,
        'op': op,
        'open': price,
        'sl': sl,
        'tp': tp,
    }

    actions.append(action_dict)
    res_dict = {
        'pair': pair,
        'id': idstr,
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
    bere = re.compile(r'(breakeven| be )', re.IGNORECASE | re.MULTILINE)
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
