# TASK Service

## Purpose
Work units

## Uses Tables
tasks

## Consumes Events
workflow.started

## Emits Events
task.created

## API Endpoints
POST /tasks/create

## Internal Flow
assign

## Failure Handling
- retry queue
- dead-letter queue
- audit log

## Tests
- unit
- integration via event bus
