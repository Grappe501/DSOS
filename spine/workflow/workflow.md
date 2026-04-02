# WORKFLOW Service

## Purpose
Process execution

## Uses Tables
workflows

## Consumes Events
schedule.created

## Emits Events
task.created

## API Endpoints
internal

## Internal Flow
state → next

## Failure Handling
- retry queue
- dead-letter queue
- audit log

## Tests
- unit
- integration via event bus
