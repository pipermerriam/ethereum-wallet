def test_deposit_function(wallet, accounts):
    assert wallet.get_balance() == 0

    wallet.deposit.s(value=1, _from=accounts[0])

    assert wallet.get_balance() == 1

    wallet.deposit.s(value=2, _from=accounts[1])

    assert wallet.get_balance() == 3

    wallet.deposit.s(value=3, _from=accounts[2])

    assert wallet.get_balance() == 6


def test_fallback_function(wallet, accounts, deploy_client):
    assert wallet.get_balance() == 0

    deploy_client.send_transaction(to=wallet._meta.address, value=1, _from=accounts[0])

    assert wallet.get_balance() == 1

    deploy_client.send_transaction(to=wallet._meta.address, value=2, _from=accounts[1])

    assert wallet.get_balance() == 3

    deploy_client.send_transaction(to=wallet._meta.address, value=3, _from=accounts[2])

    assert wallet.get_balance() == 6
