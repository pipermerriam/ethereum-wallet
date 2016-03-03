def test_multisignature_kill(wallet, accounts, deploy_client):
    wallet.kill.s(_from=accounts[0])

    assert len(deploy_client.get_code(wallet._meta.address)) > 2

    wallet.kill.s(_from=accounts[1])

    assert len(deploy_client.get_code(wallet._meta.address)) <= 2


def test_rescinding(wallet, accounts, deploy_client):
    wallet.kill.s(_from=accounts[0])
    wallet.rescind.s(_from=accounts[0])

    assert len(deploy_client.get_code(wallet._meta.address)) > 2

    wallet.kill.s(_from=accounts[1])

    assert len(deploy_client.get_code(wallet._meta.address)) > 2

    wallet.kill.s(_from=accounts[2])

    assert len(deploy_client.get_code(wallet._meta.address)) <= 2
