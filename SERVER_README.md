GTS Server Ops README

## Purpose

This server hosts GTS internal web apps on the local network (no public internet
access required for clients).

## LAN Network

- Interface: eno1
- Static IP: 192.168.1.230/24
- Gateway: 192.168.1.1
- DNS: 192.168.1.1
- DNS search domain: lan
- Hostname (target): gts-server
- Friendly name (LAN): gts-server.lan

## Access

- Primary access: tailscale ssh gts@gts-server
- Remote support: TeamViewer (installed/configured)

## Apps

### rental_scheduler

- Repo: git@github.com mailto:git@github.com:RockSolid-Data/gts-rental-scheduler.
  git
- App dir: /srv/apps/rental_scheduler
- Venv: /srv/venvs/rental_scheduler
- Env file: /etc/gts/apps/rental_scheduler.env (root-owned)
- Databases:
  - Main: gts_scheduler (owner: rental_scheduler_user)
  - Accounting: gingerich_trailer_rentals (owner: postgres)
- Gunicorn service: gunicorn-rental_scheduler
- Nginx port: 8001
- URLs:
  - On server: http://127.0.0.1:8001/
  - On LAN (IP): http://192.168.1.230:8001/
  - On LAN (name): http://gts-server.lan:8001/ http://gts-server.lan:8001/
- Logs:
  - App: /var/log/gts/rental_scheduler/access.log
  - App: /var/log/gts/rental_scheduler/error.log
  - Nginx: /var/log/nginx/error.log

- Discord error alerts (Django):
  - Purpose: send a Discord message when unhandled request exceptions occur
  - Env vars (in /etc/gts/apps/rental_scheduler.env):
    - DISCORD_WEBHOOK_URL=... (secret)
    - DISCORD_ALERTS_ENABLED=true
    - DISCORD_ALERTS_DEDUP_SECONDS=300
    - DISCORD_ALERTS_TIMEOUT_SECONDS=2
    - DISCORD_ALERTS_APP_NAME=rental_scheduler
    - DISCORD_ALERTS_ENV=prod
  - Notes:
    - Alerts only fire when DEBUG=False
    - Dedup is per-process; repeated errors within the window are suppressed
    - Full trace details remain in /var/log/gts/rental_scheduler/error.log


### shop_scheduler

- Repo: git@github.com mailto:git@github.com:stephenrocksolid/gts-shop-scheduler.
  git
- App dir: /srv/apps/shop_scheduler
- Venv: /srv/venvs/shop_scheduler
- Staticfiles: /srv/apps/shop_scheduler/staticfiles
- Env file: /etc/gts/apps/shop_scheduler.env (root-owned, group-readable via
  gtsapps)
- System user: shop_scheduler (home: /home/shop_scheduler, shell:
  /usr/sbin/nologin)
- Deploy key: /home/shop_scheduler/.ssh/id_ed25519 (GitHub deploy key on repo)
- Database: gts_shop_scheduler (owner: shop_scheduler_user)
- Gunicorn service: gunicorn-shop_scheduler
  - Socket: /run/gunicorn-shop_scheduler/gunicorn.sock
- Nginx port: 8002
- URLs:
  - On server: http://127.0.0.1:8002/
  - On LAN (IP): http://192.168.1.230:8002/
  - On LAN (name): http://gts-server.lan:8002/ http://gts-server.lan:8002/
- Logs:
  - App: /var/log/gts/shop_scheduler/access.log
  - App: /var/log/gts/shop_scheduler/error.log
  - Nginx: /var/log/nginx/error.log


Note: App code is stored in Git and is not included in system-state backups.
Python virtualenvs are not backed up; they are rebuilt during restore.
                                                                                  
## Services (how to check)

- Gunicorn status:
  - sudo systemctl status gunicorn-rental_scheduler --no-pager
  - sudo journalctl -u gunicorn-rental_scheduler -n 200 --no-pager
  - sudo systemctl status gunicorn-shop_scheduler --no-pager
  - sudo journalctl -u gunicorn-shop_scheduler -n 200 --no-pager
- Nginx status:
  - sudo systemctl status nginx --no-pager
  - sudo nginx -t


