import pytest


@pytest.fixture
def deploy_contract(deploy_client, contracts):
    from populus.deployment import (
        deploy_contracts,
    )

    def _deploy_contract(ContractClass, constructor_args=None, from_address=None):
        if constructor_args is not None:
            constructor_args = {
                ContractClass.__name__: constructor_args,
            }
        deployed_contracts = deploy_contracts(
            deploy_client=deploy_client,
            contracts=contracts,
            contracts_to_deploy=[ContractClass.__name__],
            constructor_args=constructor_args,
            from_address=None,
        )

        contract = getattr(deployed_contracts, ContractClass.__name__)
        assert deploy_client.get_code(contract._meta.address)
        return contract
    return _deploy_contract


@pytest.fixture
def get_log_data(deploy_client, contracts):
    def _get_log_data(event, txn_hash, indexed=True):
        event_logs = event.get_transaction_logs(txn_hash)
        assert len(event_logs)

        if len(event_logs) == 1:
            event_data = event.get_log_data(event_logs[0], indexed=indexed)
        else:
            event_data = tuple(
                event.get_log_data(l, indexed=indexed) for l in event_logs
            )
        return event_data
    return _get_log_data


@pytest.fixture
def wallet(deploy_contract, contracts, accounts):
    owner_b = accounts[1]
    owner_c = accounts[2]
    wallet = deploy_contract(contracts.ColdWallet, (owner_b, owner_c))

    return wallet
