from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json
from database import get_db
from .auth import get_current_user, User

router = APIRouter()

class DocumentResponse(BaseModel):
    id: int
    document_name: str
    document_type: str
    upload_date: str
    status: str
    risk_level: Optional[str]
    report_data: Optional[str]

@router.get("/my-documents", response_model=List[DocumentResponse])
async def get_my_documents(current_user: User = Depends(get_current_user)):
    with get_db() as db:
        documents = db.execute('''
        SELECT * FROM documents
        WHERE user_id = ?
        ORDER BY upload_date DESC
        ''', (current_user.id,)).fetchall()
        
        return [
            DocumentResponse(
                id=doc['id'],
                document_name=doc['document_name'],
                document_type=doc['document_type'],
                upload_date=doc['upload_date'],
                status=doc['status'],
                risk_level=doc['risk_level'],
                report_data=doc['report_data']
            )
            for doc in documents
        ]

@router.get("/all-documents", response_model=List[DocumentResponse])
async def get_all_documents(current_user: User = Depends(get_current_user)):
    if current_user.username != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can access all documents"
        )

    with get_db() as db:
        documents = db.execute('''
        SELECT * FROM documents
        ORDER BY upload_date DESC
        ''').fetchall()
        
        return [
            DocumentResponse(
                id=doc['id'],
                document_name=doc['document_name'],
                document_type=doc['document_type'],
                upload_date=doc['upload_date'],
                status=doc['status'],
                risk_level=doc['risk_level'],
                report_data=doc['report_data']
            )
            for doc in documents
        ]

@router.get("/document/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user)
):
    with get_db() as db:
        document = db.execute('''
        SELECT * FROM documents
        WHERE id = ? AND (user_id = ? OR ? = 'admin')
        ''', (document_id, current_user.id, current_user.username)).fetchone()
        
        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found or access denied"
            )
        
        return DocumentResponse(
            id=document['id'],
            document_name=document['document_name'],
            document_type=document['document_type'],
            upload_date=document['upload_date'],
            status=document['status'],
            risk_level=document['risk_level'],
            report_data=document['report_data']
        )