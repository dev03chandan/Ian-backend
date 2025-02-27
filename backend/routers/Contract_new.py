# Contract_new.py

import os
import io
import pandas as pd
from datetime import datetime
from typing import Optional

# FastAPI imports
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from pydantic import BaseModel, Field

# For PDF & DOCX text extraction
from pdf2image import convert_from_bytes
import pytesseract
from docx import Document

# New-style OpenAI import & client usage in Python
from openai import OpenAI

# Your database & auth
from database import get_db
from .auth import get_current_user, User

# ---------------------------------------------------------------------------
# Initialize the OpenAI client (Python style, analogous to your Node snippet)
# ---------------------------------------------------------------------------
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not os.getenv("OPENAI_API_KEY"):
    print("Warning: OPENAI_API_KEY is not set in environment variables.")

# ---------------------------------------------------------------------------
# Create router
# ---------------------------------------------------------------------------
router = APIRouter()

# ---------------------------------------------------------------------------
# Helper functions for text extraction
# ---------------------------------------------------------------------------
def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Convert a PDF file into images, then extract text using OCR (Tesseract)."""
    try:
        images = convert_from_bytes(file_bytes)
        text = "\n".join(pytesseract.image_to_string(image) for image in images)
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing PDF: {e}")

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing DOCX: {e}")

# ---------------------------------------------------------------------------
# The check function using the latest OpenAI call style
# ---------------------------------------------------------------------------
def check_contract_against_test_cases(contract_text: str, excel_path: str) -> str:
    """
    Reads test cases from an Excel file, sends them along with the contract text
    to the OpenAI ChatCompletion (ChatGPT) API, and returns which test cases
    might be triggered by the contract text.
    """
    # 1. Load the test cases from Excel
    df_testcases = pd.read_excel(excel_path)
    testcases_list = df_testcases.to_dict('records')

    # 2. Prepare system and user messages
    system_message = (
        "You are a compliance detection system. Your job is to analyze a contract "
        "against a provided list of potential non-compliance test cases and identify "
        "which ones may be triggered by the contract. Return the test case that fails along with risk level."
    )

    user_message_1 = f"Contract text:\n{contract_text}"
    user_message_2 = (
        "Here is a list of test cases to check for potential non-compliance issues:\n"
        f"{testcases_list}\n\n"
        "Identify which of these test cases the contract might violate or trigger, "
        "and explain briefly why. Only print the relevant test cases which are flagged."
    )

    # 3. Call the OpenAI chat completion endpoint (Python style)
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-4" / "gpt-4o" etc.
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message_1},
                {"role": "user", "content": user_message_2},
            ],
            store=True,  # analogous to your Node snippet
            max_tokens=1024,
            temperature=0.7,
        )
        # 4. Extract and return the response
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling OpenAI API: {e}"

# ---------------------------------------------------------------------------
# Simple function to derive risk level from GPT text
# ---------------------------------------------------------------------------
def derive_risk_level(analysis_text: str) -> str:
    """
    Naive approach:
    - If 'High' is mentioned anywhere, risk is HIGH
    - Else if 'Medium' is mentioned, risk is MEDIUM
    - Otherwise, LOW
    """
    # Normalize case for easier searching
    text_lower = analysis_text.lower()
    if "high" in text_lower:
        return "HIGH"
    elif "medium" in text_lower:
        return "MEDIUM"
    else:
        return "LOW"

# ---------------------------------------------------------------------------
# New Endpoint
# ---------------------------------------------------------------------------
@router.post("/check_contract_against_test_cases/")
async def check_contract_against_test_cases_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    1. Accept a PDF or DOCX file for the contract.
    2. Extract the text.
    3. Compare it against test cases in an Excel file.
       Path: "comparison_data_excel/Test cases contracts.xlsx"
    4. Derive a risk level from the GPT output.
    5. Save the result in the documents DB.
    6. Return the analysis result & document ID & risk level.
    """

    # Hard-coded path (or load from config/env):
    excel_file_path = "comparison_data_excel/Test cases contracts.xlsx"

    # 1. Read file bytes
    file_bytes = await file.read()
    file_extension = file.filename.split(".")[-1].lower()

    # 2. Extract text based on file extension
    if file_extension == "pdf":
        contract_text = extract_text_from_pdf(file_bytes)
    elif file_extension == "docx":
        contract_text = extract_text_from_docx(file_bytes)
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Only PDF and DOCX are allowed.",
        )

    if not contract_text.strip():
        raise HTTPException(status_code=400, detail="No text extracted from file.")

    # 3. Run the new test case check
    analysis_result = check_contract_against_test_cases(
        contract_text=contract_text,
        excel_path=excel_file_path
    )

    # 4. Derive a simple risk level from the text
    risk_level = derive_risk_level(analysis_result)

    # 5. Store in the DB
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
            'contract_test_check',
            datetime.utcnow().isoformat(),
            'processed',
            risk_level,
            analysis_result
        ))
        document_id = cursor.lastrowid

    # 6. Return JSON response
    return {
        "document_id": document_id,
        "risk_level": risk_level,
        "analysis_result": analysis_result
    }
