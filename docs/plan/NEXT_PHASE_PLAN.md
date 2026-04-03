# Next Phase Plan — Department Scoping + Actor-Aware Audit Tracking v1

## Purpose
The next phase should turn the current working single-slice system into a more accountable operational platform by tying actions to real users and departments.

## Objectives
1. record `actor_user_id` on all write actions
2. record actor role and department where appropriate
3. filter schedule and future operational data by department when role requires it
4. create owner/admin visibility into actions and system history
5. preserve all current working functionality

## Backend priorities
### Audit logging
- every write action should persist:
  - actor_user_id
  - action
  - entity_type
  - entity_id
  - meta_json
  - timestamp

### Schedule writes
- create
- update
- cancel
- conflict resolution

### Messaging writes
- queue message
- future resend / retry actions

### Query scoping
- viewers should stay read-only
- viewers may need department-limited visibility
- scheduler/admin/owner visibility rules should be explicit
- owner should be global

## Frontend priorities
- audit screen for owner/admin
- surface current role clearly
- show department when useful
- owner/admin views for operational oversight
- preserve viewer-safe UI behavior

## Suggested execution order
1. upgrade audit service
2. upgrade write endpoints to pass actor context
3. update models if needed for audit relations
4. add filtered audit query endpoints
5. add owner/admin audit UI
6. test role boundaries
7. commit and tag

## Definition of done
- actor_user_id appears on write-generated audit rows
- owner/admin can inspect audit history
- role restrictions still work
- schedule flow still works
- login flow still works
- frontend remains branded and stable
