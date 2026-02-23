# ❌ SEC001: All secrets hardcoded in config file

# Database
DATABASE_URL = "postgresql://admin:SuperSecret123!@prod.db.company.com:5432/maindb"
DATABASE_PASSWORD = "Prod@DB#Pass123!"
DATABASE_ROOT_PASSWORD = "root_db_pass_never_share"

# JWT
JWT_SECRET_KEY = "jwt_super_secret_key_hardcoded_in_config"
JWT_REFRESH_SECRET = "jwt_refresh_secret_also_hardcoded"
JWT_EXPIRY = 86400

# Payment Gateways
STRIPE_SECRET_KEY = "sk_live_realStripeKeyHardcoded1234"
STRIPE_WEBHOOK_SECRET = "whsec_hardcoded_stripe_webhook"
PAYPAL_SECRET = "paypal_live_secret_key_exposed"

# Cloud Services
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
AWS_REGION = "us-east-1"
S3_BUCKET = "company-production-bucket"

# Third party APIs
SENDGRID_API_KEY = "SG.hardcoded_sendgrid_key_exposed"
TWILIO_AUTH_TOKEN = "twilio_auth_token_hardcoded"
GOOGLE_API_KEY = "AIzaSyHardcodedGoogleKey12345"
SLACK_WEBHOOK = "https://hooks.slack.com/services/hardcoded/webhook/url"

# Internal
INTERNAL_API_SECRET = "internal_microservice_secret_key"
ADMIN_BYPASS_TOKEN = "admin_bypass_12345_never_use_in_prod"
ENCRYPTION_KEY = "aes256_hardcoded_encryption_key_32c"

# ❌ MAINT002: TODO/FIXME
# TODO: Move all these to environment variables
# FIXME: This is a massive security risk
# HACK: Will fix before production (never did)

# ❌ MAINT004: Magic numbers without explanation
MAX_RETRIES = 3
TIMEOUT = 30
CACHE_TTL = 3600
MAX_UPLOAD_SIZE = 10485760
RATE_LIMIT = 100
PORT = 8080
WORKERS = 4
