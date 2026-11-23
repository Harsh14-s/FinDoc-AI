"""Data Schemas, Normalization, and Privacy Masking Helpers for FinDocAI.

Provides standardized schemas for financial documents, date/amount normalizers,
and field confidence definitions.
Group G382: Harsh Shukla, Akshita Singh.
"""

import re
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


def normalize_amount(amt_str: Any) -> Optional[float]:
    """Parse numeric currency strings into clean float values.

    Handles 'INR 12,345.50', 'Rs. 1,000', '(500.00)', and '-' values.
    """
    if amt_str is None:
        return None
    if isinstance(amt_str, (int, float)):
        return round(float(amt_str), 2)

    s = str(amt_str).strip()
    if not s or s == "-":
        return 0.0

    # Handle parenthesis negative amounts: (100.00) -> -100.00
    is_negative = False
    if s.startswith("(") and s.endswith(")"):
        is_negative = True
        s = s[1:-1].strip()

    # First strip common currency prefixes (including possible period in 'Rs.')
    s = re.sub(r"^(?:INR|Rs\.?|USD|EUR|₹|\$)\s*", "", s, flags=re.IGNORECASE)
    # Remove comma thousands separators
    s = s.replace(",", "").strip()

    # Match numeric float or integer pattern
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return 0.0

    try:
        val = float(m.group(0))
        return round(-val if is_negative else val, 2)
    except ValueError:
        return None


def normalize_date(date_str: Any) -> Optional[str]:
    """Normalize varying date formats into standardized ISO-8601 (YYYY-MM-DD).

    Supports: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY, DD-Mon-YYYY, DD Month YYYY.
    """
    if not date_str:
        return None
    s = str(date_str).strip()

    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d-%b-%Y",
        "%d-%B-%Y",
        "%d %b %Y",
        "%d %B %Y",
        "%m/%d/%Y"
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    return s  # Return raw string if non-standard


def mask_sensitive_value(value: Optional[str], value_type: str = "generic") -> str:
    """Mask sensitive values (PAN, Aadhaar, Account No) for privacy protection in UI and logs.

    Never exposes full PII in review outputs or audit traces.
    """
    if not value:
        return ""
    val = str(value).strip()

    if value_type.lower() == "pan":
        # Keep first 2 and last 2 characters: ABXXXXXX4F
        if len(val) >= 5:
            return f"{val[:2]}{'X' * (len(val) - 4)}{val[-2:]}"
        return "XXXXX"

    elif value_type.lower() == "aadhaar":
        # Aadhaar: 2345 6789 0123 -> XXXX XXXX 0123
        digits = re.sub(r"\D", "", val)
        if len(digits) >= 4:
            return f"XXXX XXXX {digits[-4:]}"
        return "XXXX XXXX XXXX"

    elif value_type.lower() == "account":
        # Account Number: keep last 4 digits
        if len(val) >= 4:
            return f"{'X' * (len(val) - 4)}{val[-4:]}"
        return "XXXX"

    # Generic fallback
    if len(val) > 4:
        return f"{'X' * (len(val) - 4)}{val[-4:]}"
    return "****"


class TransactionItem(BaseModel):
    """Normalized representation of a single bank transaction."""
    date: str
    description: str
    ref_no: str
    debit: float = 0.0
    credit: float = 0.0
    balance: float
    confidence: float = 0.95


class BankStatementSchema(BaseModel):
    """Normalized schema for Bank Statement extraction."""
    bank_name: Optional[str] = None
    account_holder: Optional[str] = None
    account_number: Optional[str] = None
    ifsc: Optional[str] = None
    branch: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    opening_balance: Optional[float] = None
    closing_balance: Optional[float] = None
    total_deposits: Optional[float] = None
    total_withdrawals: Optional[float] = None
    transactions: List[TransactionItem] = Field(default_factory=list)
    field_confidences: Dict[str, float] = Field(default_factory=dict)


class InvoiceLineItem(BaseModel):
    """Normalized line item within a commercial invoice."""
    description: str
    quantity: int = 1
    unit_price: float = 0.0
    total: float = 0.0
    confidence: float = 0.95


class InvoiceSchema(BaseModel):
    """Normalized schema for Tax Invoice extraction."""
    vendor_name: Optional[str] = None
    vendor_gstin: Optional[str] = None
    client_name: Optional[str] = None
    client_gstin: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    subtotal: Optional[float] = None
    tax_amount: Optional[float] = None
    tax_rate: Optional[str] = "18%"
    grand_total: Optional[float] = None
    line_items: List[InvoiceLineItem] = Field(default_factory=list)
    field_confidences: Dict[str, float] = Field(default_factory=dict)


class KYCSchema(BaseModel):
    """Normalized schema for KYC identity documents (PAN / Aadhaar)."""
    document_type: str  # "pan_card" or "aadhaar_card"
    full_name: Optional[str] = None
    father_name: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[str] = None
    id_number: Optional[str] = None  # PAN or Aadhaar number
    address: Optional[str] = None
    field_confidences: Dict[str, float] = Field(default_factory=dict)
