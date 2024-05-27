#os 는 쉘로 tx 전송 테스트 한다고 사용한거라 임포트 안시켜도 됨
import os

import json
import base64
from solana.transaction import Transaction
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from spl.token.instructions import get_associated_token_address
# token_treasury_client 디렉토리를 전부 가지고 와야함 -> 토큰 트레져리 프로그램에 대한 정의
from token_treasury_client.instructions.transfer_token import TransferTokenArgs, TransferTokenAccounts, transfer_token
from solana.rpc.api import Client




# 트랜잭션 수수료 지불자 정보 불러오고 지불자 인스턴스 생성 코드
# env 안쓰고 json 사용한거라 env 사용하려면 os.environ.get("KEY") 이런식으로 사용하면 됨
# [123,245 ... 244, 233] 이런식으로 저장되는 솔라나 비밀키 정보를 바이트 배열로 변환해서 키페어 인스턴스 생성하는 코드
payer_kp=None
with open("/Users/deok/.config/solana/id.json", "r") as payer_json:
    payer_info = json.load(payer_json)
payer_info = bytearray(payer_info)
payerKp = Keypair.from_bytes(payer_info)


# 솔라나 네트워크에서 필요한 정보 불러오는 코드로 이거도 환경변수로 바꿔서 사용하면 됨
# 엔드포인트, 트레저리, 트레저리 ATA, 민트, authority 정보를 불러옴
# authority 같은 경우에 비밀키 정보도 불러오는데 authority 비밀키는 base58 인코딩된 문자열로 공유해줄거고 그걸 넣으면 됨
solana_info = None
with open("solana.json", "r") as solana_json:
    solana_info = json.load(solana_json)

authorityKp = Keypair.from_base58_string(solana_info.get("authoritySK"))
treasury = Pubkey.from_string(solana_info.get("treasury"))
treasury_ata = Pubkey.from_string(solana_info.get("treasuryAta"))
mint = Pubkey.from_string(solana_info.get("mint"))
authority = Pubkey.from_string(solana_info.get("authority"))

# user 는 프론트에서 받아오는 정보로 아래 코드는 테스트용으로 랜덤으로 생성한거라 프론트에서 받아오는 코드로 바꿔야함
# 주석처리된 코드를 사용하면 됨
# user_ata는 그대로 두면 됨
user = Pubkey.new_unique()
# user = Pubkey.from_string(input)
user_ata = get_associated_token_address(user, mint)

# 최신블록해시 받아와야 해서 솔라나 클라이언트 인스턴스 생성함
http_client = Client(solana_info.get("endpoint"))

# 인스터럭션 빌더는 사전 정의된 코드에서 불러오면 되고 여기 amount 값을 줘야 하는 값으로 바꿔주면 됨
# 봉크는 데시멀이 5 이니까 이부분 고려해서 0.01을 줘야 하면 1000 을 amount 값으로 줘야함
ix = transfer_token(
    TransferTokenArgs(amount=1000000),
    TransferTokenAccounts(
                treasury=treasury,
                treasury_ata=treasury_ata,
                mint=mint,
                user=user,
                user_ata=user_ata,
                payer=payerKp.pubkey(),
                authority=authority,
    )   
)


# 아래 코드는 트랜잭션 생성하고 서명해서 시리얼라이즈까지 하는 코드
tx = Transaction().add(ix)
tx.recent_blockhash = http_client.get_latest_blockhash().value.blockhash
tx.sign(payerKp,authorityKp)
serialized_tx = tx.serialize()
encoded_tx = base64.b64encode(serialized_tx)

# 트랜잭션을 json 파일로 저장하는 코드는 테스트로 임의로 만든거고 
# 실제로는 encoded_tx.decode("utf-8") 값을 프론트에 내려줘야 함
tx_json = {
    "tx": encoded_tx.decode("utf-8")
}
with open("tx.json", "w") as tx_file:
    json.dump(tx_json, tx_file)

os.system("yarn ts-node send.ts")