
# API Endpoints

## Auth
POST /auth/login
POST /auth/validate

## Scheduling
POST /schedules/create
GET /schedules/{id}

## Tasks
POST /tasks/create
POST /tasks/complete

## Reminders
POST /reminders/create

## Messaging
POST /messages/send

## Reporting
GET /reports/cashflow

All endpoints:
- validate input
- emit events
- log to audit
