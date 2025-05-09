# 数据库访问

from django.db.models import F
from reserve.models import Products
from django.db import DatabaseError
import logging


class ProductDao:


    @staticmethod
    def get_product_by_id(search_term):
        # 根据id查询商品
        try:
            search_id = int(search_term)
            results = Products.objects.filter(id=search_id).order_by('id')
        except ValueError:
            results = Products.objects.none()
        return results


    @staticmethod
    def get_products_by_name(name):
        return Products.objects.filter(name__icontains=name).order_by('name')

    @staticmethod
    def reserve_by_id(product_id):
        return Products.objects.filter(id=product_id,num__gt=0).update(num=F('num') - 1)




