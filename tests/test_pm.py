import pytest
import pickle
from okoye import pm_transform

@pytest.fixture()
def messages():
    with open('message.pickle', 'rb') as msgf:
        msgs = pickle.load(msgf)
    return msgs

def test_buy(messages):
    """Test Buy"""
    message = "Gbpusd buy now at cmp 1.3075"

    replied = messages[6]
    result = pm_transform.transform(message, replied['date'])

    assert result['actions'][0]['result_str'] == '$GBPUSD#OP_BUY@1.3075ID13.04.2019.10:26\n'
    assert len(result['actions']) == 1

def test_buy_with_sl(messages):
    """Test SL"""
    message = """Gbpusd buy now at cmp 1.3075
Sl 1.3020
Tp 1.3170
"""

    replied = messages[6]
    result = pm_transform.transform(message, replied['date'])

    assert result['actions'][0]['result_str'] == '$GBPUSD#OP_BUY@1.3075SL1.3020TP1.3170ID13.04.2019.10:26\n'
    assert len(result['actions']) == 1

def test_gold(messages):
    """Test Gold"""
    message = """Gold sell now at cmp 1310
Sl 1316
Tp 1300"""

    replied = messages[6]
    result = pm_transform.transform(message, replied['date'])

    assert result == None


def test_breakeven(messages):
    """Test Breakeven"""
    message = "15 plus pips move sl breakeven just✅✅"

    replied = messages[6]
    result = pm_transform.transform(message, replied['date'])

    result = pm_transform.reply_transform(message, replied)
    assert result['actions'][0]['result_str'] == '$EURNZD#MODIFYSL1.67120ID13.04.2019.10:26\n'
    assert len(result['actions']) == 1

def test_closefull(messages):
    """Test close full"""
    message = "close full✅✅"

    replied = messages[6]
    result = pm_transform.transform(message, replied['date'])

    result = pm_transform.reply_transform(message, replied)
    assert result['actions'][0]['result_str'] == '$EURNZD#CLOSEFULLID13.04.2019.10:26\n'
    assert len(result['actions']) == 1

def test_closehalf_breakeven(messages):
    """Test close half and breakeven"""
    message = "40 pips close half put sl breakeven ✅✅"

    replied = messages[6]
    result = pm_transform.transform(message, replied['date'])

    result = pm_transform.reply_transform(message, replied)
    assert result['actions'][0]['result_str'] == '$EURNZD#CLOSEHALFID13.04.2019.10:26\n'
    assert result['actions'][1]['result_str'] == '$EURNZD#MODIFYSL1.67120ID13.04.2019.10:26\n'
    assert len(result['actions']) == 2

def test_conditional_closefull(messages):
    """Test conditional closefull"""
    message = "close full in 40 pips if breakeven  not hit ✅✅ if hit  ignore✅💰"

    replied = messages[6]
    result = pm_transform.transform(message, replied['date'])

    result = pm_transform.reply_transform(message, replied)
    print(result)
    assert False
