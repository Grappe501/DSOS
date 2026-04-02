# REMINDER Service

## Purpose
Timers

## Uses Tables
reminders

## Consumes Events
task.created

## Emits Events
reminder.triggered

## API Endpoints
POST /reminders/create

## Internal Flow
schedule → trigger

## Failure Handling
- retry queue
- dead-letter queue
- audit log

## Tests
- unit
- integration via event bus
