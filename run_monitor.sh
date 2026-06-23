#!/bin/bash
cd "/Users/biagioderisi/UNIOR/05 - PROGETTI/MONITOR_CONCORSI_DIRIGENZA"

ERROR=0

./.venv/bin/python scripts/monitor_concorsi.py >> logs/monitor.log 2>&1 || ERROR=1
./.venv/bin/python scripts/monitor_v2.py >> logs/monitor_v2.log 2>&1 || ERROR=1
./.venv/bin/python scripts/enrich_report_v2.py >> logs/enrich.log 2>&1 || ERROR=1
./.venv/bin/python scripts/send_report_email.py >> logs/mail.log 2>&1 || ERROR=1

if [ "$ERROR" -ne 0 ]; then
    ./.venv/bin/python scripts/send_error_email.py >> logs/mail.log 2>&1
fi
