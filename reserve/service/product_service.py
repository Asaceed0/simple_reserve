# 服务

import logging
from django.core.paginator import Paginator
from reserve.database.products_dao import ProductDao
from reserve.cache.cache_manage import CacheManager

logger = logging.getLogger(__name__)

class ProductService:
    @staticmethod
    def search_products(search_type, search_term, page_number):

        # 按name分页，按id不分页，模版中按照num_pages判断是否显示分页
        if search_type == 'id':
            context = {
                'page_obj': ProductDao.get_product_by_id(search_term),
                'search_term': search_term,
                'search_type': search_type,
            }
            return context
        else:
            # 按name搜索
            cache_key = f'n_{search_term}_{page_number}'
            cached_data = CacheManager.get_page_cache(cache_key)
            if cached_data:
                # 缓存命中
                return cached_data

            results = ProductDao.get_products_by_name(search_term)
            paginator = Paginator(results, 10)
            page_obj = paginator.get_page(page_number)
            # 保存关联关系
            CacheManager.set_relate_keys(page_obj,cache_key)
            context = {
                'page_obj': page_obj,
                'search_term': search_term,
                'search_type': search_type,
            }
            # 设置分页缓存
            CacheManager.set_page_cache(cache_key,context,120)
            return context

    @staticmethod
    def reserve_product(product_id):
        try:
            updated = ProductDao.reserve_by_id(product_id)
            if updated:
                # 清除与该id关联的缓存
                CacheManager.clear_relate_cache(product_id)
                return {'success': True}
            else:
                # 若预定失败
                product = ProductDao.get_product_by_id(product_id)
                if not product:
                    return {'success': False, 'message': '商品不存在'}
                return {'success': False, 'message': '库存不足'}
        except Exception as e:

            logger.error(f"服务层异常: {e}")
            return {'success': False, 'message': '系统错误，请重试'}