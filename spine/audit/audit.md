# AUDIT Service

## Purpose
Logs

## Uses Tables
audit_logs

## Consumes Events
all

## Emits Events
-

## API Endpoints
internal

## Internal Flow
write log

## Failure Handling
- retry queue
- dead-letter queue
- audit log

## Tests
- unit
- integration via event bus
