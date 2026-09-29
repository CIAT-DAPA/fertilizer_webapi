# webapi
Swagger documentation on /apidocs/: 
For example http://localhost:105/apidocs/

## Chatbot endpoint (server-side OpenAI proxy)

`POST /chatbot/message` is the only place the HaFAS platform talks to OpenAI.
The API key, the model and the system prompt live on this server so the React
app never contains a key (a `REACT_APP_*` variable is embedded in the public
JavaScript bundle at build time, which is how earlier keys were leaked and
auto-revoked by OpenAI).

Request body (JSON):

```json
{
  "message": "I grow wheat on 2 ha",
  "conversation_context": "Bot: ...\nUser: ...",
  "collected_data": {"crop": null, "coordinates": null, "farmSizeHa": null},
  "crops": ["Wheat", "Maize"],
  "session_complete": false
}
```

Response: `{"response": "...", "extracted_data": {...}, "missing_data": [...], "next_action": "collect_data|get_recommendation|show_map"}`.
Errors use `{"error": {"code": "...", "message": "..."}}` with 400 (bad input),
429 (client or upstream rate limit), 502/504 (upstream error/timeout) or
503 (`llm_not_configured`).

### Configuration (all environments)

All API settings are read at start-up by `conf.py`, first from real environment
variables and then from a `.env` file that fills in whatever is not set.
`conf.py` looks for `src/.env` (local development) and then `../.env` relative
to `src/`. The full list of variables with their defaults is in `.env.example`.

* Local development: `fertilizer_webapi/src/.env` (gitignored).
* Production (`prodnodejs01`): `/opt/nagroadvisory/back/` is a git clone of this
  repository and the API runs from its `src/` folder, so the file goes at the
  root of the clone, `/opt/nagroadvisory/back/.env` (gitignored/untracked). The
  Jenkins job deploys with `git pull origin main` and restarts the API; it no
  longer exports any variables, so this file is the single source of
  configuration. Restart the API after changing it.

  ```bash
  sudo cp src/.env.example /opt/nagroadvisory/back/.env   # then edit the values
  sudo chown <api-user>:<api-user> /opt/nagroadvisory/back/.env
  sudo chmod 600 /opt/nagroadvisory/back/.env
  ```

Variables:

| Variable | Default | Notes |
|---|---|---|
| `DEBUG` | `true` | **Set `DEBUG=False` in production.** Debug mode binds `127.0.0.1` and uses the local `nextgen` DB. |
| `WORKSPACE` | `fertilizer_et` | GeoServer workspace |
| `LAYER_NAME` | `:et_wheat_fertilizer_recommendation_normal` | appended to `WORKSPACE` |
| `SERVICE` | `WFS` | |
| `GEOSERVER_URL` | `https://geo.aclimate.org/geoserver/` | |
| `FERTILIZER_RASTERS_DIR` | `./raster_files/cropped/` | relative to `src/` |
| `HOST` | `0.0.0.0` | production bind address |
| `PORT` | `5000` | |
| `CONNECTION_DB` | `mongodb://localhost:27017/nextgen_db` | MongoDB connection string (production) |
| `OPENAI_API_KEY` | – | **required for the chatbot**; without it `/chatbot/message` returns 503 |
| `OPENAI_CHAT_MODEL` | `gpt-4o-mini` | |
| `OPENAI_TIMEOUT_SECONDS` | `45` | |
| `CHATBOT_RATE_LIMIT_PER_MINUTE` | `20` | per client IP, `0` disables |

If the `.env` file exists but cannot be read (e.g. wrong owner with `chmod 600`),
the API prints `WARNING: cannot read env file ...` to stderr (`log.txt`) at start-up.

Note: when a `.env` file is present, the Flask dev server prints
`Tip: There are .env or .flaskenv files present. Do "pip install python-dotenv"`.
This can be ignored: `conf.py` reads the file itself, python-dotenv is not required.

Never put the key in git, in the Jenkinsfile, in GitHub Actions for the
frontend, or in any `REACT_APP_*` variable. Use a project-scoped OpenAI key with
a monthly budget, and rotate it from the OpenAI dashboard if it is ever exposed.
