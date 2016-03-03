contract ColdWallet {
    /*
     *  Wallet designed for multi-signature cold storage.
     *
     *  2 of 3 multisignature.
     *  can withdraw funds or suicide contract with 2 of 3
     */
    address public owner_a;
    address public owner_b;
    address public owner_c;

    modifier onlyowner {if (msg.sender != owner_a && msg.sender != owner_b && msg.sender != owner_c) throw; _ }

    function ColdWallet(address _owner_b, address _owner_c) {
        owner_a = msg.sender;
        owner_b = _owner_b;
        owner_c = _owner_c;
    }

    function() {
        // Allow deposits by just sending to contract address.
    }

    function deposit() public onlyowner {
    }

    uint constant EXPIRE_DELTA = 6 hours;

    struct Withdrawal {
        uint id;
        mapping (address => bool) approvals;
        uint value;
        address createdBy;
        uint createdAt;
        uint expiresAt;
        bool executed;
    }

    mapping (uint => Withdrawal) withdrawals;

    function getWithdrawal(uint _id)
        constant
        public
        onlyowner
        returns (uint id,
                 bool[3] approvals,
                 uint value,
                 address createdBy,
                 uint createdAt,
                 uint expiresAt,
                 bool executed)
    {
        if (_id == 0 || _id > lastId) throw;

        var withdrawal = withdrawals[_id];

        id = withdrawal.id;
        approvals[0] = withdrawal.approvals[owner_a];
        approvals[1] = withdrawal.approvals[owner_b];
        approvals[2] = withdrawal.approvals[owner_c];
        value = withdrawal.value;
        createdBy = withdrawal.createdBy;
        createdAt = withdrawal.createdAt;
        expiresAt = withdrawal.expiresAt;
        executed = withdrawal.executed;

        return (id, approvals, value, createdBy, createdAt, expiresAt, executed);
    }

    uint public lastId;

    event Request(uint indexed id);

    function request(uint value) public onlyowner {
        if (value > this.balance) throw;

        lastId += 1;
        var withdrawal = withdrawals[lastId];
        withdrawal.id = lastId;
        withdrawal.approvals[msg.sender] = true;
        withdrawal.value = value;
        withdrawal.createdBy = msg.sender;
        withdrawal.createdAt = now;
        withdrawal.expiresAt = now + EXPIRE_DELTA;

        Request(withdrawal.id);
    }

    event Approved(uint indexed id, address who);

    function approve(uint id) public onlyowner {
        if (id == 0 || id > lastId) throw;

        var withdrawal = withdrawals[id];

        if (withdrawal.approvals[msg.sender]) throw;
        if (withdrawal.executed) throw;
        if (withdrawal.expiresAt <= now) throw;

        withdrawal.approvals[msg.sender] = true;

        Approved(id, msg.sender);
    }

    event Execution(uint indexed id, address who);

    function execute(uint id) public onlyowner {
        if (id == 0 || id > lastId) throw;

        var withdrawal = withdrawals[id];

        if (withdrawal.executed) throw;
        if (withdrawal.expiresAt <= now) throw;

        uint numApprovals;

        if (withdrawal.approvals[owner_a]) numApprovals += 1;
        if (withdrawal.approvals[owner_b]) numApprovals += 1;
        if (withdrawal.approvals[owner_c]) numApprovals += 1;

        if (numApprovals < 2) throw;

        withdrawal.executed = true;
        if (!withdrawal.createdBy.call.value(withdrawal.value)()) {
            throw;
        }

        Execution(id, msg.sender);
    }

    mapping (address => bool) public killOrders;

    function rescind() public onlyowner {
        killOrders[msg.sender] = false;
    }

    function kill() public onlyowner {
        killOrders[msg.sender] = true;

        uint num_orders;

        if (killOrders[owner_a]) num_orders += 1;
        if (killOrders[owner_b]) num_orders += 1;
        if (killOrders[owner_c]) num_orders += 1;

        if (num_orders >= 2) {
            selfdestruct(msg.sender);
        }
    }
}
