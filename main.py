from fastapi import FastAPI, Form, status, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from classes import *
from database_stuff import engine
from sqlmodel import Session, select
from typing import Annotated


app = FastAPI()
templates = Jinja2Templates('templates')
session = Session(bind=engine)


statement = select(Hotel)
answer = session.exec(statement).all()
if answer == None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


CURRENT_USER = None


@app.get('/', response_model=Hotel, tags=['Pages'])
async def show_hotels(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='main_page.html',
        context={
            'result': answer
        }
    )


@app.get('/registration', response_model=User, tags=['Pages'])
async def registration(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='registration.html',
        context={
            'failed_message': ''
        }
    )


@app.post('/registration', status_code=status.HTTP_201_CREATED, tags=['User'])
async def register(request: Request, firstname: str = Form(...),
                            lastname: str = Form(...),
                            email: str = Form(...),
                            password: str = Form(...)):
    statement = select(User).where(User.email == email)
    result = session.exec(statement).one_or_none()
    new_user = User(first_name = firstname, last_name = lastname, email = email, password = password)
    if result == None:
        session.add(new_user)
        session.commit()
        return templates.TemplateResponse(
            request=request,
            name='main_page.html',
            context={
                'result': answer
            }
        )
    else:
        return templates.TemplateResponse(
            request=request,
            name='registration.html',
            context={
                'failed_message': 'Пользователь с таким email уже существует'
            }
        )
