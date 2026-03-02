# Admin user and how to test admin routes

## 1. Admin in the database

An admin user has been added with:

| Field    | Value             |
|----------|-------------------|
| Email    | `admin@example.com` |
| Password | `Admin@1234`      |
| Role     | `admin`           |

To create or reset this admin again (e.g. after a fresh DB), from the **project root** run:

```powershell
python scripts/create_admin.py
```

To use different credentials, edit `ADMIN_EMAIL`, `ADMIN_USERNAME`, and `ADMIN_PASSWORD` in `scripts/create_admin.py`, then run the script again.

---

## 2. Start the API

From project root, with venv activated:

```powershell
cd c:\Users\User\Desktop\task_manager_api
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

Wait until you see: `Uvicorn running on http://127.0.0.1:8000`.

---

## 3. Get the admin’s access token (Swagger UI)

1. Open in the browser: **http://127.0.0.1:8000/docs**
2. Find **POST /auth/login**.
3. Click **Try it out**.
4. Use this body (no extra spaces):

   ```json
   {
     "email": "admin@example.com",
     "password": "Admin@1234"
   }
   ```

5. Click **Execute**.
6. In the response (e.g. 200), copy the full value of **`access_token`** (the long JWT string). Do not include `"refresh_token"` or quotes.

---

## 4. Authorize Swagger with the token

1. Click the **Authorize** button (top right, lock icon).
2. In the “Value” field enter exactly:

   ```
   Bearer <paste_access_token_here>
   ```

   Example (with a fake token):

   ```
   Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

   There must be a single space between `Bearer` and the token; no extra quotes.

3. Click **Authorize**, then **Close**.

---

## 5. Test admin-only routes

### GET /admin/users (list all users)

1. Find **GET /admin/users** in the list.
2. Click **Try it out**.
3. Click **Execute** (no body or params).
4. **Expected:** Status **200**, response body is a JSON array of all users (including the admin). Each object has `id`, `email`, `username`, `role`, `is_active`, `created_at`, `updated_at`. No `hashed_password`.
5. If you get **401:** the token is missing or wrong — repeat section 3 and 4.
6. If you get **403:** the token belongs to a non-admin user — make sure you logged in as `admin@example.com`.

### DELETE /admin/users/{user_id} (delete a user)

1. Note a **user id** from the list returned by GET /admin/users (e.g. a test user you created, not the admin).
2. Find **DELETE /admin/users/{user_id}**.
3. Click **Try it out**.
4. In **user_id** enter that id (e.g. `2`).
5. Click **Execute**.
6. **Expected:** Status **204** with no response body. That user should disappear from GET /admin/users.
7. **403:** you are not admin. **404:** no user with that id.

---

## 6. Test admin vs normal user (tasks)

### As admin: see all tasks and delete all tasks

1. Keep using the admin token (Authorize still set as in section 4).
2. **GET /tasks**  
   **Expected:** Returns tasks for **all** users (not only yours). If you have tasks owned by different users, you see all of them.
3. **DELETE /tasks** (the one with no path parameter, “Delete all tasks”).  
   **Expected:** Status **204**. All tasks are deleted.

### As normal user: only own tasks, cannot delete all

1. Register a new user: **POST /auth/register** with e.g. `user@example.com` / `User@1234`.
2. Log in as that user: **POST /auth/login** with `user@example.com` / `User@1234`.
3. Copy the new **access_token** from the response.
4. Click **Authorize** again and paste: `Bearer <new_access_token>`, then Authorize → Close.
5. **GET /tasks**  
   **Expected:** Only tasks where `user_id` equals this user’s id (or empty list).
6. **DELETE /tasks** (delete all tasks).  
   **Expected:** Status **403**, body e.g. `"detail": "Only admins can delete all tasks"`.

---

## 7. Quick checklist

| Step | Action | Expected |
|------|--------|----------|
| 1 | Run `python scripts/create_admin.py` | “Admin created” or “Admin already exists” |
| 2 | Start server: `uvicorn app.main:app --reload` | “Uvicorn running on http://127.0.0.1:8000” |
| 3 | POST /auth/login as admin@example.com / Admin@1234 | 200, `access_token` and `refresh_token` in body |
| 4 | Authorize in Swagger with `Bearer <access_token>` | Lock icon shows as authorized |
| 5 | GET /admin/users | 200, list of users |
| 6 | DELETE /admin/users/{id} for a non-admin user | 204 |
| 7 | GET /tasks as admin | 200, all users’ tasks |
| 8 | DELETE /tasks as admin | 204 |
| 9 | Login as normal user, GET /tasks | 200, only that user’s tasks |
| 10 | DELETE /tasks as normal user | 403 |

If any step fails, check: token copied fully, no extra quotes, one space after `Bearer`, and that you are using the correct user (admin vs normal) for that step.
