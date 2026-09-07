# treasury.m — multi-step ledger chain

@deterministic
define hash_record(id, account, amount, prev_hex)
begin
    let id_b   = integer_to_bytes(id, 8)
    let acc_b  = integer_to_bytes(account, 8)
    let amt_b  = integer_to_bytes(amount, 16)
    let prev_b = hex_to_bytes(prev_hex)
    let msg    = concat(id_b, concat(acc_b, concat(amt_b, prev_b)))
    return sha256_hex(msg)
end

const GENESIS = "0000000000000000000000000000000000000000000000000000000000000000"

const h1 = hash_record(1, 1001, 50000, GENESIS)
const h2 = hash_record(2, 1002, 75000, h1)
const h3 = hash_record(3, 1001, 20000, h2)
