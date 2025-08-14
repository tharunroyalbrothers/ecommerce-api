from rest_framework import generics, status, permissions, serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, ValidationError, NotAuthenticated, NotFound, AuthenticationFailed
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from .models import User, Product, CartItem, Order, OrderItem
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import (
    UserSerializer, ProductCustomerSerializer, ProductSerializer,
    CartSerializer, UpdateUserSerializer, ProductManagerSerializer,OrderSerializer
)

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class UserCreateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request):
        raise ValidationError("Use POST to register")

    def post(self, request):
        username = request.data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Account already exists. Please login")

        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Account created successfully."}, status=status.HTTP_201_CREATED)


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserUpdateView(generics.UpdateAPIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    serializer_class = UpdateUserSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        response = super().put(request, *args, **kwargs)
        return Response({"message": "Updated successfully", "data": response.data}, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        response = super().patch(request, *args, **kwargs)
        return Response({"message": "Updated successfully", "data": response.data}, status=status.HTTP_200_OK)


class UserDeleteView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_authenticated:
            return Response({"logged_in_as": request.user.username})

    def delete(self, request):
        request.user.delete()
        return Response({"message": "Account deleted successfully"}, status=status.HTTP_200_OK)


class UserLoginView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            return Response({"logged_in_as": request.user.username})
        return Response({"message":"No account is logged in now. Login now"},status=status.HTTP_200_OK)

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not User.objects.filter(username=username).exists():
            raise NotFound("Account does not exist. Please create the account")

        user = authenticate(request, username=username, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials")

        login(request, user)
        return Response({"message": "Login successful"}, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            return Response({"message": f"{request.user.username} is currently logged in."})
        return Response({"message": "No account is logged in. Login before logout"})

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"message": "No user is logged in."}, status=status.HTTP_400_BAD_REQUEST)
        
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'is_manager', False)



class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsManager]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsManager]
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(product)
        return Response(
            {
                "message": "This is the product you are willing to update.",
                "product": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def put(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        updated_product_data = serializer.data  
        
        return Response(
            {
                "message": "Product updated.",
                "updated_product": updated_product_data
            },
            status=status.HTTP_200_OK
        )



class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsManager]
    lookup_field = "id"
    
    def get(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(product)
        return Response(
            {
                "message": "This is the product you are willing to delete.",
                "product": serializer.data
            },
            status=status.HTTP_200_OK
        )

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(product)
        product_data = serializer.data
        product.delete()
        return Response(
            {
                "message": "Product deleted successfully.",
                "deleted_product": product_data
            },
            status=status.HTTP_200_OK
        )


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()

    def get_serializer_class(self):
        user = self.request.user
        if user.is_authenticated and getattr(user, "is_manager", False):
            return ProductManagerSerializer
        return ProductCustomerSerializer


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        user = self.request.user
        if user.is_authenticated and getattr(user, "is_manager", False):
            return ProductManagerSerializer
        return ProductCustomerSerializer


class CartAddView(generics.CreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_product(self, product_id):
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValidationError({"message": "Product not found."})

    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('id')
        product = self.get_product(product_id)
        return Response({
            "message": "Product details",
            "product": ProductCustomerSerializer(product).data
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        product_id = kwargs.get('id')
        product = self.get_product(product_id)
        quantity = int(request.data.get('quantity', 1))

        if quantity <= 0:
            raise ValidationError({"message": "Quantity must be greater than 0"})

        existing_cart_item = CartItem.objects.filter(user=request.user, product=product).first()

        if existing_cart_item:
            new_quantity = existing_cart_item.quantity + quantity
            if new_quantity > product.stock:
                raise ValidationError({"message": f"You can't purchase more than {product.stock} of {product.name}."})
            existing_cart_item.quantity = new_quantity
            existing_cart_item.save()
            return Response({
                "message": f"Updated {product.name} in your cart.",
                "quantity": new_quantity,
                "product": ProductCustomerSerializer(product).data
            })

        if quantity > product.stock:
            raise ValidationError({"message": f"You can't purchase more than {product.stock} of {product.name}."})

        serializer = self.get_serializer(data={'quantity': quantity})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, product=product)

        return Response({
            "message": f"Added {product.name} to your cart.",
            "quantity": quantity,
            "product": ProductCustomerSerializer(product).data
        }, status=status.HTTP_201_CREATED)


class CartListView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)


class CartDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get_cart_item(self, id):
        cart_item = CartItem.objects.filter(user=self.request.user, product_id=id).first()
        if not cart_item:
            raise ValidationError({"message": "Your cart is empty."})
        return cart_item

    def get(self, request, id):
        cart_item = self.get_cart_item(id)
        serializer = CartSerializer(cart_item)
        return Response({
            "message": f"Cart item details for {cart_item.product.name}",
            "cart_item": serializer.data
        })

    def post(self, request, id):
        cart_item = self.get_cart_item(id)
        quantity_to_remove = int(request.data.get("quantity", 0))

        if quantity_to_remove <= 0:
            raise ValidationError({"message": "Quantity must be greater than 0"})
        if quantity_to_remove > cart_item.quantity:
            raise ValidationError({"message": f"You have only {cart_item.quantity} of this item in your cart."})

        cart_item.quantity -= quantity_to_remove

        if cart_item.quantity == 0:
            cart_item.delete()
            return Response({"message": f"All of {cart_item.product.name} removed from cart."})
        else:
            cart_item.save()
            return Response({
                "message": f"Removed {quantity_to_remove} of {cart_item.product.name} from cart.",
                "remaining_quantity": cart_item.quantity
            })


class CartOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = CartItem.objects.filter(user=request.user)
        bill = []
        total = 0
        for item in cart_items:
            amount = item.quantity * float(item.product.price)
            bill.append({
                "product": item.product.name,
                "quantity": item.quantity,
                "price": float(item.product.price),
                "amount": amount
            })
            total += amount
        return Response({"bill": bill, "total": total}, status=200)

    @transaction.atomic
    def post(self, request):
        cart_items = CartItem.objects.select_related('product').filter(user=request.user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        for item in cart_items:
            if item.quantity > item.product.stock:
                return Response({"error": f"Not enough stock for {item.product.name}"}, status=400)

        order_total = sum(item.quantity * float(item.product.price) for item in cart_items)
        order = Order.objects.create(user=request.user, total_amount=order_total)

        bill = []
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_per_item=item.product.price
            )

            item.product.stock -= item.quantity
            item.product.save()

            bill.append({
                "product": item.product.name,
                "quantity": item.quantity,
                "price": float(item.product.price),
                "amount": item.quantity * float(item.product.price)
            })

        cart_items.delete()

        return Response({
            "message": "Your order is placed successfully.",
            "bill": bill,
            "total": order_total
        }, status=201)