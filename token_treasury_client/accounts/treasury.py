import typing
from dataclasses import dataclass
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
import borsh_construct as borsh
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from anchorpy.borsh_extension import BorshPubkey
from ..program_id import PROGRAM_ID


class TreasuryJSON(typing.TypedDict):
    mint: str
    authority: str
    bump: int


@dataclass
class Treasury:
    discriminator: typing.ClassVar = b"\xee\xef{\xeeY\x01\xa8\xfd"
    layout: typing.ClassVar = borsh.CStruct(
        "mint" / BorshPubkey, "authority" / BorshPubkey, "bump" / borsh.U8
    )
    mint: Pubkey
    authority: Pubkey
    bump: int

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["Treasury"]:
        resp = await conn.get_account_info(address, commitment=commitment)
        info = resp.value
        if info is None:
            return None
        if info.owner != program_id:
            raise ValueError("Account does not belong to this program")
        bytes_data = info.data
        return cls.decode(bytes_data)

    @classmethod
    async def fetch_multiple(
        cls,
        conn: AsyncClient,
        addresses: list[Pubkey],
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.List[typing.Optional["Treasury"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["Treasury"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "Treasury":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = Treasury.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            mint=dec.mint,
            authority=dec.authority,
            bump=dec.bump,
        )

    def to_json(self) -> TreasuryJSON:
        return {
            "mint": str(self.mint),
            "authority": str(self.authority),
            "bump": self.bump,
        }

    @classmethod
    def from_json(cls, obj: TreasuryJSON) -> "Treasury":
        return cls(
            mint=Pubkey.from_string(obj["mint"]),
            authority=Pubkey.from_string(obj["authority"]),
            bump=obj["bump"],
        )
