# LeaveFlow — Employee Leave Management System

A production-minded Django employee leave management system with employee registration, secure phone + 4-digit PIN authentication, leave balances, approval workflow, profile management and responsive Bootstrap UI.

## What was improved

### Authentication & accounts
- Employee self-registration page.
- Phone number + 4-digit PIN login.
- PIN validation and secure Django password hashing.
- Legacy plaintext PINs are converted to password hashes by migration `users/0002_upgrade_user.py`.
- Change PIN flow.
- Logout uses POST + CSRF protection.
- Employee profile and profile editing.
- Automatic employee ID assignment for newly registered employees.

### Leave workflow
- Employee dashboard with leave statistics and balances.
- Apply leave with date validation.
- Past-date protection.
- Duplicate/overlapping pending or approved leave protection.
- Balance validation before submitting.
- Leave status starts automatically as Pending when an employee submits a request.
- Employees cannot create, edit, approve, reject, or otherwise change the leave status.
- Employees can only submit leave and view the current read-only status.
- Only administrators can approve or reject requests from the dedicated Admin Dashboard.
- LeaveRequest status is non-editable in the Django admin as an additional safeguard.
- Admin approve/reject actions use POST + CSRF protection.
- Balance is deducted only when an admin approves a request.
- Prevents approving or rejecting a request twice.

### UI
- Clean responsive Bootstrap 5 layout.
- Mobile-friendly navigation and tables.
- Consistent cards, status badges, forms and spacing.
- Separate employee and admin dashboards.
- No inline page-specific CSS required.

### Deployment readiness
- Gunicorn configuration.
- WhiteNoise static-file serving.
- `DATABASE_URL` support for PostgreSQL-compatible cloud databases.
- Production settings enabled when `DEBUG=False`.
- `.env.example` included.

## Tech stack

- Python 3.12
- Django 5.2
- SQLite for local development
- PostgreSQL-compatible database for production
- Bootstrap 5
- WhiteNoise
- Gunicorn
- django-crispy-forms

---

# 1. Run locally on Windows

Open PowerShell and go to the folder that contains `manage.py`.

```powershell
cd path	o\employee_leave_management_system_full
```

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it:

```powershell
.env\Scripts\Activate.ps1
```

