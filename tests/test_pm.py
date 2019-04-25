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
