import hmac, hashlib, urllib.parse, json
from typing import Dict, Tuple, Optional
from config import BOT_TOKEN

def _parse_init_data(init_data: str) -> Dict[str, str]:
    parsed = urllib.parse.parse_qs(init_data, strict_parsing=False)
    return {k: v[0] for k, v in parsed.items()}

def verify_init_data(init_data: str) -> Tuple[bool, Optional[Dict[str, str]]]:
    try:
        data = _parse_init_data(init_data)
        received_hash = data.get("hash")
        if not received_hash:
            return False, None

        pairs = []
        for k in sorted(data.keys()):
            if k == "hash":
                continue
            pairs.append(f"{k}={data[k]}")
        data_check_string = "\n".join(pairs)

        secret_key = hmac.new(
            key=b"WebAppData",
            msg=BOT_TOKEN.encode("utf-8"),
            digestmod=hashlib.sha256
        ).digest()

        calc_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode("utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(calc_hash, received_hash):
            return False, None

        return True, data
    except Exception:
        return False, None

def extract_tg_user(init_data: str) -> dict:
    ok, data = verify_init_data(init_data)
    if not ok or not data:
        return {}
    if "user" not in data:
        return {}
    return json.loads(data["user"])
