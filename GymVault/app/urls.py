from django.urls import path
from . import views

urlpatterns=[
    path('',views.e_login),
    path('shop_home',views.shop_home),
    path('logout',views.e_logout),
    path('add_brand',views.add_brand),
    path('s_category',views.s_category),
    path('e_category',views.e_category),
    path('add_e',views.add_equipment),
    path('add_s',views.add_supplement),
    path('add_stock',views.add_stock),
    path('edit_stock/<int:stock_id>/',views.edit_stock, name='edit_stock'),
    path('edit_supp/<int:supplement_id>/',views.edit_supplement),
    path('delete_brand/<brand_id>',views.delete_brand),
    path('view_pro',views.view_supplements),
    path('view_eqp',views.view_equipments),
    path('edit_eqp/<int:equipment_id>/',views.edit_equipment),
    path('del/<int:supp_id>/',views.delete_product),
    path('del_supp/<int:eqp_id>/',views.delete_eqp),


    path('user_home',views.user_home),
    path('user_reg',views.user_reg),
    path('error',views.not_found),
    path('user_supp',views.user_supp),
    path('user_eqp',views.user_equip),
    path('buy_p/<int:product_id>/',views.buy_product),
    path('add_cart/<int:product_id>/', views.add_to_cart),
    path('cart', views.cart),
    path('qty_in/<cid>',views.qty_in),
    path('qty_dec/<cid>',views.qty_dec),
    path('buy_product/<int:stock_id>/',views.place_order),
    path('buy_all/', views.place_order),
    path('order/',views.order_history),
    path('contact/',views.contact_view),
    path('search/',views.search_view),
    path('order_admin/',views.admin_order_history),

]