
-- Core Identity
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  role_id UUID,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE roles (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE permissions (
  id UUID PRIMARY KEY,
  role_id UUID,
  resource TEXT,
  action TEXT
);

-- Events (immutable)
CREATE TABLE events (
  id UUID PRIMARY KEY,
  type TEXT,
  payload JSONB,
  source TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Tasks
CREATE TABLE tasks (
  id UUID PRIMARY KEY,
  type TEXT,
  assigned_to UUID,
  status TEXT,
  due_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Workflows
CREATE TABLE workflows (
  id UUID PRIMARY KEY,
  name TEXT,
  state TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Schedules
CREATE TABLE schedules (
  id UUID PRIMARY KEY,
  title TEXT,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  created_by UUID
);

-- Reminders
CREATE TABLE reminders (
  id UUID PRIMARY KEY,
  task_id UUID,
  trigger_time TIMESTAMP,
  status TEXT
);

-- Messages
CREATE TABLE messages (
  id UUID PRIMARY KEY,
  recipient TEXT,
  channel TEXT,
  content TEXT,
  status TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Audit Log
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  action TEXT,
  user_id UUID,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
