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
if answer == []:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


ustatement = select(Current)
result = session.exec(ustatement).all()
info = result[0].id
print(info)
if info == 0:
    CURRENT_USER = None
else:
    CURRENT_USER = info


@app.get('/', response_model=Hotel, tags=['Pages'])
async def show_hotels(request: Request):
    global CURRENT_USER
    if CURRENT_USER == None:
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
            name='main_page_logged.html',
            context={
                'result': answer, 'user_id': CURRENT_USER
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


@app.get('/profile/{user_id}', response_model=User, tags=['User'])
async def profile(request: Request, user_id: int):
    global CURRENT_USER
    if CURRENT_USER == None:
        return RedirectResponse('/')
    statement = select(User).where(User.id == CURRENT_USER)
    result = session.exec(statement).all()
    fn = result[0].first_name
    ln = result[0].last_name
    email = result[0].email
    return templates.TemplateResponse(
        request=request,
        name='profile.html',
        context={'firstname': fn, 'lastname': ln, 'email': email}
    )


@app.get('/login', response_model=User, tags=['User'])
async def login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='login.html',
        context={
            'failed_message': ''
        }
    )


@app.get('/hotel/{hotel_id}', response_model=Hotel, tags=['Hotel'])
async def get_hotel(request: Request, hotel_id: int):
    global CURRENT_USER
    statement = select(Hotel).where(Hotel.id == hotel_id)
    result = session.exec(statement).all()
    name = result[0].name
    country = result[0].country
    town = result[0].town
    rate = result[0].rate
    price = result[0].price_per_night
    if CURRENT_USER != None:
        return templates.TemplateResponse(
            request=request,
            name='hotel_page_logged.html',
            context={'hotel_name': name, 'hotel_country': country, 'hotel_town': town, 'rate': rate, 'price': price}
        )
    else:
        return templates.TemplateResponse(
            request=request,
            name='hotel_page.html',
            context={'hotel_name': name, 'hotel_country': country, 'hotel_town': town, 'rate': rate, 'price': price}
        )


@app.get('/books', response_model=Hotel)
async def get_contracts(request: Request):
    global CURRENT_USER
    none_label = ''
    statement = select(Contract).where(Contract.user_id == CURRENT_USER)
    result = session.exec(statement).all()
    if result == []:
        none_label = 'Вы ещё не забронировали отель'
    return templates.TemplateResponse(
        request=request,
        name='contracts.html',
        context={
            'result': result, 'none_label': none_label, 'user_id': CURRENT_USER
        }
    )


@app.post('/books/{id}')
async def cancel(request: Request, id: int):
    global CURRENT_USER
    none_label = ''
    statement = select(Contract).where(Contract.hotel_id == id).where(Contract.user_id == CURRENT_USER)
    result = session.exec(statement).all()
    book = result[0]
    session.delete(book)
    session.commit()
    statement = select(Contract).where(Contract.user_id == CURRENT_USER)
    new_result = session.exec(statement).all()
    if new_result == []:
        none_label = 'Вы ещё не забронировали отель'
    return templates.TemplateResponse(
        request=request,
        name='contracts.html',
        context={
            'result': new_result, 'none_label': none_label, 'user_id': CURRENT_USER
        }
    )

@app.post('/hotel/{hotel_id}')
async def make_a_book(request: Request, hotel_id: int, nights: int = Form(...)):
    global CURRENT_USER
    fail = ''
    check = select(Contract).where(Contract.hotel_id == hotel_id).where(Contract.user_id == CURRENT_USER)
    check_result = session.exec(check).all()
    if check_result == []:
        statement = select(Hotel).where(Hotel.id == hotel_id)
        result = session.exec(statement).all()
        price_per_night = result[0].price_per_night
        total = price_per_night * nights
        name = result[0].name
        new_contract = Contract(user_id=CURRENT_USER, hotel_id=hotel_id, hotel_name=name, nights=nights,
                                total_price=total)
        session.add(new_contract)
        session.commit()
        return templates.TemplateResponse(
            request=request,
            name='main_page_logged.html',
            context={
                'result': answer, 'user_id': CURRENT_USER, 'failed': fail
            }
        )
    else:
        fail = 'Вы уже оформили бронь на этот отель'
        return templates.TemplateResponse(
            request=request,
            name='main_page_logged.html',
            context={
                'result': answer, 'user_id': CURRENT_USER, 'failed': fail
            }
        )


@app.post('/login', status_code=status.HTTP_201_CREATED, tags=['User'])
async def login_user(request: Request, email: str = Form(...),
                     password: str = Form(...)):
    global CURRENT_USER
    statement = select(User).where(User.email == email)
    result = session.exec(statement).all()
    if result == []:
        return templates.TemplateResponse(request=request, name='login.html',
                                          context={'failed_message': 'Неверный логин или пароль'})
    if result[0].email == email and result[0].password == password:
        CURRENT_USER = result[0].id
        statement1 = select(Current)
        result1 = session.exec(statement1).one()
        result1.id = CURRENT_USER
        session.add(result1)
        session.commit()
        session.refresh(result1)
        print(CURRENT_USER)
        return templates.TemplateResponse(
            request=request,
            name='main_page_logged.html',
            context={
                'result': answer, 'user_id': CURRENT_USER
            }
        )
    else:
        return templates.TemplateResponse(request=request, name='login.html', context={'failed_message': 'Неверный логин или пароль'})

@app.get('/quit', response_class=RedirectResponse, tags=['User'])
async def quit(request: Request):
    global CURRENT_USER
    CURRENT_USER = None
    statement = select(Current)
    result = session.exec(statement).one()
    result.id = 0
    session.add(result)
    session.commit()
    session.refresh(result)
    return RedirectResponse('/')

