import typing
from anchorpy.error import ProgramError


class IncorrectOwnerProgram(ProgramError):
    def __init__(self) -> None:
        super().__init__(6000, "Account does not have correct owner Program")

    code = 6000
    name = "IncorrectOwnerProgram"
    msg = "Account does not have correct owner Program"


class UninitializedAccount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6001, "Account is not initialized")

    code = 6001
    name = "UninitializedAccount"
    msg = "Account is not initialized"


class InitializedAccount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6002, "Account is already initialized")

    code = 6002
    name = "InitializedAccount"
    msg = "Account is already initialized"


class InvalidAuthority(ProgramError):
    def __init__(self) -> None:
        super().__init__(6003, "Auth account is not valid")

    code = 6003
    name = "InvalidAuthority"
    msg = "Auth account is not valid"


class MissingRequiredSignature(ProgramError):
    def __init__(self) -> None:
        super().__init__(6004, "Auth is not signer")

    code = 6004
    name = "MissingRequiredSignature"
    msg = "Auth is not signer"


CustomError = typing.Union[
    IncorrectOwnerProgram,
    UninitializedAccount,
    InitializedAccount,
    InvalidAuthority,
    MissingRequiredSignature,
]
CUSTOM_ERROR_MAP: dict[int, CustomError] = {
    6000: IncorrectOwnerProgram(),
    6001: UninitializedAccount(),
    6002: InitializedAccount(),
    6003: InvalidAuthority(),
    6004: MissingRequiredSignature(),
}


def from_code(code: int) -> typing.Optional[CustomError]:
    maybe_err = CUSTOM_ERROR_MAP.get(code)
    if maybe_err is None:
        return None
    return maybe_err
