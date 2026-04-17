# Voice / Text Intake

## Text

Standard POST body `{ text, question_key?, entry_mode: "text" }` to `/intake/sessions/{id}/answers`.

## Voice / transcript

Set `entry_mode` to `voice_transcript`. If `transcript_ref` is omitted, server generates `voice_transcript:{session_id}:{answer_id}:{hash}` for traceability.

## Same path as Malone

The browser uses the same `Authorization` header and base URL as `POST /api/malone/chat`. A future pass can pipe Web Speech results into `text` without a new backend route.
