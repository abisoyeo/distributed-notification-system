from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from deps import SessionDep
from models import *
from fastapi.exceptions import HTTPException
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from core.db import engine
import crud

def initialize_db():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifeSpan(app: FastAPI):
    initialize_db()
    yield

app = FastAPI(
    title='Template Service',
    lifespan=lifeSpan
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get('/health')
async def health():
    return {"status": "ok"}


@app.post('/templates/', response_model=TemplateOut)
async def create_template(session: SessionDep, payload: CreateTemplateReq):
    if await crud.get_template_by_code(session=session, code=payload.code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Template code already exists")
    tpl = await crud.create_template(session=session, code=payload.code, content=payload.content, language=payload.language)
    return tpl

@app.get('/templates/{code}', response_model=TemplateOut)
async def get_template(session: SessionDep, code: str):
    tpl = await crud.get_template_by_code(session=session, code=code)
    if not tpl:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='not found')
    return tpl

@app.post('/render/{code}')
async def render_template(session: SessionDep, code: str, variables: dict):
    tpl = await crud.get_template_by_code(session=session, code=code)
    if not tpl:
        raise HTTPException(404, 'template not found')
    rendered = tpl.render(variables)
    return {"rendered": rendered}
