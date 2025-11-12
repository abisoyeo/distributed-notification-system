from django.core.cache import cache
from django.conf import settings
import logging
import json

logger = logging.getLogger(__name__)


class CacheKeys:
    """Standardized cache key naming"""
    
    @staticmethod
    def user_data(user_id):
        """Cache key for full user data"""
        return f"user:data:{user_id}"
    
    @staticmethod
    def user_preferences(user_id):
        """Cache key for user preferences"""
        return f"user:preferences:{user_id}"
    
    @staticmethod
    def user_push_token(user_id):
        """Cache key for user push token"""
        return f"user:push_token:{user_id}"
    
    @staticmethod
    def user_email(email):
        """Cache key for user lookup by email"""
        return f"user:email:{email}"


class UserCache:
    """Redis cache operations for user data"""
    
    # Cache TTL settings (in seconds)
    USER_DATA_TTL = 600  # 10 minutes
    PREFERENCES_TTL = 600  # 10 minutes
    PUSH_TOKEN_TTL = 300  # 5 minutes
    
    @staticmethod
    def get_user_data(user_id):
        """
        Get cached user data
        Returns: dict or None
        """
        cache_key = CacheKeys.user_data(user_id)
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.debug(f"Cache HIT: user data for {user_id}")
                return json.loads(cached_data) if isinstance(cached_data, str) else cached_data
            logger.debug(f"Cache MISS: user data for {user_id}")
            return None
        except Exception as e:
            logger.error(f"Cache get error for user {user_id}: {str(e)}")
            return None
    
    @staticmethod
    def set_user_data(user_id, user_data, ttl=None):
        """
        Cache user data (without password)
        Args:
            user_id: UUID of user
            user_data: dict with user information
            ttl: time to live in seconds (default: USER_DATA_TTL)
        """
        cache_key = CacheKeys.user_data(user_id)
        ttl = ttl or UserCache.USER_DATA_TTL
        
        try:
            # Ensure password is not cached
            cache_data = user_data.copy()
            cache_data.pop('password', None)
            
            # Serialize for Redis
            cache.set(cache_key, json.dumps(cache_data), ttl)
            logger.debug(f"Cache SET: user data for {user_id} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for user {user_id}: {str(e)}")
            return False
    
    @staticmethod
    def delete_user_data(user_id):
        """
        Delete cached user data
        """
        cache_key = CacheKeys.user_data(user_id)
        try:
            cache.delete(cache_key)
            logger.debug(f"Cache DELETE: user data for {user_id}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error for user {user_id}: {str(e)}")
            return False
    
    @staticmethod
    def get_user_preferences(user_id):
        """
        Get cached user preferences
        Returns: dict with email/push booleans or None
        """
        cache_key = CacheKeys.user_preferences(user_id)
        try:
            cached_prefs = cache.get(cache_key)
            if cached_prefs:
                logger.debug(f"Cache HIT: preferences for {user_id}")
                return json.loads(cached_prefs) if isinstance(cached_prefs, str) else cached_prefs
            logger.debug(f"Cache MISS: preferences for {user_id}")
            return None
        except Exception as e:
            logger.error(f"Cache get error for preferences {user_id}: {str(e)}")
            return None
    
    @staticmethod
    def set_user_preferences(user_id, preferences, ttl=None):
        """
        Cache user preferences
        Args:
            user_id: UUID of user
            preferences: dict with email/push booleans
            ttl: time to live in seconds (default: PREFERENCES_TTL)
        """
        cache_key = CacheKeys.user_preferences(user_id)
        ttl = ttl or UserCache.PREFERENCES_TTL
        
        try:
            cache.set(cache_key, json.dumps(preferences), ttl)
            logger.debug(f"Cache SET: preferences for {user_id} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for preferences {user_id}: {str(e)}")
            return False
    
    @staticmethod
    def delete_user_preferences(user_id):
        """
        Delete cached user preferences
        """
        cache_key = CacheKeys.user_preferences(user_id)
        try:
            cache.delete(cache_key)
            logger.debug(f"Cache DELETE: preferences for {user_id}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error for preferences {user_id}: {str(e)}")
            return False
    
    @staticmethod
    def get_push_token(user_id):
        """
        Get cached push token
        Returns: string or None
        """
        cache_key = CacheKeys.user_push_token(user_id)
        try:
            cached_token = cache.get(cache_key)
            if cached_token:
                logger.debug(f"Cache HIT: push token for {user_id}")
                return cached_token
            logger.debug(f"Cache MISS: push token for {user_id}")
            return None
        except Exception as e:
            logger.error(f"Cache get error for push token {user_id}: {str(e)}")
            return None
    
    @staticmethod
    def set_push_token(user_id, push_token, ttl=None):
        """
        Cache push token
        Args:
            user_id: UUID of user
            push_token: FCM token string
            ttl: time to live in seconds (default: PUSH_TOKEN_TTL)
        """
        cache_key = CacheKeys.user_push_token(user_id)
        ttl = ttl or UserCache.PUSH_TOKEN_TTL
        
        try:
            cache.set(cache_key, push_token, ttl)
            logger.debug(f"Cache SET: push token for {user_id} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for push token {user_id}: {str(e)}")
            return False
    
    @staticmethod
    def delete_push_token(user_id):
        """
        Delete cached push token
        """
        cache_key = CacheKeys.user_push_token(user_id)
        try:
            cache.delete(cache_key)
            logger.debug(f"Cache DELETE: push token for {user_id}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error for push token {user_id}: {str(e)}")
            return False
    
    @staticmethod
    def invalidate_user_cache(user_id):
        """
        Invalidate all cached data for a user
        Call this on user update/delete operations
        """
        try:
            UserCache.delete_user_data(user_id)
            UserCache.delete_user_preferences(user_id)
            UserCache.delete_push_token(user_id)
            logger.info(f"Cache INVALIDATED: all data for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Cache invalidation error for user {user_id}: {str(e)}")
            return False