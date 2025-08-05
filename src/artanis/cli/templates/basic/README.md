# {{project_name}}

{{project_description}}

This project was generated using the Artanis CLI tool and demonstrates the basic features of the Artanis web framework.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

The server will start at `http://127.0.0.1:8000`

## Available Endpoints

- **GET** `/` - Welcome message with API information
- **GET** `/health` - Health check endpoint
- **GET** `/hello/{name}` - Personalized greeting (replace `{name}` with any name)
- **POST** `/echo` - Echo the request body back to the client

## Testing the API

### Using curl

```bash
# Welcome message
curl http://127.0.0.1:8000/

# Health check
curl http://127.0.0.1:8000/health

# Personalized greeting
curl http://127.0.0.1:8000/hello/world

# Echo endpoint (POST with JSON)
curl -X POST http://127.0.0.1:8000/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from {{project_name}}!"}'
```

### Using your browser

Open your browser and visit:
- http://127.0.0.1:8000/
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/hello/yourname

## Project Structure

```
{{project_name}}/
├── app.py              # Main application file
├── requirements.txt    # Project dependencies
├── README.md          # This file
└── .gitignore         # Git ignore rules
```

## Key Features Demonstrated

1. **Basic Routing**: GET and POST routes with path parameters
2. **Request Handling**: JSON request body parsing
3. **Response Formatting**: Structured JSON responses
4. **Error Handling**: Basic error handling for invalid JSON
5. **Development Server**: Hot reload during development

## Next Steps

Now that you have a basic Artanis application running, you can:

1. **Add more routes** - Create additional endpoints for your API
2. **Add middleware** - Implement authentication, logging, CORS, etc.
3. **Add validation** - Validate request data using middleware
4. **Connect a database** - Integrate with your preferred database
5. **Add tests** - Write unit tests for your endpoints
6. **Deploy** - Deploy your application to production

## Learn More

- [Artanis Documentation](https://github.com/nordxai/artanis)
- [ASGI Specification](https://asgi.readthedocs.io/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

## License

This project is licensed under the MIT License.
