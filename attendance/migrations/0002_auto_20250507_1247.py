from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('attendance', '0001_initial'),  # This is correct based on your migration history
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS attendance_teacherattendance (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                status VARCHAR(20) NOT NULL,
                remarks TEXT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
                recorded_by_id INTEGER NULL REFERENCES auth_user(id) ON DELETE SET NULL,
                teacher_id INTEGER NOT NULL REFERENCES school_teachers_teacher(id) ON DELETE CASCADE
            );
            """,
            "DROP TABLE IF EXISTS attendance_teacherattendance;"
        )
    ]