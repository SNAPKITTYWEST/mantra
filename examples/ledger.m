# ledger.m — MANTRA example: transaction seal

@deterministic
define seal(tx)
begin
    let id_bytes   = integer_to_bytes(tx.id, 8)
    let acct_bytes = integer_to_bytes(tx.account, 8)
    let amt_bytes  = integer_to_bytes(tx.amount, 16)
    let prev       = hex_to_bytes(tx.previous_hash)
    let payload    = concat(id_bytes, concat(acct_bytes, concat(amt_bytes, prev)))
    return sha256_hex(payload)
end

const tx = {
    id: 12345,
    account: 98765,
    amount: 125000,
    currency: "USD",
    timestamp: 1690000000,
    previous_hash: "0000000000000000000000000000000000000000000000000000000000000000"
}

const seal_hex = seal(tx)
