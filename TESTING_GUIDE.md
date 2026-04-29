# G2G Fleet Testing & Verification Guide

This guide explains how to test the new scalable backend and frontend architecture.

## 1. Fix Database Connection
Your app currently reports a "password authentication failed" error.
1.  Open [`.env`](file:///c:/Projects/g2g-fleet/.env).
2.  Update the `DATABASE_URL` with your correct PostgreSQL password:
    ```env
    DATABASE_URL="postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/g2g_fleet"
    ```
3.  Restart the dev server: `uvicorn app.main:app --reload`.

---

## 2. Test the API (Backend)
Open your browser to: **`http://localhost:8000/docs`**

### ✅ Test Sync Engine
1.  Find the `POST /api/sync/drivers` endpoint.
2.  Click **"Try it out"** -> **"Execute"**.
3.  It will pull all drivers from Yango and save them to your local PostgreSQL.

### ✅ Test Advanced Lists
1.  Find `GET /api/drivers`.
2.  Use the `ids` or `work_status` parameters to verify filtering works locally.

---

## 3. Test the SDK (Frontend)
The frontend is already configured with all the hooks you need.

1.  **Start Frontend**:
    ```powershell
    cd frontend
    npm run dev
    ```
2.  **Verify SDK**:
    The [API SDK](file:///c:/Projects/g2g-fleet/frontend/src/hooks/queries/) is ready. You can test it by adding this to your `frontend/src/App.tsx`:

    ```tsx
    import { useAllDrivers } from './hooks/queries/useDrivers';

    function DriverList() {
      const { data, isLoading } = useAllDrivers();
      if (isLoading) return <p>Loading drivers...</p>;
      return (
        <ul>
          {data?.drivers.map(d => <li key={d.id}>{d.name}</li>)}
        </ul>
      );
    }
    ```

---

## 4. Database Migrations (Alembic)
If you change your database models in `app/db/models.py`, run:
```powershell
alembic revision --autogenerate -m "Description of change"
alembic upgrade head
```

---

**Everything is now automated and scalable. Happy building!**
