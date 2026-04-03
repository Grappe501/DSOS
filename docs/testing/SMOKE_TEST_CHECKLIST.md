# Smoke Test Checklist

## Backend
- `/health`
- `/api/health`
- `/api/auth/login`
- `/api/auth/me`
- `/api/schedules`

## Frontend
- login works
- auth redirect works
- schedules page loads
- create schedule works
- cancel schedule works
- current role displays correctly
- sign out works

## Role tests
### owner
- can create schedule
- can cancel schedule
- can view protected operational screens

### viewer
- cannot create schedule
- cannot cancel schedule
- sees read-only messaging in schedule screen
