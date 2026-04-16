# Vaani — Professional Deployment Guide (v2.5)

## 🔒 1. Infrastructure Setup
Vaani uses Supabase as a managed PostgreSQL vault. 

### 1.1 Database Initialization
1. Paste the contents of `supabase/schema.sql` into the Supabase SQL Editor.
2. Ensure you have your Database Password saved.

---

## 🔑 2. Environment Configuration
Set these variables in your production environment.

| Key | Description |
| :--- | :--- |
| `SUPABASE_URL` | Application API endpoint |
| `SUPABASE_DB_HOST` | Database host address |
| `SUPABASE_DB_PASSWORD` | PostgreSQL Password |
| `SARVAM_API_KEY` | **Sarvam AI** for STT/TTS |
| `APP_ENV` | Set to `production` |

---

## 🚀 3. Deployment Steps
1. **Push Code:** Push to your GitHub repository.
2. **Deploy:** Use Render, Railway, or Docker.
3. **Verify:** Check `https://your-app.com/api/health`.

## 🔍 4. Troubleshooting
*   **"Mic Button Disabled":** Check if you are using **HTTPS**.
*   **"Sarvam Unreachable":** Check your Sarvam API key quota.
