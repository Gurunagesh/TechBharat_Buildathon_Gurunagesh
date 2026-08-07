-- ======================================================================
-- TechBharat Buildathon - Agentic AI Meeting Assistant
-- MySQL 8.0 Schema
--
-- Execution order (foreign key dependencies):
--   1. meetings
--   2. participants
--   3. action_items
--   4. github_syncs
--   5. audit_logs
-- ======================================================================

CREATE DATABASE IF NOT EXISTS meeting_assistant
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE meeting_assistant;

-- 1. Meetings
-- Root entity. One row = one uploaded transcript.
CREATE TABLE IF NOT EXISTS meetings (
    meeting_id        CHAR(36)        NOT NULL,
    title             VARCHAR(255)    NOT NULL DEFAULT 'Untitled Meeting',
    meeting_date      DATE            NULL,
    uploaded_at       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    transcript_hash   CHAR(64)        NOT NULL,
    transcript_text   LONGTEXT        NOT NULL,
    summary           TEXT            NULL,
    decisions         TEXT            NULL,
    risks             TEXT            NULL,
    open_questions    TEXT            NULL,
    participants_raw  TEXT            NULL,
    processing_status ENUM('UPLOADING','PARSING','EXTRACTING','VALIDATING','READY_FOR_REVIEW','COMPLETED','FAILED') NOT NULL DEFAULT 'UPLOADING',
    error_message     TEXT            NULL,
    created_at        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (meeting_id),
    UNIQUE KEY uq_transcript_hash (transcript_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Participants
CREATE TABLE IF NOT EXISTS participants (
    participant_id    CHAR(36)        NOT NULL,
    meeting_id        CHAR(36)        NOT NULL,
    name              VARCHAR(255)    NOT NULL,
    email             VARCHAR(255)    NULL,
    role              VARCHAR(100)    NULL,
    created_at        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (participant_id),
    CONSTRAINT fk_participants_meeting
        FOREIGN KEY (meeting_id) REFERENCES meetings (meeting_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Action Items
CREATE TABLE IF NOT EXISTS action_items (
    action_item_id    CHAR(36)        NOT NULL,
    meeting_id        CHAR(36)        NOT NULL,
    title             VARCHAR(512)    NOT NULL,
    description       TEXT            NULL,
    owner             VARCHAR(255)    NOT NULL DEFAULT 'UNASSIGNED',
    owner_email       VARCHAR(255)    NULL,
    due_date          DATE            NULL,
    priority          ENUM('HIGH','MEDIUM','LOW') NOT NULL DEFAULT 'MEDIUM',
    confidence_score  DECIMAL(4,3)    NOT NULL DEFAULT 0.000,
    evidence_quote    TEXT            NULL,
    status            ENUM('PENDING_REVIEW','APPROVED','REJECTED','SYNCED') NOT NULL DEFAULT 'PENDING_REVIEW',
    created_at        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (action_item_id),
    CONSTRAINT fk_action_items_meeting
        FOREIGN KEY (meeting_id) REFERENCES meetings (meeting_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. GitHub Syncs
-- One record per action item. Extensible: add SlackSync/CalendarSync later.
CREATE TABLE IF NOT EXISTS github_syncs (
    sync_id               CHAR(36)        NOT NULL,
    action_item_id        CHAR(36)        NOT NULL,
    github_issue_number   INT             NULL,
    github_issue_url      VARCHAR(512)    NULL,
    github_issue_title    VARCHAR(512)    NULL,
    sync_status           ENUM('PENDING','SUCCESS','FAILED') NOT NULL DEFAULT 'PENDING',
    synced_at             DATETIME        NULL,
    error_message         TEXT            NULL,
    created_at            DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (sync_id),
    UNIQUE KEY uq_github_sync_action (action_item_id),
    CONSTRAINT fk_github_syncs_action
        FOREIGN KEY (action_item_id) REFERENCES action_items (action_item_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Audit Logs
-- Immutable event history. Rows are NEVER updated, only inserted.
CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id          CHAR(36)        NOT NULL,
    meeting_id        CHAR(36)        NOT NULL,
    action_item_id    CHAR(36)        NULL,
    event_type        ENUM('UPLOAD','PARSE','DUPLICATE_DETECTED','EXTRACT','VALIDATE','RESOLVE','EDIT','APPROVE','REJECT','SYNC','GITHUB_SUCCESS','GITHUB_FAILURE','LLM_RETRY','LLM_FALLBACK','PROCESSING_FAILED') NOT NULL,
    actor             ENUM('AI_AGENT','HUMAN_USER','SYSTEM') NOT NULL DEFAULT 'SYSTEM',
    payload           JSON            NULL,
    created_at        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (audit_id),
    CONSTRAINT fk_audit_logs_meeting
        FOREIGN KEY (meeting_id) REFERENCES meetings (meeting_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_audit_logs_action
        FOREIGN KEY (action_item_id) REFERENCES action_items (action_item_id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ======================================================================
-- INDEXES
-- ======================================================================

CREATE INDEX idx_meetings_status      ON meetings (processing_status);
CREATE INDEX idx_meetings_date        ON meetings (meeting_date);
CREATE INDEX idx_meetings_created     ON meetings (created_at DESC);

CREATE INDEX idx_participants_meeting ON participants (meeting_id);

CREATE INDEX idx_actions_meeting      ON action_items (meeting_id);
CREATE INDEX idx_actions_status       ON action_items (status);
CREATE INDEX idx_actions_owner        ON action_items (owner);
CREATE INDEX idx_actions_priority     ON action_items (priority);
CREATE INDEX idx_actions_created      ON action_items (created_at DESC);

CREATE INDEX idx_audit_meeting        ON audit_logs (meeting_id);
CREATE INDEX idx_audit_created        ON audit_logs (created_at DESC);
CREATE INDEX idx_audit_event_type     ON audit_logs (event_type);
