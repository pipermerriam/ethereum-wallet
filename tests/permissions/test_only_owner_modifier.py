import pytest

from ethereum.tester import TransactionFailed


def test_sets_owners(deploy_contract, contracts, accounts):
    owner_b = accounts[1]
    owner_c = accounts[2]
    wallet = deploy_contract(contracts.ColdWallet, (owner_b, owner_c))

    assert wallet.owner_a() == accounts[0]
    assert wallet.owner_b() == owner_b
    assert wallet.owner_c() == owner_c


def test_deposit_restricted_to_owner(wallet, accounts, deploy_client):
    assert deploy_client.get_balance(accounts[0]) > 0
    assert deploy_client.get_balance(accounts[1]) > 0
    assert deploy_client.get_balance(accounts[2]) > 0
    assert deploy_client.get_balance(accounts[3]) > 0

    wallet.deposit.s(value=1, _from=accounts[0])
    wallet.deposit.s(value=1, _from=accounts[1])
    wallet.deposit.s(value=1, _from=accounts[2])

    with pytest.raises(TransactionFailed):
        wallet.deposit.s(value=1, _from=accounts[3])


def test_request_restricted_to_owner(wallet, accounts, deploy_client, get_log_data):
    deploy_client.send_transaction(value=10, to=wallet._meta.address)

    txn_h, txn_r = wallet.request.s(5)

    logs = get_log_data(wallet.Request, txn_h)

    assert logs

    with pytest.raises(TransactionFailed):
        wallet.request.s(5, value=1, _from=accounts[3])


def test_approve_restricted_to_owner(wallet, accounts, deploy_client, get_log_data):
    deploy_client.send_transaction(value=10, to=wallet._meta.address)

    req_txn_h, req_txn_r = wallet.request.s(5)

    request_id = get_log_data(wallet.Request, req_txn_h)['id']

    with pytest.raises(TransactionFailed):
        wallet.approve(request_id, _from=accounts[3])

    approve_txn_h, approve_txn_r = wallet.approve.s(request_id, _from=accounts[1])

    entry = get_log_data(wallet.Approved, approve_txn_h)

    assert entry['id'] == request_id
    assert entry['who'] == accounts[1]


def test_execution_restricted_to_owner(wallet, accounts, deploy_client, get_log_data):
    deploy_client.send_transaction(value=10, to=wallet._meta.address)

    req_txn_h, req_txn_r = wallet.request.s(5)

    request_id = get_log_data(wallet.Request, req_txn_h)['id']

    wallet.approve.s(request_id, _from=accounts[1])

    with pytest.raises(TransactionFailed):
        wallet.execute(request_id, _from=accounts[3])

    assert wallet.get_balance() == 10

    execute_txn_h, execute_txn_r = wallet.execute.s(request_id, _from=accounts[1])

    assert wallet.get_balance() == 5

    entry = get_log_data(wallet.Execution, execute_txn_h)

    assert entry['id'] == request_id
    assert entry['who'] == accounts[1]


def test_rescind_restricted_to_owner(wallet, accounts):
    wallet.rescind.s()

    with pytest.raises(TransactionFailed):
        wallet.rescind.s(_from=accounts[3])


def test_kill_restricted_to_owner(wallet, accounts):
    wallet.kill.s()

    with pytest.raises(TransactionFailed):
        wallet.kill.s(_from=accounts[3])
