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
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "Home"}
    )


# Auth
@app.get("/auth", response_class=HTMLResponse)
async def auth(request: Request):
    return templates.TemplateResponse(
        "auth.html", {"request": request, "title": "Please Sign In or Sign Up"}
    )


# Signup
@app.get("/auth/signup", response_class=HTMLResponse)
async def signup_form(request: Request):
    return templates.TemplateResponse(
        "partials/auth/signup/signup.html", {"request": request}
    )


@app.post("/signup", response_class=HTMLResponse)
async def signup(request: Request, email: str = Form(...), password: str = Form(...)):
    if email and password:
        print("Signing up...")
        try:
            print("Email: ", email)
            print("Password: ", password)
            user = supa.auth.sign_up({"email": email, "password": password})
            return templates.TemplateResponse(
                "partials/auth/signup/signup_success.html",
                {"request": request, "email": user},
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


# Signin
@app.get("/auth/signin", response_class=HTMLResponse)
async def signin_form(request: Request):
    return templates.TemplateResponse(
        "partials/auth/signin/signin.html", {"request": request}
    )


@app.post("/signin", response_class=HTMLResponse)
async def signin(request: Request, email: str = Form(...), password: str = Form(...)):
    if email and password:
        print("Signing in...")
        print("Email: ", email)
        try:
            supa.auth.sign_in_with_password({"email": email, "password": password})
            # If profile is not complete, redirect to /profile
            user = supa.auth.get_user()
            profile = (
                supa.table("profile")
                .select("*")
                .eq("id", user.user.id)
                .single()
                .execute()
            )
            if (
                profile.data["display_name"]
                and profile.data["first_name"]
                and profile.data["last_name"]
                and profile.data["email"] is not None
            ):
                print("Profile is not empty.")
                response = templates.TemplateResponse(
                    "partials/auth/signin/signin_success.html",
                    {"request": request, "email": email},
                )
                response.headers["HX-Redirect"] = "/"
                return response
            else:
                # If profile is empty, show complete profile page
                response = templates.TemplateResponse(
                    "partials/auth/profile/profile.html",
                    {"request": request, "email": email},
                )
                response.headers["HX-Redirect"] = "/profile"
                return response

        except Exception as e:
            print("Error: ", e)
            return templates.TemplateResponse(
                "partials/auth/signin/signin_fail.html", {"request": request}
            )

    else:
        return templates.TemplateResponse(
            "partials/auth/signin/signin_fail.html", {"request": request}
        )


# Complete Profile
@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    try:
        user = supa.auth.get_user()
        print(user.user.email)
        if user.user.id is not None:
            return templates.TemplateResponse(
                "partials/auth/profile/profile.html", {"request": request}
            )
        else:
            return templates.TemplateResponse(
                "partials/auth/profile/profile_fail.html", {"request": request}
            )
    except Exception as e:
        print("Error: ", e)
        response = templates.TemplateResponse(
            "partials/auth/profile/profile_fail.html", {"request": request}
        )
        response.headers["HX-Redirect"] = "/auth"
        return response


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


@app.post("/complete_profile", response_class=HTMLResponse)
async def complete_profile(
    request: Request,
    display_name: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
):
    if display_name and first_name and last_name:
        print("Completing prorfile...")
        user = supa.auth.get_user()
        try:
            # Update profile for matching user id
            supa.table("profile").upsert(
                {
                    "id": user.user.id,
                    "display_name": display_name,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                }
            ).execute()
            return templates.TemplateResponse(
                "partials/auth/profile/profile_success.html",
                {
                    "request": request,
                    "display_name": display_name,
                    "first_name": first_name,
                    "last_name": last_name,
                },
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
    response = RedirectResponse(url="/", status_code=200)
    response.headers["HX-Redirect"] = "/"
    return response


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
