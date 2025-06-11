// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title EVCharging
 * @dev Smart contract for managing electric vehicle charging sessions
 */
contract EVCharging {
    // Events
    event SessionStarted(uint256 indexed sessionId, address indexed user, uint256 stationId, uint256 startTime);
    event SessionEnded(uint256 indexed sessionId, uint256 endTime, uint256 duration);
    event PaymentProcessed(uint256 indexed sessionId, uint256 amount, address indexed user);
    event StationReserved(uint256 indexed stationId, address indexed user, uint256 startTime, uint256 endTime);

    // Structures
    struct Session {
        address user;
        uint256 stationId;
        uint256 startTime;
        uint256 endTime;
        bool active;
        bool paid;
        uint256 amount;
    }

    struct Reservation {
        address user;
        uint256 startTime;
        uint256 endTime;
        bool active;
    }

    // State variables
    mapping(uint256 => Session) public sessions;
    mapping(uint256 => Reservation[]) public stationReservations; // stationId => array of reservations
    uint256 public sessionCount;
    address public owner;
    uint256 public constant MINIMUM_CHARGE_DURATION = 15 minutes;
    uint256 public constant MAXIMUM_CHARGE_DURATION = 24 hours;

    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    modifier validStation(uint256 stationId) {
        require(stationId > 0, "Invalid station ID");
        _;
    }

    modifier validSession(uint256 sessionId) {
        require(sessionId > 0 && sessionId <= sessionCount, "Invalid session ID");
        _;
    }

    // Constructor
    constructor() {
        owner = msg.sender;
    }

    /**
     * @dev Reserves a charging station
     * @param stationId The ID of the station to be reserved
     * @param startTime The start time of the reservation
     * @param endTime The end time of the reservation
     */
    function reserveStation(
        uint256 stationId,
        uint256 startTime,
        uint256 endTime
    ) external validStation(stationId) {
        require(startTime > block.timestamp, "Start time must be in the future");
        require(endTime > startTime, "End time must be after start time");
        require(endTime - startTime >= MINIMUM_CHARGE_DURATION, "Reservation too short");
        require(endTime - startTime <= MAXIMUM_CHARGE_DURATION, "Reservation too long");

        // Check if station is available for the requested time
        for (uint256 i = 0; i < stationReservations[stationId].length; i++) {
            if (stationReservations[stationId][i].active) {
                require(
                    endTime <= stationReservations[stationId][i].startTime || startTime >= stationReservations[stationId][i].endTime,
                    "Time slot already reserved"
                );
            }
        }

        // Create reservation
        stationReservations[stationId].push(Reservation({
            user: msg.sender,
            startTime: startTime,
            endTime: endTime,
            active: true
        }));

        emit StationReserved(stationId, msg.sender, startTime, endTime);
    }

    /**
     * @dev Starts a charging session
     * @param stationId The ID of the station to be used
     */
    function startSession(uint256 stationId) external validStation(stationId) {
        bool hasReservation = false;
        
        // Check if station is reserved for current time
        for (uint256 i = 0; i < stationReservations[stationId].length; i++) {
            Reservation storage reservation = stationReservations[stationId][i];
            if (reservation.active && 
                reservation.user == msg.sender && 
                block.timestamp >= reservation.startTime && 
                block.timestamp <= reservation.endTime) {
                hasReservation = true;
                break;
            }
        }
        
        require(hasReservation, "No active reservation found");

        sessionCount++;
        sessions[sessionCount] = Session({
            user: msg.sender,
            stationId: stationId,
            startTime: block.timestamp,
            endTime: 0,
            active: true,
            paid: false,
            amount: 0
        });

        emit SessionStarted(sessionCount, msg.sender, stationId, block.timestamp);
    }

    /**
     * @dev Ends a charging session
     * @param sessionId The ID of the session to be ended
     */
    function endSession(uint256 sessionId) external validSession(sessionId) {
        Session storage session = sessions[sessionId];
        require(session.active, "Session already ended");
        require(session.user == msg.sender, "Not the session owner");

        session.active = false;
        session.endTime = block.timestamp;

        emit SessionEnded(
            sessionId,
            block.timestamp,
            block.timestamp - session.startTime
        );
    }

    /**
     * @dev Processes payment for a session
     * @param sessionId The ID of the session to be paid
     */
    function paySession(uint256 sessionId) external payable validSession(sessionId) {
        Session storage session = sessions[sessionId];
        require(!session.active, "Session still active");
        require(!session.paid, "Session already paid");
        require(session.user == msg.sender, "Not the session owner");

        // Calculate payment based on duration (example: 0.001 ETH per hour)
        uint256 duration = session.endTime - session.startTime;
        uint256 amount = (duration * 0.001 ether) / 1 hours;
        require(msg.value >= amount, "Insufficient payment");

        session.paid = true;
        session.amount = amount;

        // Refund excess payment
        if (msg.value > amount) {
            payable(msg.sender).transfer(msg.value - amount);
        }

        emit PaymentProcessed(sessionId, amount, msg.sender);
    }

    /**
     * @dev Gets session details
     * @param sessionId The ID of the session to be queried
     * @return user The address of the session user
     * @return stationId The ID of the station used
     * @return startTime The start time of the session
     * @return endTime The end time of the session
     * @return active Whether the session is active
     * @return paid Whether the session has been paid
     * @return amount The amount paid for the session
     */
    function getSession(uint256 sessionId)
        external
        view
        validSession(sessionId)
        returns (
            address user,
            uint256 stationId,
            uint256 startTime,
            uint256 endTime,
            bool active,
            bool paid,
            uint256 amount
        )
    {
        Session storage session = sessions[sessionId];
        return (
            session.user,
            session.stationId,
            session.startTime,
            session.endTime,
            session.active,
            session.paid,
            session.amount
        );
    }

    /**
     * @dev Withdraws contract balance (only owner)
     */
    function withdraw() external onlyOwner {
        payable(owner).transfer(address(this).balance);
    }
} 