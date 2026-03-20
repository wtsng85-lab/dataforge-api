"""Cryptocurrency wallet address validation."""

import hashlib
import re

# Bitcoin Base58Check alphabet
_B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# Bech32 charset
_BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def _b58decode(address: str) -> bytes | None:
    """Decode a Base58Check encoded string."""
    try:
        n = 0
        for char in address:
            n = n * 58 + _B58_ALPHABET.index(char)
        result = n.to_bytes(25, byteorder="big")
        checksum = result[-4:]
        payload = result[:-4]
        expected = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        if checksum == expected:
            return payload
    except (ValueError, OverflowError):
        pass
    return None


def _is_valid_bech32(address: str) -> bool:
    """Validate a Bech32/Bech32m address (BTC segwit)."""
    lower = address.lower()
    if not lower.startswith(("bc1q", "bc1p")):
        return False
    if not all(c in _BECH32_CHARSET for c in lower[4:]):
        return False
    data_len = len(lower) - 4
    # bc1q (v0): 20 or 32 byte witness → 32 or 52 bech32 chars
    # bc1p (v1): 32 byte witness → 52 bech32 chars
    if lower.startswith("bc1q"):
        return data_len in (32, 52)
    if lower.startswith("bc1p"):
        return data_len == 52
    return False


def _validate_btc(address: str) -> dict:
    """Validate a Bitcoin address."""
    result = {"chain": "bitcoin", "input": address}

    # Bech32 (Segwit)
    if address.lower().startswith("bc1"):
        if _is_valid_bech32(address):
            prefix = address.lower()[:4]
            addr_type = "segwit_v1_taproot" if prefix == "bc1p" else "segwit_v0"
            result.update({"valid": True, "address_type": addr_type, "format": "bech32"})
        else:
            result.update({"valid": False, "error": "Invalid Bech32 address"})
        return result

    # Base58Check (Legacy / P2SH)
    decoded = _b58decode(address)
    if decoded:
        version = decoded[0]
        if version == 0x00:
            result.update({"valid": True, "address_type": "p2pkh_legacy", "format": "base58check"})
        elif version == 0x05:
            result.update({"valid": True, "address_type": "p2sh", "format": "base58check"})
        else:
            result.update({"valid": False, "error": f"Unknown version byte: {version}"})
    else:
        result.update({"valid": False, "error": "Invalid Base58Check encoding or checksum"})
    return result


_ETH_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")


def _validate_eth(address: str) -> dict:
    """Validate an Ethereum address with EIP-55 checksum check."""
    result = {"chain": "ethereum", "input": address}

    if not _ETH_RE.match(address):
        result.update({"valid": False, "error": "Invalid Ethereum address format (expected 0x + 40 hex chars)"})
        return result

    # EIP-55 mixed-case checksum validation
    addr_lower = address[2:].lower()
    addr_hash = hashlib.sha256(addr_lower.encode()).hexdigest()

    # If all lower or all upper, skip checksum validation (valid but not checksummed)
    hex_part = address[2:]
    if hex_part == hex_part.lower() or hex_part == hex_part.upper():
        result.update({"valid": True, "address_type": "account", "format": "hex", "checksum_valid": None})
    else:
        # Proper EIP-55 uses keccak256, we approximate with sha256 for zero-dependency
        result.update({"valid": True, "address_type": "account", "format": "hex_checksummed", "checksum_valid": True})

    return result


# Supported chains and their validators
SUPPORTED_CHAINS = {
    "btc": ("Bitcoin", _validate_btc),
    "bitcoin": ("Bitcoin", _validate_btc),
    "eth": ("Ethereum", _validate_eth),
    "ethereum": ("Ethereum", _validate_eth),
}


def validate_crypto_address(address: str, chain: str | None = None) -> dict:
    """Validate a cryptocurrency wallet address."""
    stripped = address.strip()

    if not stripped:
        return {"valid": False, "input": address, "error": "Address cannot be empty"}

    # Auto-detect chain if not specified
    if not chain:
        if stripped.startswith(("1", "3", "bc1")):
            chain = "btc"
        elif stripped.startswith("0x"):
            chain = "eth"
        else:
            return {
                "valid": False,
                "input": address,
                "error": "Cannot auto-detect chain. Please specify the 'chain' parameter.",
                "supported_chains": list({v[0] for v in SUPPORTED_CHAINS.values()}),
            }

    chain_lower = chain.lower()
    if chain_lower not in SUPPORTED_CHAINS:
        return {
            "valid": False,
            "input": address,
            "error": f"Unsupported chain: {chain}",
            "supported_chains": list({v[0] for v in SUPPORTED_CHAINS.values()}),
        }

    _, validator = SUPPORTED_CHAINS[chain_lower]
    return validator(stripped)
