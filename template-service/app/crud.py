from deps import SessionDep
from models import Template
from sqlmodel import select


async def create_template(session: SessionDep, code: str, content: str, language: str | None ='en'):
    tpl = Template(code=code, content=content, language=language) # type: ignore
    session.add(tpl)
    session.commit()
    session.refresh(tpl)
    return tpl

async def get_template_by_code(session: SessionDep, code: str):
    tpl = session.exec(select(Template).where(Template.code == code)).first()
    return tpl