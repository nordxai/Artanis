# {{project_name}}

{{project_description}}

This project was generated using the Artanis CLI tool and demonstrates the basic features of the Artanis web framework.

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### 1. Set up your environment (recommended)

Create a virtual environment to isolate your project dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The server will start at `http://127.0.0.1:8000`

### 4. Verify it's working

Open your browser and visit `http://127.0.0.1:8000` - you should see a welcome message with API information.

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

## Troubleshooting

### Common Issues

**"Command not found" errors:**
- Make sure you have Python 3.8+ installed: `python --version`
- Try using `python3` instead of `python` on some systems

**"Permission denied" errors:**
- On Unix systems, ensure you have the right permissions
- Try using `sudo` if needed for global installations (not recommended for development)

**Virtual environment issues:**
- Make sure the virtual environment is activated (you should see `(venv)` in your terminal prompt)
- If activation doesn't work, try recreating the virtual environment

**Port already in use:**
- If port 8000 is busy, edit `app.py` and change the port number in the `uvicorn.run()` call
- Or kill the process using the port: `lsof -ti:8000 | xargs kill -9` (Unix/macOS)

**Module import errors:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're using the correct Python environment

### Getting Help

If you encounter issues:
1. Check the [Artanis GitHub Issues](https://github.com/nordxai/artanis/issues)
2. Make sure you're using a supported Python version (3.8+)
3. Try recreating your virtual environment
4. Verify all dependencies are correctly installed

## Learn More

- [Artanis Documentation](https://github.com/nordxai/artanis)
- [ASGI Specification](https://asgi.readthedocs.io/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

## License

This project is licensed under the MIT License.
