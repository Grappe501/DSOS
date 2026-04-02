# EVENT_BUS Service

## Purpose
Event transport

## Uses Tables
events

## Consumes Events
all

## Emits Events
all

## API Endpoints
internal

## Internal Flow
persist → dispatch

## Failure Handling
- retry queue
- dead-letter queue
- audit log

## Tests
- unit
- integration via event bus
