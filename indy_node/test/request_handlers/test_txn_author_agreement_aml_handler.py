import pytest as pytest

from common.serializers.serialization import domain_state_serializer
from indy_node.server.request_handlers.config_req_handlers.txn_author_agreement_aml_handler import \
    TxnAuthorAgreementAmlHandler
from indy_node.test.request_handlers.helper import get_exception, add_to_idr
from plenum.common.constants import ROLE, STEWARD, NYM, TARGET_NYM, TXN_TYPE, TXN_AUTHOR_AGREEMENT, \
    TXN_AUTHOR_AGREEMENT_TEXT, TXN_AUTHOR_AGREEMENT_VERSION, TRUSTEE, DOMAIN_LEDGER_ID, TXN_AUTHOR_AGREEMENT_AML, \
    AML_VERSION, AML, AML_CONTEXT
from plenum.common.exceptions import UnauthorizedClientRequest, InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_payload_data, reqToTxn, get_reply_nym
from plenum.common.util import randomString
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.utils import get_nym_details, get_role, is_steward, nym_to_state_key
from plenum.test.testing_utils import FakeSomething
from state.pruning_state import PruningState
from state.state import State
from indy_common.test.auth.conftest import write_auth_req_validator, constraint_serializer, config_state
from storage.kv_in_memory import KeyValueStorageInMemory


@pytest.fixture(scope="module")
def txn_author_agreement_aml_handler(db_manager, write_auth_req_validator):
    handler = TxnAuthorAgreementAmlHandler(db_manager, FakeSomething(), write_auth_req_validator)
    state = PruningState(KeyValueStorageInMemory())
    db_manager.register_new_database(handler.ledger_id, FakeSomething(), state)
    return handler


@pytest.fixture(scope="module")
def aml_request(txn_author_agreement_aml_handler, creator):
    return Request(identifier=creator,
                   signature="signature",
                   operation={TXN_TYPE: TXN_AUTHOR_AGREEMENT_AML,
                              AML_VERSION: "AML_VERSION",
                              AML: {"test": "test"},
                              AML_CONTEXT: "AML_CONTEXT"})


def test_dynamic_validation_without_permission(aml_request,
                                               txn_author_agreement_aml_handler: TxnAuthorAgreementAmlHandler,
                                               creator):
    add_to_idr(txn_author_agreement_aml_handler.database_manager.idr_cache, creator, STEWARD)
    with pytest.raises(UnauthorizedClientRequest, match="Not enough TRUSTEE signatures"):
        txn_author_agreement_aml_handler.dynamic_validation(aml_request)


def test_dynamic_validation(aml_request,
                            txn_author_agreement_aml_handler: TxnAuthorAgreementAmlHandler,
                            creator):
    add_to_idr(txn_author_agreement_aml_handler.database_manager.idr_cache, creator, TRUSTEE)
    txn_author_agreement_aml_handler.dynamic_validation(aml_request)