## Node.js Setup (one-time)

If Node.js/npm is not installed on the server:

```bash
# Install Node.js 20 LTS from NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

## Deploying (manual, current approach)

### rental_scheduler

  1. Pull latest code:

    sudo -u rental_scheduler -H git -C /srv/apps/rental_scheduler pull

  2. Install python deps (if changed):

    sudo -u rental_scheduler -H /srv/venvs/rental_scheduler/bin/pip install -r /srv/apps/rental_scheduler/requirements.txt

  3. Install npm deps (if package.json or package-lock.json changed):

    cd /srv/apps/rental_scheduler
    sudo -u rental_scheduler -H npm install

  4. Build front-end assets (if CSS/templates/tailwind config changed):

    cd /srv/apps/rental_scheduler
    sudo -u rental_scheduler -H npm run build

  5. Migrate + collectstatic:

    sudo -u rental_scheduler -H bash -lc '
    set -a
    source /etc/gts/apps/rental_scheduler.env
    set +a
    cd /srv/apps/rental_scheduler
    /srv/venvs/rental_scheduler/bin/python manage.py migrate
    /srv/venvs/rental_scheduler/bin/python manage.py collectstatic --noinput
    '

  6. Restart:

    sudo systemctl restart gunicorn-rental_scheduler

## Accounting invoice lock guardrail

When a Classic invoice is PAID or has external relations (payments/credits),
the scheduler blocks price-sensitive contract edits unless a force override is used.

### Staff workflow

- Normal path: unapply payment(s) in Classic, reopen invoice, then edit contract.
- Emergency path: check "Force override" and provide a reason.
  - This saves the Scheduler contract but DOES NOT update Classic.
  - Force overrides are logged in /var/log/gts/rental_scheduler/error.log.

### Audit existing mismatches

Run after deploy to identify legacy mismatches:

  sudo -u rental_scheduler -H bash -lc '
  set -a
  source /etc/gts/apps/rental_scheduler.env
  set +a
  cd /srv/apps/rental_scheduler
  /srv/venvs/rental_scheduler/bin/python manage.py audit_contract_invoice_mismatches
  '

Optional filters:

  /srv/venvs/rental_scheduler/bin/python manage.py audit_contract_invoice_mismatches \
    --start-date 2026-01-01 --end-date 2026-01-31 --report-path /tmp/mismatch_report.csv

  5. Test Discord alerts (optional, controlled):

  sudo -u rental_scheduler -H bash -lc '
  set -a
  source /etc/gts/apps/rental_scheduler.env
  set +a
  cd /srv/apps/rental_scheduler
  /srv/venvs/rental_scheduler/bin/python manage.py shell -c "import logging; logger=logging.getLogger('django.request');\ntry:\n    1/0\nexcept Exception:\n    logger.exception('Discord alert test')"
  '

### shop_scheduler

  1. Pull latest code:
 
    sudo -u shop_scheduler -H git -C /srv/apps/shop_scheduler pull

  2. Install python deps (if changed):

    sudo -u shop_scheduler -H /srv/venvs/shop_scheduler/bin/pip install -r /srv/apps/shop_scheduler/requirements.txt

  3. Install npm deps (if package.json or package-lock.json changed):

    cd /srv/apps/shop_scheduler
    sudo -u shop_scheduler -H npm install

  4. Build front-end assets (if CSS/templates/tailwind config changed):

    cd /srv/apps/shop_scheduler
    sudo -u shop_scheduler -H npm run build

  5. Migrate + collectstatic:

    sudo -u shop_scheduler -H bash -lc '
    set -a
    source /etc/gts/apps/shop_scheduler.env
    set +a
    cd /srv/apps/shop_scheduler
    /srv/venvs/shop_scheduler/bin/python manage.py migrate
    /srv/venvs/shop_scheduler/bin/python manage.py collectstatic --noinput
    '

  6. Restart:

    sudo systemctl restart gunicorn-shop_scheduler

## Config locations

- Gunicorn units: /etc/systemd/system/gunicorn-*.service
- Nginx sites: /etc/nginx/sites-available/* and sites-enabled/*
- App env files: /etc/gts/apps/*.env
- Log rotation: /etc/logrotate.d/gts-*

## Log rotation

  Application logs are rotated daily by logrotate, which sends USR1 to gunicorn
  for graceful log file reopening.

### rental_scheduler

- Config: /etc/logrotate.d/gts-rental_scheduler
- Rotates: /var/log/gts/rental_scheduler/*.log
- Schedule: daily
- Retention: 14 days
- Compression: gzip (delayed by 1 day)
  
  Manual rotation:

    sudo logrotate -f /etc/logrotate.d/gts-rental_scheduler

  Dry run test:

    sudo logrotate -d /etc/logrotate.d/gts-rental_scheduler

### shop_scheduler

- Config: /etc/logrotate.d/gts-shop_scheduler (if created)
- Rotates: /var/log/gts/shop_scheduler/*.log

## Backups (implemented)

### Overview

  We keep business-critical Postgres backups in two places:

  1. Local (WD Red HDD) for fast restores
  2. Cloud (DigitalOcean Spaces, nyc3) for offsite recovery

### Local Postgres backups (WD Red)

- Mount: /mnt/pg_backups (WD Red HDD mounted here)
- Automated backup root: /mnt/pg_backups/postgres
  - Dumps:
    - /mnt/pg_backups/postgres/db/gts_scheduler/
    - /mnt/pg_backups/postgres/db/gts_shop_scheduler/
    - /mnt/pg_backups/postgres/db/gingerich_trailer_rentals/
    - /mnt/pg_backups/postgres/db/gingerich_trailer/
  - Globals (roles/grants): /mnt/pg_backups/postgres/globals/
  - Logs: /mnt/pg_backups/postgres/logs/
- Script: /usr/local/sbin/pg_backup_gts_databases.sh
- Schedule: hourly via pg-backup-gts.timer
- Retention (local):
  - DB dumps + sha256: 7 days
  - globals + sha256: 30 days
  - logs: 30 days
- Validation: each dump is checked with pg_restore --list and a .sha256 file
  is written.

  Check status:

    systemctl list-timers | grep pg-backup-gts
    sudo systemctl status pg-backup-gts.service --no-pager
    sudo ls -lt /mnt/pg_backups/postgres/logs | head

### Offsite backups (DigitalOcean Spaces / Restic)

- Provider: DigitalOcean Spaces (nyc3)
- Repo: s3:https://nyc3.digitaloceanspaces.com/rocksolid-storage/backups/gts-
  server/postgres
- Credentials/env: /etc/gts/backup/restic.env (root-owned, chmod 600)
- Script: /usr/local/sbin/restic_backup_postgres_dumps.sh
- Schedule: daily at 02:30 via restic-postgres.timer
- Integrity check: weekly (Sun 03:30) via restic-postgres-check.timer
- Retention (cloud): keep 48 hourly, 30 daily, 12 weekly, 12 monthly

  Check status:

    systemctl list-timers | egrep 'restic-postgres'
    sudo bash -c 'source /etc/gts/backup/restic.env && restic snapshots | tail -n
  10'

### Restore (local-first)

  Local restore is fastest. Pick the desired dump and restore with  pg_restore .

  Example: restore  gts_shop_scheduler  from local disk:

    latest="$(ls -1t /mnt/pg_backups/postgres/db/gts_shop_scheduler/*.dump | head -
  n 1)"
    echo "$latest"

    sudo systemctl stop gunicorn-shop_scheduler

    sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM
  pg_stat_activity WHERE datname='gts_shop_scheduler';"
    sudo -u postgres dropdb gts_shop_scheduler
    sudo -u postgres createdb -O shop_scheduler_user gts_shop_scheduler
    sudo -u postgres pg_restore -d gts_shop_scheduler "$latest"

    sudo systemctl start gunicorn-shop_scheduler

  Example: restore  gts_scheduler :

    latest="$(ls -1t /mnt/pg_backups/postgres/db/gts_scheduler/*.dump | head -n
  1)"
    echo "$latest"

    sudo systemctl stop gunicorn-rental_scheduler

    sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM
  pg_stat_activity WHERE datname='gts_scheduler';"
    sudo -u postgres dropdb gts_scheduler
    sudo -u postgres createdb -O rental_scheduler_user gts_scheduler
    sudo -u postgres pg_restore -d gts_scheduler "$latest"

    sudo systemctl start gunicorn-rental_scheduler

### Notes

- Backups are stored with restricted permissions (group postgres). The gts user is
  in the postgres group for read access.

## System-state backups (server recovery)

### Goal

  In a disaster (hardware loss / OS reinstall), we can rebuild the server quickly
  by restoring:

- Nginx config
- systemd unit files + timers
- app env files/secrets
- SSH deploy keys (service users)
- backup tooling config + scripts
- an inventory snapshot (packages, enabled services, mounts, nginx -T output)

  Not included: app code ( /srv/apps ) and Python venvs ( /srv/venvs ). Code is
  restored from Git and venvs are rebuilt.

### What is backed up

  This backup intentionally focuses on “state/config” needed to rebuild:

  Included:

- /etc/gts
- /etc/nginx
- /etc/systemd/system
- /etc/ssh
- /home (includes deploy keys like /home/*/.ssh/)
- /root
- /etc/fstab
- /usr/local/sbin
- Inventory output: /etc/gts/bootstrap/* (generated each run)

  Excluded:

- /mnt/pg_backups (local DB dump disk)
- /var/lib/postgresql (we restore Postgres from dumps)
- /var/log, /tmp, caches
- /srv/apps, /srv/venvs, **/.venv, **/venv

### Offsite repo (DigitalOcean Spaces / Restic)

- Repo: s3:https://nyc3.digitaloceanspaces.com/rocksolid-storage/backups/gts-
  server/system-state
- Credentials/env: /etc/gts/backup/restic-system-state.env (root-owned, chmod 600)
  - Note: systemd EnvironmentFile= requires KEY=value format (no export).
- Include/exclude lists:
  - /etc/gts/backup/system-state/includes.txt
  - /etc/gts/backup/system-state/excludes.txt
- Script: /usr/local/sbin/restic-system-state-backup.sh
- Schedule: daily via restic-system-state-backup.timer (02:20)
- Retention (cloud): keep 30 daily, 12 weekly, 12 monthly

### How to check status

    systemctl list-timers | egrep 'restic-system-state'
    sudo systemctl status restic-system-state-backup.service --no-pager
    sudo journalctl -u restic-system-state-backup.service -n 200 --no-pager

### View snapshots (helper method)

  Systemd loads env vars automatically, but interactive shells need exported vars.
  Recommended helper:

    sudo tee /usr/local/sbin/restic-system-state-env.sh >/dev/null <<'EOF'
    #!/usr/bin/env bash
    set -euo pipefail
    set -a
    source /etc/gts/backup/restic-system-state.env
    set +a
    exec "$@"
    EOF
    sudo chmod 755 /usr/local/sbin/restic-system-state-env.sh

  Then:

    sudo /usr/local/sbin/restic-system-state-env.sh restic snapshots --tag system-
  state

### Restore test (safe)

  Restore into a staging directory (does not overwrite live system):

    sudo rm -rf /root/restore-test
    sudo mkdir -p /root/restore-test
    sudo /usr/local/sbin/restic-system-state-env.sh restic restore latest --tag
  system-state --target /root/restore-test
    sudo ls -la /root/restore-test/etc/gts | head

### Disaster recovery (high-level)

  1. Install Debian and set networking/hostname for  gts-server  (static IP 192.
  168.1.230)
  2. Install base packages:  tailscale ,  nginx ,  restic , and any dependencies
  3. Recreate  /etc/gts/backup/restic-system-state.env  from password manager
  4. Restore system-state:
    sudo /usr/local/sbin/restic-system-state-env.sh restic restore latest --tag
  system-state --target /

  5.  sudo systemctl daemon-reload 
  6. Rebuild apps:
  - recreate service users (if needed)
  - clone repos into /srv/apps/<app>
  - rebuild venvs and install requirements
  - run migrations/collectstatic
  7. Restore Postgres from local/offsite dumps (see Postgres restore section
  above)
  8. Start gunicorn services and reload nginx