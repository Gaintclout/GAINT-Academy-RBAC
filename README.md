# GAINT Academy — RBAC Corrected Full-Stack Source

This package implements the master functional design as a production-oriented starter:

- Web: React + Vite
- Mobile: React Native + Expo
- API: FastAPI + SQLAlchemy
- Database: SQLite for local development, PostgreSQL-ready
- JWT authentication
- 8 demo roles
- Role-specific dashboards and navigation
- RBAC enforced in backend
- Parent ↔ Student linkage
- Student live-location safety APIs
- Parent child tracking
- Campus live-location monitor
- Generic enterprise/add-on records workspace
- Audit logging
- Docker Compose
- Swagger/OpenAPI
- Backend tests

## Demo Password

All demo users use:

`Password@123`

## Demo Accounts

| Role | Email |
| --- | --- |
| Institution Admin | admin@gaintacademy.com |
| Teacher | teacher@gaintacademy.com |
| Student | student@gaintacademy.com |
| Parent / Guardian | parent@gaintacademy.com |
| Accounts | accounts@gaintacademy.com |
| HR | hr@gaintacademy.com |
| Campus Admin | campus@gaintacademy.com |
| Auditor | auditor@gaintacademy.com |

## Start Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open: <http://127.0.0.1:8000/docs>

## Start Web

```powershell
cd web
npm install
npm run dev
```

Open: <http://localhost:5173>

## Start Mobile

```powershell
cd mobile
npm install
npx expo start
```

For Android emulator use:

```env
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000
```

For a real phone, use your PC LAN IP, for example:

```env
EXPO_PUBLIC_API_URL=http://192.168.1.20:8000
```

## Production Notes

This source implements the functional architecture and working flows. External production integrations still require your real provider credentials and contracts:

- Google Maps / Mapbox
- FCM / APNs
- Payment gateway
- SMS / WhatsApp
- Email
- School bus GPS hardware / IoT
- Cloud object storage
- Production AI provider

Location tracking is implemented as a safety feature with role checks and `ParentStudentLink` authorization.

Replace demo coordinates and simulation controls with real mobile GPS and your approved privacy/retention policy before production.

## RBAC Correction

This build removes generic CRUD controls from read-only roles and enforces the same permissions in the backend through:

`/api/v1/module-access/{page}`

and record mutation checks.