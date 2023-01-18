from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.models import mongodb
from app.models.book import SimpleModel

BASE_DIR = Path(__file__).resolve().parent


app = FastAPI()  # fastAPI에는 app을 싱글톤 패턴을 사용해서 하나 찍어냄
templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)  # templates에는 해당하는 html 파일의 위치를 지정함

"""
app.get은 하나의 라우터
여기서 라우터는 요청을 받고 해당하는 logic을 따라서 응답을 해주는 것
response_class=HTMLResponse: response를 해줬을 때 response 타입을 htmlResponse로 지정한 것
"""


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    # tutorial1. 임의의 정보 넣기
    # 'book'이라는 이름으로 BookModel을 인스턴스로 찍음 (테스트용 데이터)
    """
    # book = BookModel(keyword="자바", publisher="BJPublic", price=1200, image="me.png")
    # # db에 저장. await을 붙인 이유: save라는 함수가 async(코루틴) 함수기 때문. = 비동기적으로 작동함
    # print(await mongodb.engine.save(book))  # db에 저장되는 정보를 print로 찍음

    """
    templeates 폴더 안에 TemplateResponse 클래스가 있는데, 클래스를 사용해서 리턴함
    첫 번째 인자는 index.html, 두 번째 인자는 보내고 싶은 데이터
    """
    return templates.TemplateResponse(
        "./index.html",
        {"request": request, "title": "Python is So Easy"},
    )


@app.get("/user", response_class=HTMLResponse)
async def search(request: Request, q: str):
    keyword = request.query_params.get("q")  # 쿼리에서 검색어 추출
    # number = request.query_params.get("n")
    # keyword = q  # 쿼리에서 검색어 추출
    # number = n

    simple_model = SimpleModel(
        keyword=keyword,
    )

    print(simple_model)
    await mongodb.engine.save(simple_model)  # db에 저장

    return templates.TemplateResponse(
        "./index.html",
        {"request": request, "title": "Python is So Easy"},
    )


@app.get("/bring", response_class=HTMLResponse)
async def bring(request: Request):
    data = mongodb.engine.find(SimpleModel)
    print(data)

    simples = await mongodb.engine.find(SimpleModel)
    context = {"request": request, "simples": simples}

    # 값 정제...
    search = "SimpleModel(id=ObjectId"
    for i, word in enumerate(simples):
        if search in word:
            print(">> modify: " + word)
            simples[i] = word.strip(search)

    print(simples)

    return templates.TemplateResponse("index.html", context=context)
    # return templates.TemplateResponse("index.html", context=context)


# app이 처음 실행될 때 이 함수(on_app_start)가 실행됨
@app.on_event("startup")
def on_app_start():
    """before app starts"""
    mongodb.connect()


# 서버가 shutdown이 됐을 때 on_app_shutdown이 실행됨
@app.on_event("shutdown")
async def on_app_shutdown():
    print("bye server")
    """after app shutdown"""
    mongodb.close()
