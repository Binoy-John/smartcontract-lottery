import time
from scripts.helpful_scripts import get_account, get_contract, fund_with_link
from brownie import Lottery, network, config, accounts


def deploy_lottery():

    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["key_hash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get(
            "verify", False
        ),  # The get verify function will see the verify field. if there is no verify field found in the config, it will assume it as false
    )
    print("Deployed Lottery!")
    return lottery
    # print(account)


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("Lottery has started!!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee({"from": account}) + 6900
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("You entered the lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    ending_tx = lottery.endLottery({"from": account})
    ending_tx.wait(1)
    time.sleep(180)
    print("The new winner is", lottery.recentWinner())


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
