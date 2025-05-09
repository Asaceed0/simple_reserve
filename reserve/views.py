# from django.conf import settings
# from django.shortcuts import render
# from django.core.paginator import Paginator
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from django.views.decorators.csrf import csrf_exempt
# from .models import Products
# from django.db.models import F
# from django.core.cache import cache
# import redis
#
# redis_conn = redis.Redis(**settings.REDIS_CONNECTION)
#
# def search(request):
#     search_type = request.GET.get('search_type', 'name')
#     search_term = request.GET.get('search_term', '').strip()
#     if not search_term:
#         return render(request, 'search.html')
#
#     # id搜索不分页
#     if search_type == 'id':
#
#         try:
#             search_id = int(search_term)
#             results = Products.objects.filter(id=search_id).order_by('id')
#         except ValueError:
#             results = Products.objects.none()
#         context = {
#             'page_obj': results,
#             'search_term': search_term,
#             'search_type': search_type,
#         }
#
#
#         return render(request, 'result2.html', context)
#
#
#     # name搜索分页
#     else:
#         page_number = request.GET.get('page', 1)
#         cache_key = f'n_{search_term}_{page_number}'  # 分页缓存
#         cache_data = cache.get(cache_key)
#         if cache_data:
#             print('cache命中')
#             return render(request, 'result2.html', cache_data)
#         print('没命中')
#         results = Products.objects.filter(name__icontains=search_term).order_by('name')
#
#         # 美页10条
#         paginator = Paginator(results, 10)
#         page_obj = paginator.get_page(page_number)
#
#         # 保存本分也中单个商品与缓存键的关系，其他地方修改库存也能删除该缓存
#         for p in page_obj:
#             product_id = p.id
#             relate_cache_keys = f'relate_{product_id}_keys'
#             redis_conn.sadd(relate_cache_keys, cache_key)
#         context = {
#             'page_obj': page_obj,
#             'search_term': search_term,
#             'search_type': search_type,
#         }
#         cache_key = f'n_{search_term}_{page_number}'
#         cache.set(cache_key,context,timeout=120)
#         print('cache saved')
#         return render(request, 'result2.html', context)
#
#
#
#
#
# @require_POST
# @csrf_exempt
# def reserve_product(request, product_id):
#     updated = Products.objects.filter(
#         id=product_id,
#         num__gt=0
#     ).update(num=F('num') - 1)
#
#
#     if updated:
#         relate_cache_keys = f'relate_{product_id}_keys'
#         cache_keys = redis_conn.smembers(relate_cache_keys)
#         # print(cache_keys)
#         if cache_keys:
#             # 删除关联缓存，删除关联关系
#             cache.delete(*cache_keys)
#             cache.delete(relate_cache_keys)
#         return JsonResponse({'success': True})
#     else:
#         try:
#             Products.objects.get(id=product_id)
#             return JsonResponse({'success': False, 'message': '库存不足'})
#         except Products.DoesNotExist:
#             return JsonResponse({'success': False, 'message': '商品不存在'})


from reserve.service.product_service import ProductService
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)


def exp_handle(func):
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except Exception as e:
            logger.exception("视图层异常")
            return JsonResponse({'success': False, 'message': '系统繁忙，请稍后重试'})

    return wrapper


def search(request):
    search_type = request.GET.get('search_type', 'name')
    search_term = request.GET.get('search_term', '').strip()
    page_number = request.GET.get('page', 1)
    if not search_term:
        return render(request, 'search.html')
    context = ProductService.search_products(search_type, search_term, page_number)
    return render(request, 'result2.html', context)


@exp_handle
@require_POST
@csrf_exempt
def reserve_product(request, product_id):
    status = ProductService.reserve_product(product_id)
    return JsonResponse(status)
