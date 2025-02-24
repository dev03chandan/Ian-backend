import os
import io
import csv
import zipfile
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from collections import Counter, defaultdict
from typing import List
from fuzzywuzzy import fuzz
from fastapi import APIRouter

from pydantic import BaseModel, Field
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
from pdf2image import convert_from_bytes
import pytesseract
from openai import OpenAI
from docx import Document
from pydantic import BaseModel, Field

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi import APIRouter

router = APIRouter()



# -----------------------------------------------------------------------------
# Data Models
# -----------------------------------------------------------------------------
class Invoice(BaseModel):
    invoice_id: str
    vendor: str
    amount: float
    gsa_standard: float
    payment_routing: str
    invoice_date: Optional[str] = None
    payment_delay_days: Optional[int] = Field(
        None, description="Number of days payment is delayed."
    )
    early_payment_requested: Optional[bool] = Field(
        False, description="Whether early payment was requested before work completion."
    )
    supporting_documents: Optional[bool] = Field(
        True,
        description="Whether supporting documentation for services/goods was provided.",
    )
    description: Optional[str] = Field(
        "", description="Invoice item description for duplicate detection."
    )


class FraudIssue(BaseModel):
    issue: str
    severity: str
    risk_increase: int
    recommended_action: str


class InvoiceFraudReport(BaseModel):
    invoice_id: str
    risk_score: int
    risk_level: str
    issues: List[FraudIssue]
    final_recommendation: str


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def is_offshore(payment_routing: str) -> bool:
    flagged_countries = ["cayman islands", "panama", "belize"]
    return any(country in payment_routing.lower() for country in flagged_countries)


def check_overpricing(amount: float, gsa_standard: float) -> bool:
    return amount > (gsa_standard * 1.3)


def parse_csv_invoices(file_data: bytes) -> List[Invoice]:
    text = file_data.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    invoices = []

    for row in reader:
        try:
            invoice = Invoice(
                invoice_id=row.get("invoice_id", "").strip(),
                vendor=row.get("vendor", "").strip(),
                amount=float(row.get("amount", "0").strip()),
                gsa_standard=float(row.get("gsa_standard", "0").strip()),
                payment_routing=row.get("payment_routing", "").strip(),
                invoice_date=row.get("invoice_date", "").strip(),
                payment_delay_days=(
                    int(row.get("payment_delay_days", "0").strip())
                    if row.get("payment_delay_days")
                    else None
                ),
                early_payment_requested=row.get("early_payment_requested", "False")
                .strip()
                .lower()
                == "true",
                supporting_documents=row.get("supporting_documents", "True")
                .strip()
                .lower()
                == "true",
                description=row.get("description", "").strip(),
            )
            invoices.append(invoice)
        except Exception as e:
            print(f"Error processing row {row}: {e}")

    return invoices


def detect_duplicate_invoices(invoices: List[Invoice]) -> List[str]:
    seen_invoices = {}
    potential_duplicates = []

    for inv in invoices:
        key = f"{inv.vendor.lower()}_{inv.amount}_{inv.invoice_date}"
        if key in seen_invoices:
            potential_duplicates.append(
                f"Exact duplicate found: {inv.invoice_id} (Vendor: {inv.vendor}, Amount: {inv.amount})"
            )
        else:
            seen_invoices[key] = inv.invoice_id

    vendor_groups = defaultdict(list)
    for inv in invoices:
        vendor_groups[inv.vendor.lower()].append(inv)

    for vendor, invoices_list in vendor_groups.items():
        for i in range(len(invoices_list)):
            for j in range(i + 1, len(invoices_list)):
                inv1, inv2 = invoices_list[i], invoices_list[j]
                if (
                    fuzz.ratio(inv1.description.lower(), inv2.description.lower()) > 80
                    and fuzz.ratio(inv1.vendor.lower(), inv2.vendor.lower()) > 80
                    and abs(float(inv1.amount) - float(inv2.amount)) <= 10
                    and inv1.invoice_id != inv2.invoice_id
                ):
                    potential_duplicates.append(
                        f"Potential duplicate invoices: {inv1.invoice_id} and {inv2.invoice_id} (Similar descriptions & amounts)"
                    )

    return potential_duplicates


