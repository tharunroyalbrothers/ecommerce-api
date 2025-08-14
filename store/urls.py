from django.urls import path
from .views import (
    UserCreateView, UserDetailView, UserUpdateView, UserDeleteView, UserLoginView, UserLogoutView,
    ProductCreateView, ProductUpdateView, ProductDeleteView, ProductListView, ProductDetailView,
    CartAddView, CartListView, CartDeleteView,CartOrderView,
    
)


urlpatterns = [
    path('usercreate', UserCreateView.as_view(), name='user-create'),
    path('userview', UserDetailView.as_view(), name='user-view'),
    path('userupdate', UserUpdateView.as_view(), name='user-update'),
    path('userdelete', UserDeleteView.as_view(), name='user-delete'),
    path('userlogin', UserLoginView.as_view(), name='user-login'),
    path('userlogout', UserLogoutView.as_view(), name='user-logout'),
    
    
    path('productview', ProductListView.as_view(), name='product-list'),
    path('productview/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
    path('productcreate', ProductCreateView.as_view(), name='product-create'),
    path('productupdate/<int:id>/', ProductUpdateView.as_view(), name='product-update'),
    path('productdelete/<int:id>/', ProductDeleteView.as_view(), name='product-delete'),

    path('cartadd/<int:id>/', CartAddView.as_view(), name='cart-add'),
    path('cartview', CartListView.as_view(), name='cart-view'),
    path('cartdelete/<int:id>/', CartDeleteView.as_view(), name='cart-delete'),
    path('cartorder', CartOrderView.as_view(), name='cart-order'),


]
