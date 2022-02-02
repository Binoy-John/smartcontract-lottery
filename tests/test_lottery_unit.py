# 0.020 eth or 20000000000000000 gwei
from brownie import Lottery, accounts, config, network, web3, exceptions
import pytest
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3

from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    fund_with_link,
    get_account,
    get_contract,
)


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act
    # 2000 eth/usd
    # 2000/1 == 50/x  => 0.025
    expected_entry_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    # assert
    assert expected_entry_fee == entrance_fee


def test_cant_enter_unless_started():
    # arrange
    account = get_account()
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    fee = lottery.getEntranceFee() + 200
    # act

    # assert
    with pytest.raises(AttributeError):
        lottery.enter({"from": account, "value": fee})


def can_start_and_enter_lottery():
    # arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    fee = lottery.getEntranceFee() + 200

    lottery.startLottery({"from": account})
    # act
    lottery.enter({"from": account, "value": fee})
    # assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    # arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    fee = lottery.getEntranceFee() + 200
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": fee})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    # arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    account = get_account()
    lottery = deploy_lottery()
    lottery.startLottery({"from": account})
    fee = lottery.getEntranceFee() + 6969
    lottery.enter({"from": account, "value": fee})
    lottery.enter({"from": get_account(index=2), "value": fee})
    lottery.enter({"from": get_account(index=3), "value": fee})
    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 666
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from": account}
    )  # pretending to be a chainlink node
    # 666%3 == 0
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()
    print("the recent winner is", lottery.recentWinner())
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == (starting_balance_of_account + balance_of_lottery)