def analyze_invoices(invoices: List[Invoice]) -> List[InvoiceFraudReport]:
    invoice_ids = [inv.invoice_id for inv in invoices]
    exact_duplicates = {
        inv_id for inv_id, count in Counter(invoice_ids).items() if count > 1
    }
    fuzzy_duplicates = detect_duplicate_invoices(invoices)
    reports = []

    for inv in invoices:
        issues = []
        risk_score = 0

        if inv.invoice_id in exact_duplicates:
            risk_score += 30
            issues.append(
                FraudIssue(
                    issue=f"Duplicate invoice {inv.invoice_id} detected.",
                    severity="High",
                    risk_increase=30,
                    recommended_action="Verify before payment.",
                )
            )

        for duplicate in fuzzy_duplicates:
            if inv.invoice_id in duplicate:
                risk_score += 25
                issues.append(
                    FraudIssue(
                        issue=f"Potential duplicate invoice: {duplicate}",
                        severity="Medium-High",
                        risk_increase=25,
                        recommended_action="Manually review for payment fraud.",
                    )
                )

        if check_overpricing(inv.amount, inv.gsa_standard):
            risk_score += 25
            issues.append(
                FraudIssue(
                    issue="Overpricing detected.",
                    severity="High",
                    risk_increase=25,
                    recommended_action="Verify pricing.",
                )
            )

        if is_offshore(inv.payment_routing):
            risk_score += 35
            issues.append(
                FraudIssue(
                    issue="Offshore payment detected.",
                    severity="High",
                    risk_increase=35,
                    recommended_action="Flag for compliance review.",
                )
            )

        if inv.payment_delay_days:
            if inv.payment_delay_days > 30:
                risk_score += 30
            elif inv.payment_delay_days > 15:
                risk_score += 20
            elif inv.payment_delay_days > 5:
                risk_score += 10
            issues.append(
                FraudIssue(
                    issue="Detected payment delays.",
                    severity="Medium",
                    risk_increase=10,
                    recommended_action="Review payment timelines.",
                )
            )

        if inv.early_payment_requested:
            risk_score += 20
            issues.append(
                FraudIssue(
                    issue="Invoice requests early payment.",
                    severity="High",
                    risk_increase=20,
                    recommended_action="Ensure service completion first.",
                )
            )

        if not inv.supporting_documents:
            risk_score += 25
            issues.append(
                FraudIssue(
                    issue="Missing supporting documentation.",
                    severity="High",
                    risk_increase=25,
                    recommended_action="Request proof of delivery.",
                )
            )

        risk_score = min(risk_score, 100)
        risk_level = (
            "Fraud Detected 🔴"
            if risk_score >= 80
            else "Suspicious 🟡" if risk_score >= 40 else "Safe 🟢"
        )
        final_recommendation = (
            "Immediate review required."
            if risk_score >= 80
            else "Review before payment." if risk_score >= 40 else "Likely safe."
        )
        reports.append(
            InvoiceFraudReport(
                invoice_id=inv.invoice_id,
                risk_score=risk_score,
                risk_level=risk_level,
                issues=issues,
                final_recommendation=final_recommendation,
            )
        )

    return reports


@router.post("/upload-csv-invoices/")
async def upload_csv_invoices(file: UploadFile = File(...)):
    """Upload a CSV file for invoice fraud analysis."""
    file_data = await file.read()
    invoices = parse_csv_invoices(file_data)
    analysis_report = analyze_invoices(invoices)
    return {
        "parsed_invoices": [inv.dict() for inv in invoices],
        "analysis_report": [report.dict() for report in analysis_report],
    }