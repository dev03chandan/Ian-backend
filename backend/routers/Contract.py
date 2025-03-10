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
from fastapi import Depends

from pydantic import BaseModel, Field
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
from pdf2image import convert_from_bytes
import pytesseract
from openai import OpenAI
from docx import Document
from pydantic import BaseModel, Field
import json
from database import get_db
from .auth import get_current_user, User
from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware

from fastapi import APIRouter   

router = APIRouter()


regulatory_data = {}
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not os.getenv("OPENAI_API_KEY"):
    print("Warning: OPENAI_API_KEY is not set in environment variables.")


def extract_text_from_dita(file_path: str) -> str:
    """
    Parse a DITA XML file and return its complete text content.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        full_text = " ".join(text.strip() for text in root.itertext() if text.strip())
        return full_text
    except ET.ParseError as e:
        return f"Error parsing XML: {e}"


def load_far_regulatory_data() -> dict:
    """
    Downloads FAR regulatory DITA ZIP files, extracts designated files,
    and returns a mapping of file names to their extracted text content.
    """
    base_url = (
        "https://www.acquisition.gov/sites/default/files/current/far/compiled_dita/"
    )
    dita_files = [
        "part_52/52.232-25.dita",
        "part_52/52.244-2.dita",
        "part_52/52.249-8.dita",
        "part_52/52.249-9.dita",
        "part_52/52.249-10.dita",
        "part_9/9.103.dita",
        "part_52/52.209-5.dita",
        "part_3/3.101-1.dita",
        "part_9/9.505.dita",
    ]

    parts = set(f.split("/")[0] for f in dita_files)
    zip_files = {}
    for part in parts:
        zip_url = f"{base_url}{part}.zip"
        response = requests.get(zip_url)
        if response.status_code == 200:
            zip_files[part] = zipfile.ZipFile(io.BytesIO(response.content))
            print(f"Downloaded {part}.zip successfully.")
        else:
            print(f"Error downloading {part}.zip: Status code {response.status_code}")

    output_folder = "extracted_dita"
    os.makedirs(output_folder, exist_ok=True)

    extracted_texts = {}
    for file_name in dita_files:
        part = file_name.split("/")[0]
        if part in zip_files:
            zip_ref = zip_files[part]
            if file_name in zip_ref.namelist():
                zip_ref.extract(file_name, output_folder)
                dita_file_path = os.path.join(output_folder, file_name)
                extracted_texts[file_name] = extract_text_from_dita(dita_file_path)
            else:
                extracted_texts[file_name] = "Error: File not found in ZIP."
        else:
            extracted_texts[file_name] = "Error: No ZIP available for this part."
    return extracted_texts


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Convert a PDF file into images, then extract text using OCR (Tesseract).
    """
    try:
        images = convert_from_bytes(file_bytes)
        text = "\n".join(pytesseract.image_to_string(image) for image in images)
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing PDF: {e}")


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract text from a DOCX file using python-docx.
    """
    try:
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing DOCX: {e}")


def analyze_contract(contract_text: str) -> str:
    """
    Constructs a prompt that includes the FAR regulatory details and the contract text.
    Sends the prompt to OpenAI and returns the analysis result.
    """
    regulatory_data = load_far_regulatory_data()
    print("DEBUG: ", regulatory_data)
    regulatory_info = "\n\n".join(
        [f"{key}:\n{value}" for key, value in regulatory_data.items()]
    )
    

    system_message = (
    "You are a contract compliance analyst specializing in evaluating contracts against Federal Acquisition Regulations (FAR). "
    "Your responsibilities include:\n"
    "1. Breaking down the contract into key sections.\n"
    "2. Extracting key clauses and comparing them to the regulatory reference data.\n"
    "3. Focusing on these five compliance areas:\n"
    "   - Pricing & Payment Terms (FAR 52.232-25)\n"
    "   - Subcontracting Restrictions (FAR 52.244-2)\n"
    "   - Penalties for Non-Performance\n"
    "   - Vendor Eligibility & Registration (verify against SAM.gov requirements)\n"
    "   - Conflict of Interest & Undisclosed Relationships\n"
    "4. Flagging any missing or incomplete clauses.\n"
    "5. Assigning a risk level for each area: Low (fully compliant), Medium (minor issues), or High (major non-compliance).\n"
    "6. Calculating an overall compliance score (0-100%), where a higher score indicates lower risk and better compliance.\n"
    "7. Providing a concise summary of issues.\n"
    "Ensure that your analysis is clear, structured, and concise."
)


    user_message = (
        f"Below is the regulatory reference information:\n\n{regulatory_info}\n\n"
        f'Below is the contract text to be analyzed:\n"""\n{contract_text}\n"""'
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
            max_tokens=1500,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error in OpenAI API call: {e}"



@router.post("/analyze_contract/")
async def analyze_contract_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Accepts a PDF or DOCX file, extracts its text, analyzes it against FAR regulatory data,
    and stores the results in the database.
    """
    file_bytes = await file.read()
    file_extension = file.filename.split(".")[-1].lower()

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

    # Analyze the contract
    analysis_result = analyze_contract(contract_text)
    
    # Extract risk level from the analysis
    risk_level = "HIGH"  # Default value
    if "Overall Compliance Risk Score: " in analysis_result:
        score = int(analysis_result.split("Overall Compliance Risk Score: ")[1].split("%")[0])
        print('Score: ', score)
        risk_level = "LOW" if score > 75 else "MEDIUM" if score > 50 else "HIGH"

    # Store the document and analysis in the database
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
            'contract',
            datetime.utcnow().isoformat(),
            'processed',
            risk_level,
            analysis_result
        ))
        document_id = cursor.lastrowid

    return {
        "analysis": analysis_result,
        "document_id": document_id,
        "risk_level": risk_level
    }