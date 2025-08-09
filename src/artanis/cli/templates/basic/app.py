from __future__ import annotations

import uvicorn

from artanis import App

app = App()


async def root() -> dict[str, str]:
    return {"message": "Hello from {{project_name}}!"}


app.get("/", root)

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
