import hashlib
from typing import Any, Dict

from settings import settings


class TransactionSignatureService:
    @staticmethod
    def generate_signature(
        data: Dict[str, Any], secret_key: str = settings.secret_key.get_secret_value()
    ) -> str:
        data = data.copy()
        data.pop("signature", None)

        sorted_values = (str(data[k]) for k in sorted(data))
        message = "".join(sorted_values) + secret_key

        return hashlib.sha256(message.encode()).hexdigest()

    @staticmethod
    def verify_signature(
        data: Dict[str, Any], secret_key: str = settings.secret_key.get_secret_value()
    ) -> bool:
        received_signature = data["signature"]
        expected_signature = TransactionSignatureService.generate_signature(
            data, secret_key
        )

        return received_signature == expected_signature
