class Config:
  # Redis settings
  USE_REDIS = True
  REDIS_HOST = 'localhost'
  REDIS_PORT = 6379
  REDIS_DB = 0
  CACHE_EXPIRY_SECONDS = 3600  # 1 hour

  # Flask settings
  DEBUG = True
  TESTING = False
