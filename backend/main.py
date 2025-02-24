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
from routers import contract_router, invoice_router


# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contract_router, tags=["Contracts"])

app.include_router(invoice_router, tags=["Invoices"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
