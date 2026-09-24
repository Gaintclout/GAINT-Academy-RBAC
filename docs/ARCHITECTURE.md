# Architecture

## Authentication
JWT access tokens are returned by `/api/v1/auth/login`.

## RBAC
Backend authorization is enforced with `require_roles(...)`.
The frontend also requests `/api/v1/navigation` to render role-specific menus.

## Role dashboards
`/api/v1/dashboard` returns a different payload for:
- Institution Admin
- Teacher
- Student
- Parent / Guardian
- Accounts
- HR
- Campus Admin
- Auditor

## Parent-child security
Parents cannot fetch an arbitrary student. `/api/v1/parents/children/{student_id}/location`
first checks `ParentStudentLink`.

## Location
Student sends approved location updates through `/api/v1/location/update`.
Admin/Campus Admin can access authorized live monitoring.
Parent can see only linked children.
Location views and updates are audit logged.

## Production extensions
- PostgreSQL
- Alembic migrations
- Redis
- Celery/RQ worker
- FCM/APNs
- Google Maps/Mapbox
- payment gateway
- object storage
- real AI provider
- rate limiting
- refresh tokens / token revocation
- MFA
