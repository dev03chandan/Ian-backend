# Invoice_new.py

import os
import logging
import pandas as pd
import fitz  # PyMuPDF
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from openai import OpenAI

# Database and auth (adjust to your actual imports)
from database import get_db
from .auth import get_current_user, User

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# ---------------------------------------------------------------------------
# Initialize OpenAI client (Python style, matching your "latest version" usage)
# ---------------------------------------------------------------------------
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not os.getenv("OPENAI_API_KEY"):
    logging.warning("Warning: OPENAI_API_KEY is not set in environment variables.")

# ---------------------------------------------------------------------------
# Create the FastAPI router
# ---------------------------------------------------------------------------
router = APIRouter()

# ---------------------------------------------------------------------------
# Helper function: Load test cases from Excel
# ---------------------------------------------------------------------------
def load_test_cases(
    excel_path: str,
    sheet_name: str = "can you generate a table of all"
) -> pd.DataFrame:
    """
    Load test cases from an Excel file, including risk level and scenario details.
    Expects columns: 'Test Case ID', 'Test Case Name/Scenario', 'Description', 'Risk Level'.
    """
    try:
        xls = pd.ExcelFile(excel_path)
        df = pd.read_excel(xls, sheet_name=sheet_name)
        # Keep only relevant columns and drop rows with missing data
        df = df[["Test Case ID", "Test Case Name/Scenario", "Description", "Risk Level"]].dropna()
        logging.info("Loaded %d test cases.", len(df))
        return df
    except Exception as e:
        logging.error("Error loading test cases from Excel: %s", e)
        raise HTTPException(status_code=500, detail="Failed to load test cases from Excel.")

# ---------------------------------------------------------------------------
# Helper function: Extract text from PDF using PyMuPDF (fitz)
# ---------------------------------------------------------------------------
def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    """
    Extract text from a PDF invoice given as bytes.
    """
    try:
        text = ""
        # Open from bytes stream
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
        if not text.strip():
            logging.warning("No text was extracted from the PDF.")
        return text
    except Exception as e:
        logging.error("Error reading PDF file: %s", e)
        raise HTTPException(status_code=400, detail="Failed to process PDF file.")

# ---------------------------------------------------------------------------
# Helper function: Analyze invoice with OpenAI
# ---------------------------------------------------------------------------
def analyze_invoice_with_openai(invoice_text: str, test_cases: pd.DataFrame) -> str:
    """
    Use the OpenAI API to determine which test cases the invoice fails,
    considering risk levels and scenarios.
    """
    # Format test cases as a string for inclusion in the prompt
    test_cases_str = test_cases.to_string(index=False)

    # Build the prompt for the OpenAI API
    prompt = (
        "You are an expert invoice compliance checker. Compare the invoice details below "
        "with the test cases provided and determine which test cases the invoice fails.\n\n"
        "Invoice Details:\n"
        f"{invoice_text}\n\n"
        "Test Cases:\n"
        f"{test_cases_str}\n\n"
        "Return the failed test case details in the following format:\n"
        "Test Case ID | Test Case Name | Risk Level | Description\n"
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",  # Adjust to your preferred model
            messages=[
                {"role": "system", "content": "You are an expert invoice compliance checker."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        answer = response.choices[0].message.content
        logging.info("Received response from OpenAI API.")
        return answer.strip()
    except Exception as e:
        logging.error("Error during OpenAI API call: %s", e)
        raise HTTPException(status_code=500, detail="OpenAI API call failed.")

# ---------------------------------------------------------------------------
# FastAPI Endpoint
# ---------------------------------------------------------------------------
@router.post("/check_invoice_compliance/")
async def check_invoice_compliance_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    1. Accepts a PDF invoice (as a file upload).
    2. Extracts text from the PDF using PyMuPDF (fitz).
    3. Loads test cases from an Excel file.
    4. Analyzes the invoice text with OpenAI to find which test cases it fails.
    5. Stores the analysis in the 'documents' table and returns the result.
    """

    # Hard-coded path to your Excel file (adjust as needed)
    excel_file_path = "comparison_data_excel/Test cases invoices.xlsx"

    # Step 1: Read file bytes
    file_bytes = await file.read()
    file_extension = file.filename.split(".")[-1].lower()

    # Step 2: Only allow PDF for this endpoint
    if file_extension != "pdf":
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Only PDF is allowed for invoices."
        )

    # Extract the PDF text
    invoice_text = extract_text_from_pdf_bytes(file_bytes)
    if not invoice_text.strip():
        raise HTTPException(status_code=400, detail="No text extracted from PDF invoice.")

    # Step 3: Load test cases from Excel
    test_cases = load_test_cases(excel_file_path)

    # Step 4: Analyze the invoice with OpenAI
    analysis_result = analyze_invoice_with_openai(invoice_text, test_cases)

    # (Optional) Derive a simple risk level if you want
    # For example: "HIGH" if the text contains 'High', else "LOW"
    risk_level = "HIGH" if "High" in analysis_result else "LOW"

    # Step 5: Store the result in the database
    with get_db() as db:
        cursor = db.execute('''
            INSERT INTO documents (
                user_id,
                document_name,
                document_type,
                upload_date,
                status,
                risk_level,
                report_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            current_user.id,
            file.filename,
            'invoice_test_check',
            datetime.utcnow().isoformat(),
            'processed',
            risk_level,
            analysis_result
        ))
        document_id = cursor.lastrowid

    # Return JSON response
    return {
        "document_id": document_id,
        "risk_level": risk_level,
        "analysis_result": analysis_result
    }
