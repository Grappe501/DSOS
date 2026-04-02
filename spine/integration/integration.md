# INTEGRATION Service

## Purpose
External I/O

## Uses Tables
-

## Consumes Events
integration.failed

## Emits Events
-

## API Endpoints
POST /integrate

## Internal Flow
ingest

## Failure Handling
- retry queue
- dead-letter queue
- audit log

## Tests
- unit
- integration via event bus
