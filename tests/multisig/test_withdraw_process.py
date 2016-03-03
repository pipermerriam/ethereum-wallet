import pytest

from ethereum.tester import TransactionFailed


def test_requesting(wallet, accounts, deploy_client, get_log_data):
    wallet.deposit.s(value=10)

    txn_h, txn_r = wallet.request.s(5)

    request_id = get_log_data(wallet.Request, txn_h)['id']
    assert request_id == 1


def test_getting_request_data(wallet, accounts, deploy_client, get_log_data):
    wallet.deposit.s(value=10)

    txn_h, txn_r = wallet.request.s(5)

    request_id = get_log_data(wallet.Request, txn_h)['id']

    block = deploy_client.get_block_by_number(txn_r['blockNumber'])

    request_data = wallet.getWithdrawal(request_id)

    assert request_data[0] == request_id
    assert request_data[1] == [True, False, False]
    assert request_data[2] == 5
    assert request_data[3] == accounts[0]
    assert request_data[4] == int(block['timestamp'], 16)
    assert request_data[5] == int(block['timestamp'], 16) + 6 * 60 * 60
    assert request_data[6] is False


def test_approving(wallet, accounts, deploy_client, get_log_data):
    wallet.deposit.s(value=10)

    txn_h, txn_r = wallet.request.s(5)

    request_id = get_log_data(wallet.Request, txn_h)['id']

    approve_txn_h, approve_txn_r = wallet.approve.s(request_id, _from=accounts[1])

    request_data = wallet.getWithdrawal(request_id)

    assert request_data[1] == [True, True, False]


def test_execution(wallet, accounts, deploy_client, get_log_data):
    wallet.deposit.s(value=10)

    txn_h, txn_r = wallet.request.s(5)

    request_id = get_log_data(wallet.Request, txn_h)['id']

    wallet.approve.s(request_id, _from=accounts[1])

    exec_txn_h, exec_txn_r = wallet.execute.s(request_id, _from=accounts[1])

    request_data = wallet.getWithdrawal(request_id)

    assert request_data[6] is True


def test_cannot_double_execute(wallet, accounts, deploy_client, get_log_data):
    wallet.deposit.s(value=10)

    txn_h, txn_r = wallet.request.s(5)

    request_id = get_log_data(wallet.Request, txn_h)['id']

    wallet.approve.s(request_id, _from=accounts[1])

    exec_txn_h, exec_txn_r = wallet.execute.s(request_id, _from=accounts[1])

    with pytest.raises(TransactionFailed):
        wallet.execute.s(request_id, _from=accounts[1])


def test_cannot_execute_without_2_of_3(wallet, accounts, deploy_client, get_log_data):
    wallet.deposit.s(value=10)

    txn_h, txn_r = wallet.request.s(5)

    request_id = get_log_data(wallet.Request, txn_h)['id']

    with pytest.raises(TransactionFailed):
        wallet.execute.s(request_id, _from=accounts[1])


def test_ether_sent_on_execution(wallet, accounts, deploy_client, get_log_data):
    balance_a = deploy_client.get_balance(accounts[1]) - 3141592
    balance_b = deploy_client.get_balance(accounts[2]) - 3141592

    assert balance_a > 1e21
    assert balance_a == balance_b

    wallet.deposit.s(value=balance_b, _from=accounts[2])

    txn_h, txn_r = wallet.request.s(balance_b, _from=accounts[1])

    deploy_client.send_transaction(to=accounts[2], _from=accounts[1], value=deploy_client.get_balance(accounts[1]) - 3141592)

    assert deploy_client.get_balance(accounts[1]) < 3141592

    request_id = get_log_data(wallet.Request, txn_h)['id']

    wallet.approve.s(request_id)
    wallet.execute.s(request_id)

    after_balance = deploy_client.get_balance(accounts[1])
    assert after_balance > 3141592
    assert after_balance > 1e21
    assert abs(after_balance - balance_a) < 3141592
