import pytest
import pickle
from okoye import af_transform

@pytest.fixture()
def messages():
    with open('message.pickle', 'rb') as msgf:
        msgs = pickle.load(msgf)
    return msgs

def test_sell(messages):
    """Test Sell"""
    message = """EURNZD SELL 1.67120
TP 1.66000 | SL 1.67800
(Note: Last Entry Hit Breakeven)
"""
    replied = messages[6]
    result = af_transform.transform(message, replied['date'])

    assert result['actions'][0]['result_str'] == '$EURNZD#OP_SELL@1.67120SL1.67800TP1.66000ID13.04.2019.10:26\n'
    assert len(result['actions']) == 1

def test_ch_be(messages):
    """Test Close Half and Breakeven"""
    reply_message = "30+ Pips Running ✅✅ Close Half & Set BE."
    replied = messages[6]

    result = af_transform.reply_transform(reply_message, replied)
    assert result['actions'][0]['result_str'] == '$EURNZD#CLOSEHALFID13.04.2019.10:26\n'
    assert result['actions'][1]['result_str'] == '$EURNZD#MODIFYSL1.67120ID13.04.2019.10:26\n'
    assert len(result['actions']) == 2

def test_ch_be2(messages):
    """Test Close Half and Breakeven 2"""
    reply_message = "42+ Pips Profit ✅✅ Set Breakeven & Close Half.."
    replied = messages[6]

    result = af_transform.reply_transform(reply_message, replied)
    assert result['actions'][0]['result_str'] == '$EURNZD#CLOSEHALFID13.04.2019.10:26\n'
    assert result['actions'][1]['result_str'] == '$EURNZD#MODIFYSL1.67120ID13.04.2019.10:26\n'
    assert len(result['actions']) == 2

def test_ch_ss(messages):
    """Test Close Half and Set SL"""
    reply_message = "25+ Pips Running ✅✅ Close Half & Set 79.480"

    replied = messages[6]

    result = af_transform.reply_transform(reply_message, replied)
    print(result)
    assert result['actions'][0]['result_str'] == '$EURNZD#CLOSEHALFID13.04.2019.10:26\n'
    assert result['actions'][1]['result_str'] == '$EURNZD#MODIFYSL79.480ID13.04.2019.10:26\n'
    assert len(result['actions']) == 2

def test_ch_ss2(messages):
    """Test Close Half and Set SL 2"""
    reply_message = "32+ Pips Running ✅✅ Close Half & Set SL 1.67100"
    replied = messages[6]

    result = af_transform.reply_transform(reply_message, replied)
    print(result)
    assert result['actions'][0]['result_str'] == '$EURNZD#CLOSEHALFID13.04.2019.10:26\n'
    assert result['actions'][1]['result_str'] == '$EURNZD#MODIFYSL1.67100ID13.04.2019.10:26\n'
    assert len(result['actions']) == 2

def test_ss(messages):
    """Test Set SL"""
    reply_message = "EURNZD SHIFT SL 1.56500"
    replied = messages[6]

    result = af_transform.reply_transform(reply_message, replied)
    print(result)
    assert result['actions'][0]['result_str'] == '$EURNZD#MODIFYSL1.56500ID13.04.2019.10:26\n'
    assert len(result['actions']) == 1

def test_cf(messages):
    """Test Close Full"""
    reply_message = "60+ Pips Close Full ✅✅"
    replied = messages[6]

    result = af_transform.reply_transform(reply_message, replied)
    print(result)
    assert result['actions'][0]['result_str'] == '$EURNZD#CLOSEFULLID13.04.2019.10:26\n'
    assert len(result['actions']) == 1

def test_cf2(messages):
    """Test Close Full 2"""
    reply_message = "60+ Pips Closed Full ✅✅"
    replied = messages[6]

    result = af_transform.reply_transform(reply_message, replied)
    print(result)
    assert result['actions'][0]['result_str'] == '$EURNZD#CLOSEFULLID13.04.2019.10:26\n'
    assert len(result['actions']) == 1
