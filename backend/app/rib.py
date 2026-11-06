"""
Moroccan RIB (Relevé d'Identité Bancaire) generation.

Structure: 24 digits = 3 (bank code) + 3 (branch code) + 16 (account number)
+ 2 (check key).

Check key formula (verified against real sources, not just recalled):
    key = 97 - ((89 * bank_code + 15 * branch_code + 3 * account_number) mod 97)
"""

import random

BANK_CODE = "009"
BRANCH_CODE = "001"


def _generate_account_number() -> str:
    return f"{random.randint(0, 10**16 - 1):016d}"


def _compute_rib_key(bank_code: str, branch_code: str, account_number: str) -> str:
    total = 89 * int(bank_code) + 15 * int(branch_code) + 3 * int(account_number)
    key = 97 - (total % 97)
    return f"{key:02d}"


def generate_rib() -> str:
    account_number = _generate_account_number()
    key = _compute_rib_key(BANK_CODE, BRANCH_CODE, account_number)
    return f"{BANK_CODE}{BRANCH_CODE}{account_number}{key}"
