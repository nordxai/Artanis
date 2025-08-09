# 1. Project Setup

First, let's create a new directory for our project and set up a virtual environment.

```bash
mkdir artanis-blog-api
cd artanis-blog-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Next, we'll install Artanis and Uvicorn:

```bash
pip install artanis uvicorn
```

Now, create a new file called `main.py` and add the following code:

```python
# main.py
from artanis import App
import uvicorn

app = App()

async def root():
    return {"message": "Welcome to the Blog API!"}

app.get("/", root)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

This is the most basic Artanis application. Let's break it down:

1.  We import the `App` class from `artanis`.
2.  We create an instance of the `App` class.
3.  We define a handler function `root`.
4.  We register the `root` handler for GET requests to the `/` path using `app.get()`.
5.  We use `uvicorn` to run the application.

To run the application, use the following command:

```bash
uvicorn main:app --reload
```

Now, if you open your browser to `http://127.0.0.1:8000`, you should see the message `{"message":"Welcome to the Blog API!"}`.

In the next section, we'll add more routes to our API.
