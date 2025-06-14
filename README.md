# Project Management System

A Flask-based project management system that allows project managers to create and manage projects, assign engineers, and monitor project progress through various types of reports.

## Features

- User authentication with role-based access (Project Manager/Engineer)
- Project creation and management
- Engineer account creation and project assignment
- Four types of project reports:
  - Progress Reports
  - Damage Reports
  - Bills Reports
  - Supply Reports
- Photo upload support for all reports
- Responsive web interface

## Requirements

- Python 3.7+
- Flask and its dependencies (listed in requirements.txt)
- SQLite database

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd project-management-system
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python app.py
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Register as a Project Manager:
   - Click "Register"
   - Fill in your details
   - Check the "Register as Project Manager" box
   - Submit the form

4. As a Project Manager, you can:
   - Create new projects
   - Create engineer accounts
   - Assign engineers to projects
   - View all project reports

5. Engineers can:
   - Log in with their credentials
   - View assigned projects
   - Submit various types of reports with photos

## Security Notes

- Change the `SECRET_KEY` in `app.py` before deploying to production
- Implement proper password policies in production
- Consider using a more robust database system for production
- Implement proper file upload restrictions and validation
- Add rate limiting and other security measures

## File Structure

```
project-management-system/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Custom styles
│   ├── js/
│   │   └── main.js       # Client-side JavaScript
│   └── uploads/          # Uploaded photos
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── manager_dashboard.html    # Project manager dashboard
│   └── engineer_dashboard.html   # Engineer dashboard
└── README.md             # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 