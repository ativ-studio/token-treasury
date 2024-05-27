from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class InitializeTreasuryAccounts(typing.TypedDict):
    treasury: Pubkey
    treasury_ata: Pubkey
    mint: Pubkey
    payer: Pubkey
    authority: Pubkey


def initialize_treasury(
    accounts: InitializeTreasuryAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["treasury"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["treasury_ata"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["mint"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["payer"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["authority"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=ASSOCIATED_TOKEN_PROGRAM_ID, is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"|\xba\xd3\xc3U\xa5\x81\xa6"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
