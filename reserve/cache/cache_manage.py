# 缓存管理
import logging
from django.core.cache import cache
from django.conf import settings
import redis

logger = logging.getLogger(__name__)

cache_conn = redis_conn = redis.Redis(**settings.REDIS_CONNECTION)


class CacheManager:

    @staticmethod
    def get_page_cache(key):
        # 找缓存
        return cache.get(key)

    @staticmethod
    def set_page_cache(key,data,timeout=120):
        # 设置缓存
        cache.set(key,data,timeout=timeout)

    @staticmethod
    def set_relate_keys(page_obj,key):
        # 保存关联，id:保存有该商品的所有缓存键
        for p in page_obj:
            product_id = p.id
            relate_cache_keys = f'relate_{product_id}_keys'
            redis_conn.sadd(relate_cache_keys, key)

    @staticmethod
    def clear_relate_cache(product_id):

        try:
            # 根据修改库存的id删除与其关联的所有缓存
            relate_cache_keys = f'relate_{product_id}_keys'
            cache_keys = redis_conn.smembers(relate_cache_keys)
            # print(cache_keys)
            if cache_keys:
                # 删除关联缓存，删除关联关系
                cache.delete(*cache_keys)
                cache.delete(relate_cache_keys)
        except redis.exceptions.RedisError as e:
            logger.error(f'清理缓存失败:{e}')








