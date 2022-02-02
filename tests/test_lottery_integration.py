from brownie import Lottery, accounts, config, network, web3, exceptions
import pytest
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3
import time

from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    fund_with_link,
    get_account,
)


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()

    account = get_account()
    fee = lottery.getEntranceFee() + 6969
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": fee})
    lottery.enter({"from": account, "value": fee})
    lottery.enter({"from": account, "value": fee})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    print("lottery ended and waiting for result...")
    time.sleep(180)
    print("the winner is calculated as", lottery.recentWinner())
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
