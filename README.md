# Airtasker Bot Manager

A simplified Flask application for managing automated Airtasker comments.

## Features

- Manage Airtasker accounts
- Define target cities and radius
- Create and store message templates
- Schedule automated commenting
- View detailed activity logs
- Simple JSON-based storage (no database required)
- Selenium-based automation with CAPTCHA solving

## Project Structure

```
.
├── app/                    # Application package
│   ├── __init__.py         # App factory
│   ├── automations/        # Automation scripts
│   │   ├── main.py         # Main selenium automation
│   │   └── comments.py     # Comment automation
│   ├── static/             # Static files (CSS, JS)
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── js/
│   │   │   └── scripts.js
│   │   └── uploads/        # Image uploads directory
│   ├── templates/          # Jinja2 templates
│   │   ├── base.html       # Base template
│   │   ├── accounts.html   # Account management
│   │   ├── cities.html     # City management
│   │   ├── dashboard.html  # Main dashboard
│   │   ├── logs.html       # Activity logs
│   │   ├── messages.html   # Message templates
│   │   └── schedules.html  # Scheduling
│   ├── data_manager.py     # JSON data storage
│   ├── forms.py            # Form definitions
│   ├── routes.py           # Route handlers
│   └── tasks.py            # Background task handling
├── config.py               # Configuration settings
├── data/                   # JSON data storage directory
├── run.py                  # Application entry point
├── requirements.txt        # Project dependencies
├── .env                    # Environment variables (optional)
└── README.md               # This documentation
```

## Getting Started

### Prerequisites

- Python 3.7 or later
- Chrome browser (for Selenium automation)

### Installation

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/airtasker-bot.git
   cd airtasker-bot
   ```

2. Create a virtual environment:

   ```
   python -m venv venv
   ```

3. Activate the virtual environment:

   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

4. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

5. Run the application:

   ```
   python run.py
   ```

   Or with Flask:

   ```
   export FLASK_APP=run.py
   export FLASK_ENV=development
   flask run
   ```

6. Access the application at `http://localhost:5000`

## Configuration

The application uses a simple JSON-based storage system that doesn't require a database. All data is stored in JSON files in the `data/` directory.

### Environment Variables

You can customize the application by creating a `.env` file:

```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
CAPSOLVER_API_KEY=your-capsolver-api-key
```

## Usage

1. **Add Accounts**: Create accounts with your Airtasker login credentials
2. **Define Cities**: Add cities where you want to comment
3. **Create Messages**: Write template messages to post on tasks
4. **Start Bot**: From the dashboard, select an account, city, and message to start commenting

## Deployment

For production deployment, you can use Gunicorn or Waitress:

```
# Using Gunicorn (Linux/Mac)
gunicorn -w 2 -b 0.0.0.0:5000 run:app

# Using Waitress (Windows/Mac/Linux)
waitress-serve --port=5000 run:app
```

### Google Cloud Platform Deployment

To deploy this application to Google Cloud Platform's App Engine:

1. Install the Google Cloud SDK from [cloud.google.com/sdk](https://cloud.google.com/sdk/docs/install)

2. Authenticate with Google Cloud:

   ```
   gcloud auth login
   ```

3. Create a new project (or select an existing one):

   ```
   gcloud projects create [PROJECT_ID] --name="Airtasker Automation"
   gcloud config set project [PROJECT_ID]
   ```

4. Deploy the application:

   ```
   gcloud app deploy
   ```

5. Access your application:
   ```
   gcloud app browse
   ```

**Note**: This deployment method requires billing to be enabled on your GCP project. The app.yaml file in this repository is configured for a basic F2 instance which should be sufficient for most use cases.

### Docker Deployment

The repository includes a Dockerfile for containerized deployment:

1. Build the Docker image:

   ```
   docker build -t airtasker-automation .
   ```

2. Run the container:

   ```
   docker run -d -p 8080:8080 --name airtasker-bot airtasker-automation
   ```

3. Access the application at `http://localhost:8080`

For Google Cloud Run deployment with Docker:

```
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/[PROJECT_ID]/airtasker-automation

# Deploy to Cloud Run
gcloud run deploy --image gcr.io/[PROJECT_ID]/airtasker-automation --platform managed
```

## License

This project is for private use only.

## Notes on CAPTCHA Solving

The application uses the CapSolver extension for solving CAPTCHA challenges. You'll need a valid API key from [CapSolver](https://capsolver.com/) to use this functionality. Set it in the `.env` file as `CAPSOLVER_API_KEY`.