If PowerShell blocks activation, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.env\Scripts\Activate.ps1
```

Install packages:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run migrations:

```powershell
python manage.py makemigrations
python manage.py migrate
```

Check the project:

```powershell
python manage.py check
```

Create an admin account:

```powershell
python manage.py createsuperuser
```

The project asks for a phone number and PIN/password according to the custom user model. Use a 4-digit PIN if you want to use the normal phone + PIN login.

Start the server:

```powershell
python manage.py runserver
```

Open:

- Home: http://127.0.0.1:8000/
- Employee login: http://127.0.0.1:8000/accounts/login/
- Employee registration: http://127.0.0.1:8000/accounts/register/
- Employee dashboard: http://127.0.0.1:8000/leaves/dashboard/
- Admin dashboard: http://127.0.0.1:8000/leaves/admin-dashboard/
- Django admin: http://127.0.0.1:8000/admin/

## Test flow

1. Open Register.
2. Create an employee account.
3. Sign in with phone + 4-digit PIN.
4. Check the dashboard and initial leave balance.
5. Apply for leave.
6. Sign out.
7. Sign in as admin.
8. Open Admin Dashboard.
9. Approve or reject the request from the Admin Dashboard.
10. Sign back in as the employee and verify the read-only status and balance.

### Approval responsibility
The employee never controls the approval status. Submitting a request automatically creates it as **Pending**. Only an authenticated administrator can change it to **Approved** or **Rejected** using the Admin Dashboard. The employee screens only display the result.

New employees receive an initial balance of:
- Casual: 12 days
- Sick: 10 days
- Other: 5 days

These values can be changed in `users/views.py` and `leaves/views.py` according to the organization's policy.

---

# 2. Important security note

The previous version had a `pin` database field containing the PIN. The revised application does **not** use that field for authentication.

Authentication uses Django's password hashing through:

```python
user.set_password(pin)
```

The migration also converts legacy 4-digit PINs in an existing database to password hashes and clears the old PIN field.

For production, always set a strong `SECRET_KEY` and `DEBUG=False`.

---

# 3. Production environment variables

Copy `.env.example` to `.env` for local environment configuration.

Example:

```env
SECRET_KEY=your-long-random-secret
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=your-postgresql-database-url
SECURE_SSL_REDIRECT=True
```

Do not commit `.env` to GitHub.

---

# 4. Deploy to Railway

## A. Push the revised project to GitHub

Create a new GitHub repository, for example:

`employee-leave-management-system`

From the project folder:

```powershell
git init
git add .
git commit -m "Upgrade employee leave management system"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/employee-leave-management-system.git
git push -u origin main
```

## B. Create Railway project

1. Sign in to Railway.
2. Create a new project.
3. Choose **Deploy from GitHub Repo**.
4. Select the repository.
5. Railway should detect the `Procfile`.
6. Deploy the service.

The Procfile is:

```text
web: gunicorn leave_mgmt.wsgi:application
```

## C. Add a PostgreSQL database

For production, do not rely on the included SQLite database because a cloud service filesystem may not be persistent.

In Railway:

1. Open the project.
2. Add a PostgreSQL service/database.
3. Make sure the application receives the database connection as `DATABASE_URL`.
4. Redeploy the application.

The settings automatically use `DATABASE_URL` when it is available.

## D. Add environment variables

Add:

```text
SECRET_KEY=<strong-random-secret>
DEBUG=False
ALLOWED_HOSTS=<your-railway-domain>
SECURE_SSL_REDIRECT=True
```

If Railway provides a PostgreSQL connection variable under a different name, map it to:

```text
DATABASE_URL
```

## E. Run migrations

After deployment, run:

```bash
python manage.py migrate
```

If your deployment platform provides a shell, execute the command there.

Create the production admin:

```bash
python manage.py createsuperuser
```

## F. Collect static files

Run:

```bash
python manage.py collectstatic --noinput
```

WhiteNoise serves the collected files.

## G. Generate the public domain

Use your hosting provider's **Networking / Domains / Generate Domain** option and open the generated HTTPS URL.

---

# 5. Deploy to Render

The project is also compatible with Render.

Recommended settings:

**Build Command**

```bash
pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

**Start Command**

```bash
gunicorn leave_mgmt.wsgi:application
```

Set environment variables:

```text
DEBUG=False
SECRET_KEY=<strong-random-secret>
ALLOWED_HOSTS=<your-render-domain>
DATABASE_URL=<postgresql-connection-string>
SECURE_SSL_REDIRECT=True
```

For production, create/use PostgreSQL rather than the local SQLite file.

---

# 6. Recommended Git files

Do not upload your local virtual environment or cache files.

The repository should contain the application source, migrations, templates, static files, `requirements.txt`, `Procfile`, `.env.example`, and README.

It should NOT contain:

```text
venv/
__pycache__/
*.pyc
.env
```

The included `.gitignore` should be used before pushing to GitHub.

---

# 7. Future enhancements

For a larger company deployment, the next useful additions would be:

- HR-managed employee accounts and invitation links.
- Forgot PIN / password-reset flow using email or OTP.
- Half-day leave support.
- Holiday calendar.
- Weekend exclusion.
- Manager-specific approval hierarchy.
- Email notifications for submitted/approved/rejected requests.
- Employee directory.
- Export reports to Excel/PDF.
- Audit log for administrative actions.
- Role-based permissions beyond employee/admin.
- Automated annual leave-balance allocation.
- PostgreSQL indexes and pagination for large datasets.
