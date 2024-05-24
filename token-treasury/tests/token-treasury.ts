import {
  Keypair,
  PublicKey,
  SYSVAR_RENT_PUBKEY,
  SystemProgram
} from "@solana/web3.js";
import {
  TOKEN_PROGRAM_ID,
  ASSOCIATED_PROGRAM_ID
} from "@coral-xyz/anchor/dist/cjs/utils/token";
import {
  createInitializeMintInstruction,
  createMintToCheckedInstruction,
  MINT_SIZE
} from "@solana/spl-token";
import BN from "bn.js";
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { TokenTreasury } from "../target/types/token_treasury";
import { associatedAddress } from "@coral-xyz/anchor/dist/cjs/utils/token";

describe("token-treasury", () => {
  // Configure the client to use the local cluster.
  anchor.setProvider(anchor.AnchorProvider.env());

  const program = anchor.workspace.TokenTreasury as Program<TokenTreasury>;

  function getTreasuryAddress(
    mint: PublicKey,
    authority: PublicKey
  ): [PublicKey, number] {
    return PublicKey.findProgramAddressSync(
      [
        anchor.utils.bytes.utf8.encode("treasury"),
        mint.toBuffer(),
        authority.toBuffer()
      ],
      program.programId
    );
  }
  const mintKp = new Keypair();
  const authoriyKp = new Keypair();
  const mint = mintKp.publicKey;
  const authority = authoriyKp.publicKey;
  const payer = program.provider.publicKey;

  it("Initialize Treasury", async () => {
    const [treasury, bump] = getTreasuryAddress(mint, authority);
    const treasuryAta = associatedAddress({ mint: mint, owner: treasury });
    const mintLamport =
      await program.provider.connection.getMinimumBalanceForRentExemption(
        MINT_SIZE
      );
    const createMintTx = SystemProgram.createAccount({
      fromPubkey: payer,
      lamports: mintLamport,
      newAccountPubkey: mint,
      programId: TOKEN_PROGRAM_ID,
      space: MINT_SIZE
    });
    const initializeMintTx = createInitializeMintInstruction(
      mint,
      5,
      payer,
      payer
    );
    const mintTx = createMintToCheckedInstruction(
      mint,
      treasuryAta,
      payer,
      1000000000,
      5
    );
    const tx = await program.methods
      .initializeTreasury()
      .accounts({
        treasury,
        treasuryAta,
        mint,
        payer,
        authority,
        rent: SYSVAR_RENT_PUBKEY,
        systemProgram: SystemProgram.programId,
        tokenProgram: TOKEN_PROGRAM_ID,
        associatedProgram: ASSOCIATED_PROGRAM_ID
      })
      .preInstructions([createMintTx, initializeMintTx])
      .postInstructions([mintTx])
      .signers([authoriyKp, mintKp])
      .rpc({ skipPreflight: true });

    console.log("Your transaction signature", tx);
  });

  it("Transfer Token", async () => {
    const [treasury, bump] = getTreasuryAddress(mint, authority);
    const treasuryAta = associatedAddress({ mint: mint, owner: treasury });

    const user = PublicKey.unique();
    const userAta = associatedAddress({ mint: mint, owner: user });

    const tx = await program.methods
      .transferToken(new BN(1000000))
      .accounts({
        treasury,
        treasuryAta,
        mint,
        user,
        userAta,
        payer,
        authority,
        rent: SYSVAR_RENT_PUBKEY,
        systemProgram: SystemProgram.programId,
        tokenProgram: TOKEN_PROGRAM_ID,
        associatedProgram: ASSOCIATED_PROGRAM_ID
      })
      .signers([authoriyKp])
      .rpc({ skipPreflight: true });

    console.log("Your transaction signature", tx);
  });
});
