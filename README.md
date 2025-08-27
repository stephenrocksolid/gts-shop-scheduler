# GTS Rental Scheduler

A Django-based rental scheduling system with a modern UI powered by TailwindCSS and HTMX.

## Prerequisites

- Python 3.x
- Node.js and npm
- PostgreSQL

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/joshuarocksolid/gts-rental-scheduler.git
cd gts-rental-scheduler
```

### 2. Python Environment Setup

Create and activate a virtual environment:

```bash
# Windows
python -m venv env
env\Scripts\activate

# Unix/MacOS
python -m venv env
source env/bin/activate
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

### 3. JavaScript Dependencies

Install Node.js dependencies:
```bash
npm install
```

Build the CSS:
```bash
# For one-time build
npm run build

# For development with watch mode
npm run watch
```

### 4. Environment Variables

Create a `.env` file in the root directory with the following variables:
```env
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://user:password@localhost:5432/database_name
```

### 5. Database Setup

```bash
python manage.py migrate
python manage.py createsuperuser
```

## Running the Application

1. Start the Django development server:
```bash
python manage.py runserver
```

2. In a separate terminal, run the TailwindCSS watcher for development:
```bash
npm run watch
```

3. Access the application at `http://localhost:8000`

## Key Features

- Rental scheduling and management
- Modern UI with TailwindCSS
- Interactive features using HTMX
- PostgreSQL database backend
- Excel file handling with pandas
- PDF generation with WeasyPrint

## Project Structure

- `rental_scheduler/` - Main Django app
- `static/` - Static files (CSS, JS)
- `templates/` - HTML templates
- `requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies

## Development

- CSS styling is managed through TailwindCSS
- Run `npm run watch` during development to automatically compile CSS changes
- Python dependencies should be added to `requirements.txt`
- JavaScript dependencies should be managed through `package.json`

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Submit a pull request

## License

ISC License 