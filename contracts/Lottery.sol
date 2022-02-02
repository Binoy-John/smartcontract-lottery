// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is Ownable, VRFConsumerBase {
    address payable[] public players;
    uint256 public randomness;
    address payable public recentWinner;
    uint256 public usdEntryFee;
    uint256 public fee;
    bytes32 public keyhash;
    AggregatorV3Interface internal ethUsdPriceFeed; //gets pricefeed
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    } //enum helps us to create a new data type. this enum tells us the phase that the lottery is currently in
    LOTTERY_STATE public lottery_state;

    event RequestedRandomness(bytes32 requestId);

    constructor(
        address _priceFeedAddress,
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyhash
    ) VRFConsumerBase(_vrfCoordinator, _link) {
        lottery_state = LOTTERY_STATE.CLOSED;
        usdEntryFee = 50 * (10**18); // initialize entry fee 50 usd to 18 decimals
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress); // _priceFeedAddress input from the config file
        keyhash = _keyhash;
        fee = _fee;
    }

    function enter() public payable {
        //this is a payable function because users will pay with this
        require(
            lottery_state == LOTTERY_STATE.OPEN,
            "Please wait for the lottery to begin!"
        );

        //50$ minimum
        require(msg.value > getEntranceFee(), "Not enough ETH!");
        players.push(payable(msg.sender));
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * (10**10); //adjusting it for the 18 decimal places, and converting it to uint256
        uint256 costToEnter = (usdEntryFee * (10**18)) / adjustedPrice;
        return costToEnter;
    }

    function startLottery() public {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "lottery has already started!"
        ); //check if the lottery is already open or not
        lottery_state = LOTTERY_STATE.OPEN; // set lottery state to open
    }

    function endLottery() public {
        // uint256(
        //     keccak256(
        //         abi.encodePacked(
        //             nonce,
        //             msg.sender,
        //             block.difficulty,
        //             block.timestamp
        //         )
        //     )
        // ) % players.length;
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyhash, fee);
        emit RequestedRandomness(requestId);
        // This function will call a chainlink node, which in turn calls fulfillrandomness function
    }

    // for the following function, internal keyword is used because it will be called only within the contract ie. the VRFCoordinator
    // the override keyword is used because it overrides the functionality of the function in VRFConsumerBase.sol with the same name. so it basically overrides the original declaration.
    function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "You have to start calculating the winner for this!"
        );
        require(_randomness > 0, "random not found :( ");
        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        recentWinner.transfer(address(this).balance);

        //reset
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }
}
