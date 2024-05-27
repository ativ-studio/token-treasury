from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class TransferTokenArgs(typing.TypedDict):
    amount: int


layout = borsh.CStruct("amount" / borsh.U64)


class TransferTokenAccounts(typing.TypedDict):
    treasury: Pubkey
    treasury_ata: Pubkey
    mint: Pubkey
    user: Pubkey
    user_ata: Pubkey
    payer: Pubkey
    authority: Pubkey


def transfer_token(
    args: TransferTokenArgs,
    accounts: TransferTokenAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["treasury"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["treasury_ata"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["mint"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["user"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["user_ata"], is_signer=False, is_writable=True),
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
    identifier = b"\xdb\x11z5\xed\xab\xe8\xde"
    encoded_args = layout.build(
        {
            "amount": args["amount"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
