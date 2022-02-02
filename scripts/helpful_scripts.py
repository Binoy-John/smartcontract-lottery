from brownie import (
    network,
    accounts,
    config,
    Contract,
    Lottery,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    interface,
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_account(index=None, id=None):
    # these are the ways to add an account:
    # accounts[0]
    # accounts.add("env")
    # accounts.load("id")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)

    if (
        network.show_active() in FORKED_LOCAL_ENVIRONMENTS
        or network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
    ):
        print("The active network found is : ", network.show_active())
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


def get_contract(contract_name):
    """If you want to use this function, go to the brownie config and add a new entry for
    the contract that you want to be able to 'get'. Then add an entry in the variable 'contract_to_mock'.
    You'll see examples like the 'link_token'.
        This script will then either:
            - Get a address from the config
            - Or deploy a mock to use for a network that doesn't have it
        Args:
            contract_name (string): This is the name that is referred to in the
            brownie config and 'contract_to_mock' variable.
        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            Contract of the type specificed by the dictionary. This could be either
            a mock or the 'real' contract on a live network.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:  # MockV3Aggregator.length
            deploy_mocks()
        contract = contract_type[-1]  # recent MockV3Aggregator[-1]
    else:  # not is local blockchain
        contract_address = config["networks"][network.show_active()][contract_name]
        # address
        # ABI (or Mock)
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


DECIMALS = 8
INITIAL_PRICE = 200000000000


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_PRICE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})

    print("Mocks Deployed!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):  # 0.1 LINK
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(
        contract_address, amount, {"from": account}
    )  # this uses contract
    # link_token_contract = interface.LinkTokenInterface(link_token.address) ##this used interface instead
    # link_token_contract.transfer(contract_address, amount, {"from": account})
    print("Funded the contract!!")
    return tx
