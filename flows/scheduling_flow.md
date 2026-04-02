
# Core Flow: Scheduling → Reminder → Messaging

1. POST /schedules/create
2. emit schedule.created
3. workflow engine starts follow-up workflow
4. task created
5. reminder scheduled
6. reminder.triggered event
7. messaging engine sends notification
8. audit log written
