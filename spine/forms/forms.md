# FORMS Service

## Purpose
Data capture

## Uses Tables
-

## Consumes Events
-

## Emits Events
workflow.started

## API Endpoints
POST /forms

## Internal Flow
validate

## Failure Handling
- retry queue
- dead-letter queue
- audit log

## Tests
- unit
- integration via event bus
