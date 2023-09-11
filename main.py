from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
import uvicorn
from database.db import supa

app = FastAPI()

# Static folder for css/media
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    try:
        data = supa.auth.get_user()
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "title": "Logged In!", "data": data},
        )
    except Exception as e:
        print("Error: ", e)
        return RedirectResponse(url="/auth", status_code=302)


# Signup
@app.get("/auth", response_class=HTMLResponse)
async def auth(request: Request):
    return templates.TemplateResponse(
        "auth.html", {"request": request, "title": "Not logged in"}
    )


@app.post("/signup", response_class=HTMLResponse)
async def signup(request: Request, email: str = Form(...), password: str = Form(...)):
    if email and password:
        print("Signing up...")
        try:
            supa.auth.sign_up({"email": email, "password": password})
            return templates.TemplateResponse(
                "partials/auth/signup/signup_success.html",
                {"request": request, "email": email, "password": password},
            )
        except Exception as e:
            print("Error: ", e)
            return templates.TemplateResponse(
                "partials/auth/signup/signup_fail.html", {"request": request}
            )
    else:
        return templates.TemplateResponse(
            "partials/auth/signup/signup_fail.html", {"request": request}
        )


@app.post("/signin", response_class=HTMLResponse)
async def signin(request: Request, email: str = Form(...), password: str = Form(...)):
    if email and password:
        print("Signing in...")
        print("Email: ", email)
        try:
            supa.auth.sign_in_with_password({"email": email, "password": password})
            return RedirectResponse(url="/")

        except Exception as e:
            print("Error: ", e)
            return templates.TemplateResponse(
                "partials/auth/signin/signin_fail.html", {"request": request}
            )

    else:
        return templates.TemplateResponse(
            "partials/auth/signin/signin_fail.html", {"request": request}
        )


@app.get("/get_user_profile", response_class=HTMLResponse)
async def get_user_profile(request: Request):
    try:
        data = supa.auth.get_user()

        return templates.TemplateResponse(
            "partials/auth/profile/profile.html", {"request": request, "data": data}
        )

    except Exception as e:
        print("Error: ", e)
        return templates.TemplateResponse(
            "partials/auth/profile/profile_fail.html", {"request": request}
        )


# Signout
@app.post("/signout", response_class=HTMLResponse)
async def signout(request: Request):
    supa.auth.sign_out()
    return RedirectResponse(url="/auth", status_code=302)


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
