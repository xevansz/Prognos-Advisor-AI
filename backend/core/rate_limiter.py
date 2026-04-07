from slowapi import Limiter
from slowapi.util import get_remote_address

# Create rate limiter instance
limiter = Limiter(key_func=get_remote_address)

# Rate limit configurations
# Write operations (POST, PUT, DELETE): 30 requests per minute
WRITE_LIMIT = "60/minute"

# Read operations (GET): 100 requests per minute
READ_LIMIT = "100/minute"

# Expensive operations already have custom limits (e.g., prognosis: 5/day)
