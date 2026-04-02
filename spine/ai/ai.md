# AI Service

## Purpose
AI layer

## Uses Tables
-

## Consumes Events
-

## Emits Events
-

## API Endpoints
POST /ai/query

## Internal Flow
prompt → validate

## Failure Handling
- retry queue
- dead-letter queue
- audit log

## Tests
- unit
- integration via event bus
