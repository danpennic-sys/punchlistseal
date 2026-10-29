#!/usr/bin/env python3
"""
PunchListSeal — local-first punch-list / deficiency logger and QuantumGuard sealer.
Compatible with QuantumGuard CONTRACT-v1 and the Operator Pages suite.
Offline after key setup. Deterministic payload hashing.
"""
import argparse
import json
import hashlib
import base64
from datetime import datetime, timezone
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Note: cryptography not installed. Using stub signatures. pip install cryptography for real Ed25519.")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load_or_create_key(key_path: Path):
    """Returns (private_key_or_None, public_key_hex)"""
    if not CRYPTO_AVAILABLE:
        return None, "00" * 32
    if key_path.exists():
        with open(key_path, "rb") as f:
            priv = serialization.load_pem_private_key(f.read(), password=None)
        pub = priv.public_key()
        pub_bytes = pub.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        return priv, pub_bytes.hex()
    else:
        priv = Ed25519PrivateKey.generate()
        pub = priv.public_key()
        pub_bytes = pub.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        pem = priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        key_path.write_bytes(pem)
        return priv, pub_bytes.hex()

def sign_payload(priv, payload_hash_hex: str) -> str:
    if not CRYPTO_AVAILABLE or priv is None:
        return "00" * 64
    hash_bytes = bytes.fromhex(payload_hash_hex)
    sig = priv.sign(hash_bytes)
    return sig.hex()

def build_evidence_pack(punch_list: dict, priv, pub_hex: str) -> dict:
    payload_obj = {
        "version": "1",
        "type": "punch_list",
        "list_id": punch_list.get("list_id", "unknown"),
        "job_id": punch_list.get("job_id", ""),
        "client": punch_list.get("client", ""),
        "location": punch_list.get("location", ""),
        "walkthrough_date": punch_list.get("walkthrough_date", ""),
        "items": punch_list.get("items", []),
        "open_count": sum(1 for i in punch_list.get("items", []) if i.get("status", "open").lower() == "open"),
        "closed_count": sum(1 for i in punch_list.get("items", []) if i.get("status", "").lower() == "closed"),
        "operator": punch_list.get("operator", "field-tech"),
        "sealed_at": punch_list.get("sealed_at", datetime.now(timezone.utc).isoformat()),
        "notes": punch_list.get("notes", "")
    }
    payload_bytes = json.dumps(payload_obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.b64encode(payload_bytes).decode("ascii")
    payload_hash = sha256_hex(payload_bytes)
    signature = sign_payload(priv, payload_hash)

    pack = {
        "version": "1",
        "payload": payload_b64,
        "payload_hash": payload_hash,
        "signature": signature,
        "public_key": pub_hex,
        "alg": "ed25519"
    }
    return pack

def demo():
    sample = {
        "list_id": "PL-2026-003",
        "job_id": "JOB-2026-042",
        "client": "Acme Property Management",
        "location": "123 Main St, Springfield MO — RTU-3",
        "walkthrough_date": "2026-10-28",
        "items": [
            {
                "item_id": "P-01",
                "location": "RTU-3 electrical panel",
                "description": "Missing panel cover screw (NE corner)",
                "status": "open",
                "owner": "tech-dan",
                "priority": "low",
                "media_hashes": []
            },
            {
                "item_id": "P-02",
                "location": "RTU-3 condensate drain",
                "description": "Drain line not fully insulated past roof penetration",
                "status": "closed",
                "owner": "tech-dan",
                "priority": "medium",
                "closed_at": "2026-10-28T16:20:00+00:00",
                "media_hashes": ["b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456a1"]
            }
        ],
        "operator": "tech-dan",
        "notes": "Final walkthrough with client site lead present."
    }
    key_path = Path.home() / ".punchlistseal_key.pem"
    priv, pub_hex = load_or_create_key(key_path)
    pack = build_evidence_pack(sample, priv, pub_hex)
    print(json.dumps(pack, indent=2))
    print("\n# Verify with: qg verify <this.json>  (from QuantumGuard)")

def main():
    parser = argparse.ArgumentParser(description="PunchListSeal — local punch-list evidence sealer")
    parser.add_argument("--demo", action="store_true", help="Run demo and print sealed pack")
    parser.add_argument("--list", type=str, help="Path to punch-list JSON file")
    parser.add_argument("--out", type=str, help="Output sealed pack path")
    parser.add_argument("--key", type=str, default=str(Path.home() / ".punchlistseal_key.pem"), help="Private key path")
    args = parser.parse_args()

    if args.demo:
        demo()
        return

    if not args.list:
        parser.print_help()
        return

    with open(args.list) as f:
        punch_list = json.load(f)

    key_path = Path(args.key)
    priv, pub_hex = load_or_create_key(key_path)
    pack = build_evidence_pack(punch_list, priv, pub_hex)

    out_path = args.out or f"sealed_punch_{punch_list.get('list_id', 'unknown')}.json"
    with open(out_path, "w") as f:
        json.dump(pack, f, indent=2)
    print(f"Sealed punch list written to {out_path}")
    print(f"Payload hash: {pack['payload_hash']}")
    print("Verify with QuantumGuard: qg verify", out_path)

if __name__ == "__main__":
    main()
