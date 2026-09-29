
import os
import sys

# ---------------------------------------------------------------------------
# Optional .env loading (no external dependency).
# Real environment variables always win; a .env file only fills in what is
# not already set. Lookup order:
#   1. <this dir>/.env      local development  (src/.env, gitignored)
#   2. <this dir>/../.env   production: /opt/nagroadvisory/back/.env, at the
#                           root of the server's git clone (untracked, so
#                           `git pull` on deploy never touches it).
# Never commit a .env file; see .env.example for the supported keys.
# ---------------------------------------------------------------------------
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_env_file(path):
    if not os.path.isfile(path):
        return
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                if line.startswith('export '):
                    line = line[len('export '):].strip()
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                    value = value[1:-1]
                if key and key not in os.environ:
                    os.environ[key] = value
    except OSError as exc:
        # Typically a permissions problem (file owned by another user with
        # chmod 600). Say so loudly instead of failing silently later.
        print('WARNING: cannot read env file %s: %s' % (path, exc), file=sys.stderr)


for _env_path in (os.path.join(_BASE_DIR, '.env'),
                  os.path.join(_BASE_DIR, os.pardir, '.env')):
    _load_env_file(_env_path)


def _env_int(name, default):
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return int(default)


config = {}

if os.getenv('DEBUG', "true").lower() == "true":
    config['DEBUG'] = True
    config['WORKSPACE'] = "fertilizer_et"
    config['LAYER_NAME'] = config['WORKSPACE'] + \
        ":et_wheat_fertilizer_recommendation_normal"
    config['SERVICE'] = 'WFS'
    config['GEOSERVER_URL'] = "https://geo.aclimate.org/geoserver/"
    config['FERTILIZER_RASTERS_DIR'] = "./raster_files/cropped/"
    config['HOST'] = 'localhost'
    config['PORT'] = 5000
    config['CONNECTION_DB'] = 'mongodb://localhost:27017/nextgen'
else:
    # Production. Values come from the environment or the .env file (see
    # .env.example); the defaults below match the historical deployment so a
    # missing line cannot take the API down.
    config['DEBUG'] = False
    config['WORKSPACE'] = os.getenv('WORKSPACE', 'fertilizer_et')
    config['LAYER_NAME'] = config['WORKSPACE'] + \
        os.getenv('LAYER_NAME', ':et_wheat_fertilizer_recommendation_normal')
    config['SERVICE'] = os.getenv('SERVICE', 'WFS')
    config['GEOSERVER_URL'] = os.getenv('GEOSERVER_URL', 'https://geo.aclimate.org/geoserver/')
    config['FERTILIZER_RASTERS_DIR'] = os.getenv('FERTILIZER_RASTERS_DIR', './raster_files/cropped/')
    config['HOST'] = os.getenv('HOST', '0.0.0.0')
    config['PORT'] = _env_int('PORT', 5000)
    config['CONNECTION_DB'] = os.getenv('CONNECTION_DB', 'mongodb://localhost:27017/nextgen_db')

# --- Chatbot / LLM (server-side only: the browser never sees these) ---------
config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '')
config['OPENAI_CHAT_MODEL'] = os.getenv('OPENAI_CHAT_MODEL', 'gpt-4o-mini')
config['OPENAI_TIMEOUT_SECONDS'] = _env_int('OPENAI_TIMEOUT_SECONDS', 45)
# Max chatbot requests per client IP per minute (0 disables the limit).
config['CHATBOT_RATE_LIMIT_PER_MINUTE'] = _env_int('CHATBOT_RATE_LIMIT_PER_MINUTE', 20)
