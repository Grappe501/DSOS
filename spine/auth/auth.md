# AUTH Service

## Purpose
Identity + RBAC

## Uses Tables
users, roles, permissions

## Consumes Events
-

## Emits Events
auth.login

## API Endpoints
POST /auth/login

## Internal Flow
validate → token

## Failure Handling
- retry queue
- dead-letter queue
- audit log

## Tests
- unit
- integration via event bus
