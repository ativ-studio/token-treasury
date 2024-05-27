import * as fs from "fs";
import {
  Connection,
  sendAndConfirmRawTransaction,
  BlockheightBasedTransactionConfirmationStrategy
} from "@solana/web3.js";

const sendTx = async () => {
  try {
    const solanaFile = fs.readFileSync("./solana.json", "utf-8");
    const txFile = fs.readFileSync("./tx.json", "utf-8");

    const txData = JSON.parse(txFile);
    const solanaData = JSON.parse(solanaFile);

    const connection = new Connection(solanaData.endpoint, "confirmed");

    const signature = await connection.sendRawTransaction(
      Buffer.from(txData.tx, "base64"),
      {
        skipPreflight: true
      }
    );

    const latestBlockHash = await connection.getLatestBlockhash();
    const confirmStrategy: BlockheightBasedTransactionConfirmationStrategy = {
      blockhash: latestBlockHash.blockhash,
      lastValidBlockHeight: latestBlockHash.lastValidBlockHeight,
      signature: signature
    };
    const result = await connection.confirmTransaction(
      confirmStrategy,
      "confirmed"
    );

    console.log(signature, result);
  } catch (err) {
    console.log(err);
    return;
  }
};

sendTx();
