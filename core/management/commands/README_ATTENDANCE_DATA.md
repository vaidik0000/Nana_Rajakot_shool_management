# Attendance Data Generation Tools

This repository includes tools for generating dummy attendance data for students and teachers in the School Management System.

## Features

- Generate realistic attendance records with proper status distributions
- Create data for both students and teachers
- Configurable date ranges
- Skip weekends automatically
- Bulk creation for performance
- Overwrite option for existing data

## Available Tools

### 1. One-time Script (add_dummy_data.py)

This standalone script can be run directly to generate a fixed set of dummy data:

```bash
python add_dummy_data.py
```

The script will:
- Check for existing students and teachers
- Create new students/teachers if needed
- Generate attendance records for a 60-day period

### 2. Django Management Command

A more flexible option is to use the Django management command:

```bash
# Generate 30 days of attendance data (default)
python manage.py generate_attendance_data

# Generate 90 days of attendance data
python manage.py generate_attendance_data --days 90

# Generate 180 days and overwrite existing records in that date range
python manage.py generate_attendance_data --days 180 --overwrite
```

#### Command Options

- `--days`: Number of days to generate data for (default: 30)
- `--overwrite`: Delete existing attendance records in the specified date range before creating new ones

## Data Distribution

The generated data uses realistic weighted distributions:

### Student Attendance:
- Present: 80%
- Absent: 15%
- Late: 3%
- Half Day: 2%

### Teacher Attendance:
- Present: 90%
- Absent: 7%
- Late: 2%
- Half Day: 1%

## Viewing the Data

Once generated, the attendance data will be visible:

1. In the admin interface under Attendance > Attendances and TeacherAttendances
2. In the Attendance Chart on the admin dashboard
3. In the attendance list views

## Using in Development

This data is intended for development and testing purposes. It provides:

- A realistic dataset for testing attendance reports
- Data for visualizing attendance trends
- Material for testing date range filters

## Troubleshooting

If you encounter any issues:

1. Make sure you have students and teachers in the database
2. Check that your database migrations are up to date
3. Verify that the `attendance` app is in your INSTALLED_APPS
4. If getting Unicode errors, ensure all __init__.py files have proper UTF-8 encoding 