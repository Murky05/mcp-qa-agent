# Prompts given to Claude

## 1. System-style instructions for API testing

> You are my local API testing and file-system automation assistant connected via MCP servers.
> 1. **Tool discovery first**: check which MCP tools are available and use them directly.
> 2. **File system**: check the target directory and file names before reading/modifying; never overwrite without confirming or backing up.
> 3. **API testing**: inspect method, URL, headers and body before sending; report status code, relevant headers, body and extracted values (tokens, IDs); never expose real passwords or tokens.
> 4. **Summary**: end each task with what was executed, files read/written, and API results.

## 2. The end-to-end task

> Go to https://rahulshettyacademy.com/client and click on "Don't have an account? Register here".
> Pull the data of the last 2 records from the `RegistrationDetails` and `Usernames` tables and register them on the page. If anything is missing, use your own knowledge to fill it in.
> Then read the attached Postman collection to understand the API contract, make a login call with the necessary information, and confirm the login succeeded.
> Once confirmed, write the newly registered email and password to `newdata.xlsx` in the appropriate columns.

## What the agent did

1. Queried MySQL: `SELECT r.*, u.email FROM RegistrationDetails r JOIN Usernames u ... ORDER BY r.id DESC LIMIT 2`
2. Found that one record was already registered from an earlier run and skipped it instead of failing.
3. Filled in a blank `occupation` with a sensible value (`Student`).
4. Filled the registration form and checked every field with JavaScript before submitting.
5. A human typed the passwords. The agent then read `POST /api/ecom/auth/register` → `200` and `POST /api/ecom/auth/login` → `200 "Login Successfully"` from the network log.
6. Wrote the results to an Excel report, leaving a yellow column for passwords.
