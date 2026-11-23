# MCP QA Agent on Windows: Claude + MySQL + Playwright + REST API + Excel

An end-to-end QA automation setup where **Claude Desktop** works as a testing agent through **Model Context Protocol (MCP)** servers. With these servers, Claude can:

- **Query a MySQL database** to pull test data
- **Drive a browser** to register users on a web app
- **Verify the login API** (`POST /api/ecom/auth/login`) and capture the response
- **Write results to Excel** as a test-run report

Everything here was set up from scratch on a **Windows 11** machine, including fixing a broken Python install along the way.

> Practice app used: [rahulshettyacademy.com/client](https://rahulshettyacademy.com/client), a public demo e-commerce site for automation practice.

---

## The flow

```
┌──────────────┐   SQL    ┌─────────────┐  browser   ┌──────────────────────┐
│  MySQL (MCP) │ ───────► │   Claude    │ ─────────► │  Registration page   │
│ Registration │          │  (agent)    │            │  (Playwright / pane) │
│ Details +    │ ◄─────── │             │ ◄───────── │                      │
│ Usernames    │  results │             │  network   │  POST /auth/register │
└──────────────┘          │             │    log     │  POST /auth/login    │
                          │             │            └──────────────────────┘
                          │             │  write     ┌──────────────────────┐
                          │             │ ─────────► │  Excel report (.xlsx)│
                          └─────────────┘            └──────────────────────┘
```

**Agent prompt used** (see [`prompts/agent-prompt.md`](prompts/agent-prompt.md)):
> Go to the client site → open Register → pull the last 2 records from `RegistrationDetails` and `Usernames` → register them (fill anything missing) → read the Postman collection to understand the API contract → make a login call and confirm success → write the new emails to the Excel file.

**Result:** 3/3 users registered, 3/3 logins verified (HTTP 200, `"Login Successfully"`). See [`reports/Registered_Users_Test_Run.xlsx`](reports/Registered_Users_Test_Run.xlsx).

---

## Repo layout

| Path | What it is |
|---|---|
| `config/claude_desktop_config.example.json` | All 5 MCP servers configured for Windows (placeholders only) |
| `sql/schema.sql` | `vikhyatacademy` database: `RegistrationDetails`, `Usernames`, `students` + sample rows |
| `scripts/add-mysql-to-claude-config.ps1` | Adds the MySQL MCP server to Claude's config (prompts for password, backs up first) |
| `scripts/reset-mysql-root-password.ps1` | Resets a forgotten MySQL root password on Windows |
| `registration-site/` | A small local registration website (Python standard library + MySQL) for practice |
| `reports/` | Test-run report from the agent |
| `prompts/agent-prompt.md` | The prompts given to Claude |
| `docs/troubleshooting.md` | Every error hit during setup and how it was fixed |

---

## Setup (Windows)

### 1. Prerequisites
- **Claude Desktop** app
- **Node.js 18+** (for `npx`). Check with `node -v`
- **Python 3.13** from python.org, with **"Add python.exe to PATH"** ticked
  > Python 3.15 was too new and broke `pip` on this machine. 3.13 is the safe choice. See troubleshooting.
- **MySQL Server 8.0** + MySQL Workbench

### 2. Install the MySQL MCP server and uv
```powershell
$py = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
& $py -m pip install mysql-mcp-server uv
```
This puts `uv.exe` and `mysql_mcp_server.exe` in `...\Python313\Scripts\`.

### 3. Create the database
Run [`sql/schema.sql`](sql/schema.sql) in MySQL Workbench (⚡ Execute).

### 4. Configure Claude Desktop
1. Create the folder `C:\Users\<you>\files_claude` (needed by the filesystem server).
2. Open Claude Desktop → **Settings → Developer → Edit Config**.
3. Paste [`config/claude_desktop_config.example.json`](config/claude_desktop_config.example.json), replace `<you>` and `YOUR_MYSQL_PASSWORD`.
4. **Quit Claude from the system tray** (closing the window isn't enough) and reopen it.

> **Tip:** Your config may not be at `%APPDATA%\Claude`. Some installs keep it under `%LOCALAPPDATA%\Claude-Data\<profile>\`. Always open it via **Edit Config**.

### 5. Verify
Ask Claude: *"Run SELECT DATABASE(), VERSION()"*. It should answer with `vikhyatacademy` and your MySQL version.

---

## The 5 MCP servers

| Server | Package | Used for |
|---|---|---|
| `playwright` | `@playwright/mcp` | Browser automation: filling and submitting forms |
| `filesystem` | `@modelcontextprotocol/server-filesystem` | Reading Postman collections, writing files |
| `excel-mcp-server` | `@negokaz/excel-mcp-server` | Reading/writing `.xlsx` |
| `rest-api` | `dkmaker-mcp-rest-api` | Direct REST calls against `https://rahulshettyacademy.com` |
| `mysql` | `mysql-mcp-server` (via `uv`) | SQL queries against the test database |

---

## API contract verified

**Register**: `POST https://rahulshettyacademy.com/api/ecom/auth/register` → `200 {"message":"Registered Successfully"}`

**Login**: `POST https://rahulshettyacademy.com/api/ecom/auth/login`
```json
// Request (Content-Type: application/json)
{ "userEmail": "user@example.com", "userPassword": "********" }

// Response 200
{ "token": "eyJhbGciOi…(JWT)", "userId": "6b04…9740", "message": "Login Successfully" }
```

---

## Safety choices
- **No real passwords** are in this repo. The config uses placeholders, and scripts ask for passwords at runtime with `Read-Host`/`getpass`.
- Test users use `@example.com` addresses (reserved for documentation, so the mail never goes anywhere).
- The agent was **not** allowed to type passwords into websites or put them in API calls. A human entered them, and the agent verified the results from the network log. This is a good pattern for AI-assisted testing.

## Bonus: local registration site
`registration-site/` is a dependency-free practice site that saves to the `students` table. Double-click `start.bat`, enter your MySQL password, and it opens at `http://127.0.0.1:5000`. Every field has a `data-testid` for Playwright.

---

## Credits
- MCP flow inspired by Rahul Shetty Academy's *Agentic AI / Multi-Agent Automation* course
- [Model Context Protocol](https://modelcontextprotocol.io) · [mysql_mcp_server](https://github.com/designcomputer/mysql_mcp_server)
