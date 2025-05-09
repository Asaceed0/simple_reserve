
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
