# Library Statistics Project - Dr. B. B. Hegde First Grade College

A Flask-based web application for searching and managing library statistics at Dr. B. B. Hegde First Grade College, Kundapura.

## Features

- **Interactive Search Interface**: Search through library collections by Title, Author, Department, or Department Code
- **Real-time Suggestions**: Get search suggestions as you type
- **Modern UI**: Beautiful, responsive design using Tailwind CSS
- **MongoDB Integration**: Fast and scalable database backend
- **RESTful API**: Clean API endpoints for search and suggestions

## Project Structure

```
your_project/
│
├── app/
│   ├── __init__.py           # App factory & MongoDB init
│   ├── routes.py             # All routes
│   ├── config.py             # MongoDB & other settings
│   ├── templates/            # HTML templates
│   │   └── index.html
│   └── static/               # CSS, JS, images
│       └── README.md
│
├── env.example               # Environment variables template
├── requirements.txt          # Dependencies
├── run.py                    # Development entry point
├── wsgi.py                   # Production entry point
└── README.md                 # This file
```

## Prerequisites

- Python 3.8 or higher
- MongoDB installed and running
- pip (Python package manager)

## Installation

1. **Clone or download the project files**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   cp env.example .env
   
   # Edit .env with your settings
   # Update SECRET_KEY and MONGO_URI as needed
   ```

5. **Set up MongoDB**
   - Ensure MongoDB is running on your system
   - Create a database named `library_db` (or update MONGO_URI in .env)
   - Optionally, add some sample data to the `books` collection

## Running the Application

### Development Mode
```bash
python run.py
```
The application will be available at `http://localhost:5000`

### Production Mode
```bash
# Using Gunicorn (install with: pip install gunicorn)
gunicorn wsgi:app

# Or using the built-in WSGI server
python wsgi.py
```

## Sample Data Structure

The application expects a MongoDB collection named `books` with documents in this format:

```json
{
  "_id": ObjectId("..."),
  "title": "Book Title",
  "author": "Author Name",
  "department": "Department Name",
  "department_code": "DEPT001"
}
```

## API Endpoints

- `GET /` - Main application page
- `POST /api/search` - Search for books
- `GET /api/suggestions` - Get search suggestions

## Configuration

Key configuration options in `app/config.py`:

- `SECRET_KEY`: Flask secret key for sessions
- `MONGO_URI`: MongoDB connection string
- `DEBUG`: Enable/disable debug mode

## Customization

- **Logo**: Place your college logo as `logo-removebg-preview.png` in the `app/static/` directory
- **Colors**: Modify the Tailwind CSS classes in `index.html` to match your brand colors
- **Search Fields**: Update the search options in the JavaScript code and routes

## Troubleshooting

1. **MongoDB Connection Error**: Ensure MongoDB is running and the connection string is correct
2. **Module Not Found**: Make sure all dependencies are installed with `pip install -r requirements.txt`
3. **Port Already in Use**: Change the port in `run.py` or stop other services using port 5000

## License

This project is created for Dr. B. B. Hegde First Grade College, Kundapura.

## Support

For technical support or questions about this application, please contact the development team. 