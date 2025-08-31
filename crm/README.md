# ALX Backend GraphQL CRM

A Django-based CRM application with GraphQL, cron jobs, and Celery for task automation, including weekly report generation.

<details>
<summary>Click to view full project documentation</summary>

## Project Overview

This project implements a CRM system with GraphQL endpoints, task automation using `django-crontab` and Celery, and periodic reporting. Key features include customer cleanup, order reminders, stock updates, and a weekly CRM report summarizing customers, orders, and revenue.

## Features

- **GraphQL API**: Provides endpoints for querying and mutating CRM data.
- **Cron Jobs**: Scheduled tasks for customer cleanup, order reminders, and stock updates using `django-crontab`.
- **Celery Tasks**: Asynchronous weekly CRM report generation using Celery and `django-celery-beat`.
- **Logging**: Logs task outputs for monitoring and debugging.

## Prerequisites

- Python 3.8 or higher
- Django 4.2 or higher
- Celery 5.3 or higher
- Redis 6.0 or higher
- RabbitMQ 3.8 or higher (for previous tasks)
- Git for version control

## Setup Instructions

### 1. Clone the Repository

Clone the project repository and navigate to the project directory:

```bash
git clone <alx-backend-graphql_crm_repo_url>
cd alx-backend-graphql_crm
```

###  2. Install Redis and Dependencies

Create a virtual environment and install required packages:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Install and Start Redis
Install Redis and ensure it’s running:
```bash
sudo apt-get install redis-server  # On Ubuntu
sudo systemctl enable redis
sudo systemctl start redis
```
Verify Redis status:
```bash
redis-cli ping
```
Expected output: PONG


### 4. Install and Start RabbitMQ (for previous tasks)
Install RabbitMQ and ensure it’s running:
```bash
sudo apt-get install rabbitmq-server  # On Ubuntu
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server
```
Verify RabbitMQ status:
```bash
sudo systemctl status rabbitmq-server
```


 ### 5. Apply Database Migrations

Run migrations to set up the database:
```bash
python manage.py migrate
```
### 6. Start Celery Worker

Run the Celery worker to process background tasks:
```bash
celery -A crm worker -l info
```

### 7. Start Celery Beat
Run Celery Beat to schedule periodic tasks:
```bash
celery -A crm beat -l info
```
### 8. Start Django Development Server
Start the Django server:
```bash
python manage.py runserver
```


### 9. Veryfy Logs
Check the report logs:
```bash
cat /tmp/crmreportlog.txt
```