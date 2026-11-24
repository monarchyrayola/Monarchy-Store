from django.contrib import admin
from .models import (
    Category,
    Product,
    ProductColor,
    ProductImage,
    Order,
    OrderItem
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductColorInline(admin.StackedInline):
    model = ProductColor
    extra = 1


@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'color_code')
    list_filter = ('name',)
    search_fields = ('product__name', 'name')
    inlines = [ProductImageInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'quantity',
        'created_at'
    )

    list_filter = ('category', 'created_at')

    search_fields = ('name', 'description')

    inlines = [ProductColorInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'full_name',
        'phone',
        'total_amount',
        'status',
        'created_at',
    )

    list_filter = ('status', 'created_at')

    search_fields = (
        'full_name',
        'phone',
        'user__username',
    )

    inlines = [OrderItemInline]
