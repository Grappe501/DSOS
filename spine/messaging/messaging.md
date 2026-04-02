# MESSAGING Service

## Purpose
Notifications

## Uses Tables
messages

## Consumes Events
reminder.triggered

## Emits Events
message.sent

## API Endpoints
POST /messages/send

## Internal Flow
send → confirm

## Failure Handling
- retry queue
- dead-letter queue
- audit log

## Tests
- unit
- integration via event bus
