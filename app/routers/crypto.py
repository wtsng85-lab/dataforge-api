"""Cryptocurrency wallet address validation endpoints."""

from fastapi import APIRouter, Query

from app.models import CryptoValidateRequest, CryptoValidateResponse
from app.validators.crypto import validate_crypto_address, SUPPORTED_CHAINS

router = APIRouter(prefix="/crypto", tags=["Crypto"])


@router.get("/validate", summary="Validate a crypto wallet address", response_model=CryptoValidateResponse)
async def crypto_validate(
    address: str = Query(..., description="Wallet address to validate", examples=["1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"], max_length=128),
    chain: str | None = Query(None, description="Blockchain (btc, eth). Auto-detected if omitted.", max_length=10),
):
    """Validate a cryptocurrency wallet address. Supports Bitcoin (legacy, segwit, taproot) and Ethereum."""
    return validate_crypto_address(address.strip(), chain)


@router.post("/validate", summary="Validate a crypto wallet address (POST)", response_model=CryptoValidateResponse)
async def crypto_validate_post(req: CryptoValidateRequest):
    """Validate a crypto wallet address via POST body."""
    return validate_crypto_address(req.address.strip(), req.chain)


@router.get("/chains", summary="List supported blockchains")
async def crypto_chains():
    """List all supported blockchains for address validation."""
    unique = {}
    for key, (name, _) in SUPPORTED_CHAINS.items():
        if name not in unique:
            unique[name] = key
    return {
        "total": len(unique),
        "chains": {name: {"alias": alias} for name, alias in unique.items()},
    }
