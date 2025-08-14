from rest_framework import serializers
from .models import User, Product, CartItem, Order, OrderItem
from django.contrib.auth.password_validation import validate_password
import re


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'phone_number']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': True,
                'error_messages': {
                    "blank": "Password can't be empty",
                    "required": "Password can't be empty"
                }
            },
            "email": {
                "required": True
            }
        }

    def validate_username(self, username):
        username = ' '.join(username.strip().split())
        if not username:
            raise serializers.ValidationError("Username can't be empty")
        elif username.isdigit():
            raise serializers.ValidationError("Username can't be a number")
        elif '..' in username or username.startswith('.') or username.endswith('.'):
            raise serializers.ValidationError("Username is invalid")
        elif not all(char.isalpha() or char.isspace() or char == '.' for char in username):
            raise serializers.ValidationError("Username is invalid")
        elif User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username already exists")
        return username

    # def validate_password(self, password):
    #     password = password.strip()
    #     if not password:
    #         raise serializers.ValidationError("Password can't be empty")
    #     if len(password) < 8:
    #         raise serializers.ValidationError("Password must be at least 8 characters long")
    #     if not re.search(r"[A-Z]", password):
    #         raise serializers.ValidationError("Password must contain at least one uppercase letter")
    #     if not re.search(r"[a-z]", password):
    #         raise serializers.ValidationError("Password must contain at least one lowercase letter")
    #     if not re.search(r"\d", password):
    #         raise serializers.ValidationError("Password must contain at least one digit")
    #     if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
    #         raise serializers.ValidationError("Password must contain at least one special character")
    #     return password

    def validate_email(self, email):
        email = email.strip().lower()
        if not email:
            raise serializers.ValidationError("Email can't be empty")
        elif User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists")
        elif '..' in email or email.startswith('.') or email.endswith('.') \
            or email.startswith('-') or email.endswith('-') \
            or '--' in email or '.-' in email or '-.' in email \
            or ' ' in email or email.count('@') != 1:
            raise serializers.ValidationError("Invalid Email")
        return email

    def validate_phone_number(self, phone_number):
        phone_number = phone_number.strip()
        if not phone_number:
            raise serializers.ValidationError("Phone number can't be empty")
        if not phone_number.isdigit() or len(phone_number) != 10:
            raise serializers.ValidationError("Invalid phone number")
        if User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError("Phone number already exists")
        return phone_number

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UpdateUserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        required=False,
        allow_blank=False,
        error_messages={
            "blank": "Phone number can't be empty",
        }
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number']

    def validate_username(self, value):
        username = value.strip()
        if not username:
            raise serializers.ValidationError("Username can't be empty")
        elif username.isdigit():
            raise serializers.ValidationError("Username can't be a number")
        return username

    def validate_email(self, value):
        email = value.strip().lower()
        if not email:
            raise serializers.ValidationError("Email can't be empty")
        if User.objects.exclude(id=self.instance.id).filter(email=email).exists():
            raise serializers.ValidationError("Email already in use")
        return email

    def validate_phone_number(self, value):
        phone = value.strip()
        user = self.instance
        if not phone:
            raise serializers.ValidationError("Phone number can't be empty")
        if not phone.isdigit() or len(phone) != 10:
            raise serializers.ValidationError("Invalid phone number")
        if User.objects.exclude(user=user).filter(phone_number=phone).exists():
            raise serializers.ValidationError("Phone number already in use")
        return phone

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        phone_number = validated_data.get('phone_number')
        if phone_number:
            instance.phone_number = phone_number
        instance.save()

        return instance



class ProductCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price']


class ProductManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'created_at', 'updated_at']



class CartSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='product.id', read_only=True)   
    name = serializers.CharField(source='product.name', read_only=True)  
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'name', 'price', 'quantity', 'added_at']  


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock = serializers.IntegerField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'created_at', 'updated_at']


    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be a positive number.")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock must be zero or a positive number.")
        return value
    

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    
    class Meta:
        model = OrderItem
        fields = ['product_name', 'quantity', 'price_per_item']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'total_amount', 'created_at', 'items']
        read_only_fields = ['id', 'user', 'total_amount', 'created_at', 'items']
