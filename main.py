import os
import hashlib
from fastapi import FastAPI, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

import models
from database import get_db, init_db
from crypto import VaultCrypto, generate_secure_token

# Garante a criação imediata das tabelas na inicialização
init_db()

# Segurança: Tenta ler a chave do sistema operacional. Se não achar, usa a chave atual para dev local.
MASTER_KEY = os.getenv("VAULT_MASTER_KEY", "EwqYeCkOl_O5PmyRRODX2Pis-4bAmNH3v2knJe7zuCo=")

app = FastAPI(
    title="ForteKnox Vault API",
    description="Cofre seguro para armazenamento, criptografia e gerenciamento de credenciais.",
    version="1.1.0"
)

def get_current_app(x_vault_token: str = Header(..., alias="X-Vault-Token"), db: Session = Depends(get_db)) -> models.Application:
    token_hash = hashlib.sha256(x_vault_token.encode('utf-8')).hexdigest()
    app_record = db.query(models.Application).filter(models.Application.token_hash == token_hash).first()
    
    if not app_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso inválido ou aplicação não registrada."
        )
    return app_record

# --- SCHEMAS PYDANTIC ---

class ApplicationCreate(BaseModel):
    name: str

class ApplicationResponse(BaseModel):
    name: str
    token: str

class SecretCreate(BaseModel):
    key_name: str
    value: str

class SecretValueResponse(BaseModel):
    key_name: str
    value: str

class SecretKeysListResponse(BaseModel):
    keys: List[str]

class AuditLogResponse(BaseModel):
    action: str
    details: str
    timestamp: str

    class Config:
        from_attributes = True

# --- ROTAS DA API ---

@app.get("/")
def read_root():
    return {"status": "healthy", "message": "ForteKnox Vault está totalmente operacional."}

@app.post("/api/v1/apps", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def register_application(app_data: ApplicationCreate, db: Session = Depends(get_db)):
    existing_app = db.query(models.Application).filter(models.Application.name == app_data.name).first()
    if existing_app:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uma aplicação com este nome já está registrada."
        )

    token_limpo, token_hash = generate_secure_token()
    new_app = models.Application(name=str(app_data.name), token_hash=str(token_hash))
    
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    
    return ApplicationResponse(name=str(new_app.name), token=str(token_limpo))

@app.post("/api/v1/secrets", status_code=status.HTTP_201_CREATED)
def save_secret(secret_data: SecretCreate, db: Session = Depends(get_db), current_app: models.Application = Depends(get_current_app)):
    target_app_id = int(current_app.id)
    crypto = VaultCrypto(MASTER_KEY)
    encrypted_val = crypto.encrypt_secret(str(secret_data.value))
    
    existing_secret = db.query(models.Secret).filter(
        models.Secret.app_id == target_app_id,
        models.Secret.key_name == str(secret_data.key_name)
    ).first()
    
    if existing_secret:
        existing_secret.encrypted_value = str(encrypted_val)
        action_detail = f"Atualizou a chave: {secret_data.key_name}"
    else:
        new_secret = models.Secret(
            app_id=target_app_id,
            key_name=str(secret_data.key_name),
            encrypted_value=str(encrypted_val)
        )
        db.add(new_secret)
        action_detail = f"Criou a chave: {secret_data.key_name}"
        
    log = models.AuditLog(app_id=target_app_id, action="WRITE_SECRET", details=action_detail)
    db.add(log)
    db.commit()
    
    return {"status": "success", "message": f"Segredo '{secret_data.key_name}' salvo com sucesso."}

@app.get("/api/v1/secrets", response_model=SecretKeysListResponse)
def list_secret_keys(db: Session = Depends(get_db), current_app: models.Application = Depends(get_current_app)):
    """Lista apenas os nomes das chaves armazenadas para a aplicação autenticada."""
    target_app_id = int(current_app.id)
    
    secrets = db.query(models.Secret).filter(models.Secret.app_id == target_app_id).all()
    keys_list = [str(s.key_name) for s in secrets]
    
    log = models.AuditLog(app_id=target_app_id, action="LIST_SECRETS", details=f"Listou {len(keys_list)} chaves.")
    db.add(log)
    db.commit()
    
    return SecretKeysListResponse(keys=keys_list)

@app.get("/api/v1/secrets/{key_name}", response_model=SecretValueResponse)
def get_secret(key_name: str, db: Session = Depends(get_db), current_app: models.Application = Depends(get_current_app)):
    target_app_id = int(current_app.id)
    
    secret = db.query(models.Secret).filter(
        models.Secret.app_id == target_app_id,
        models.Secret.key_name == str(key_name)
    ).first()
    
    if not secret:
        raise HTTPException(status_code=404, detail="Segredo não encontrado para esta aplicação.")
        
    crypto = VaultCrypto(MASTER_KEY)
    plain_value = crypto.decrypt_secret(secret.encrypted_value)
    
    log = models.AuditLog(app_id=target_app_id, action="READ_SECRET", details=f"Leu a chave: {key_name}")
    db.add(log)
    db.commit()
    
    return SecretValueResponse(key_name=str(secret.key_name), value=str(plain_value))

@app.get("/api/v1/logs", response_model=List[AuditLogResponse])
def get_audit_logs(db: Session = Depends(get_db), current_app: models.Application = Depends(get_current_app)):
    """Retorna o histórico de todas as operações realizadas por esta aplicação."""
    target_app_id = int(current_app.id)
    
    logs = db.query(models.AuditLog).filter(
        models.AuditLog.app_id == target_app_id
    ).order_by(models.AuditLog.timestamp.desc()).all()
    
    return [
        AuditLogResponse(
            action=str(l.action),
            details=str(l.details if l.details else ""),
            timestamp=l.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        ) for l in logs
    ]

@app.delete("/api/v1/secrets/{key_name}", status_code=status.HTTP_200_OK)
def delete_secret(key_name: str, db: Session = Depends(get_db), current_app: models.Application = Depends(get_current_app)):
    """Remove permanentemente um segredo do cofre."""
    target_app_id = int(current_app.id)
    
    secret = db.query(models.Secret).filter(
        models.Secret.app_id == target_app_id,
        models.Secret.key_name == str(key_name)
    ).first()
    
    if not secret:
        raise HTTPException(status_code=404, detail="Segredo não encontrado para exclusão.")
        
    db.delete(secret)
    
    log = models.AuditLog(app_id=target_app_id, action="DELETE_SECRET", details=f"Deletou a chave: {key_name}")
    db.add(log)
    db.commit()
    
    return {"status": "success", "message": f"Segredo '{key_name}' foi removido com sucesso."}