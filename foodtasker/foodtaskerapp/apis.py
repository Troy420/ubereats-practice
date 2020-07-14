import json
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from oauth2_provider.models import AccessToken

from foodtaskerapp.models import Restaurant, Meal, Order, OrderDetails
from foodtaskerapp.serializers import RestaurantSerializer, MealSerializer, OrderSerializer

# --------------------
# CUSTOMER
# --------------------
def customer_get_all_restaurant_lists(request):
    restaurants = RestaurantSerializer(
        Restaurant.objects.all().order_by("-id"),
        many = True,
        context = {"request": request}
    ).data
    return JsonResponse({"restaurants": restaurants})

def customer_get_all_menu(request, restaurant_id):
    meals = MealSerializer(
        Meal.objects.filter(restaurant_id = restaurant_id).order_by("-id"),
        many = True,
        context = {"request": request}
    ).data
    return JsonResponse({"meals": meals})

@csrf_exempt
def customer_add_order(request):
    """
        params:
            access_token
            restaurant_id
            address
            order_details (json format), example:
                [{"meal_id": 1, "quantity": 2},{"meal_id": 2, "quantity": 3}]
            stripe_token

        return: {"status": "success"}
    """

    if request.method == "POST":
        # Get Token
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
            expires__gt = timezone.now())

        # Get Profile
        customer = access_token.user.customer

        # Check whether customer has any order that is not delivered
        if Order.objects.filter(customer = customer).exclude(status = Order.DELIVERED):
            return JsonResponse(
                {
                    "status": "fail", 
                    "error": "your last order must be completed"
                }
            )

        # Check the Address
        if not request.POST["address"]:
            return JsonResponse(
                {
                    "status": "failed", 
                    "error": "Address is required"
                }
            )

        #  Get Order Details in Json Format
        order_details = json.loads(request.POST["order_details"])

        # Get total order
        order_total = 0
        for meal in order_details:
            order_total += Meal.objects.get(id = meal["meal_id"]).price * meal["quantity"]
        
        if len(order_details) > 0:
            # step 1- create an order
            order = Order.objects.create(
                customer = customer,
                restaurant_id = request.POST["restaurant_id"],
                total = order_total,
                status = Order.COOKING,
                address = request.POST["address"]
            )

            # step 2 - create order details
            for meal in order_details:
                OrderDetails.objects.create(
                    order = order,
                    meal_id = meal["meal_id"],
                    quantity = meal["quantity"],
                    sub_total = Meal.objects.get(id = meal["meal_id"]).price * meal["quantity"]
                )
            return JsonResponse(
                {
                    "status":"success"
                }
            )

def customer_get_latest_order(request):
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
        expires__gt = timezone.now())
    customer = access_token.user.customer
    order = OrderSerializer(Order.objects.filter(customer = customer).last()).data

    return JsonResponse({"order": order})

# ---------------------
# RESTAURANT
# ---------------------
def restaurant_order_notification(request, last_request_time):
    notification = Order.objects.filter(restaurant = request.user.restaurant, 
    created_at__gt = last_request_time).count()

    return JsonResponse({"notification": notification})

# ---------------------
# DRIVER
# ---------------------

def driver_get_ready_orders(request):
    orders = OrderSerializer(
        Order.objects.filter(status = Order.READY, driver = None).order_by("-id"),
        many=True
    ).data
    return JsonResponse({"orders": orders})

@csrf_exempt
# POST params: access_token, order_id
def driver_pick_order(request):

    if request.method == "POST":
        #GET token
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"),
        expires__gt = timezone.now())

        #GET Driver
        driver = access_token.user.driver

        #Check if the driver can only pick up on order at a time
        if Order.objects.filter(driver = driver).exclude(status = Order.OTW and Order.DELIVERED):
            return JsonResponse({"status": "failed", "error": "you can only pick one order at a time"})

        try:
            order = Order.objects.get(
                id = request.POST['order_id'],
                driver = None,
                status = Order.READY,
            )
            order.driver = driver
            order.status = Order.OTW
            order.picked_at = timezone.now()
            order.save()

            return JsonResponse({"status": "success"})

        except Order.DoesNotExist:
            return JsonResponse({"status": "failed", "error": "This order has been picked up by another driver"})

    return JsonResponse({"status": "failed", "error": "you must fill in the blanks"})

# GET
# what do we need to get from the database?
# access_token 
def driver_get_latest_order(request):
     #GET token
    access_token = AccessToken.objects.get(token = request.GET.get("access_token"),
    expires__gt = timezone.now())

    #GET Driver
    driver = access_token.user.driver

    #GET latest order
    latest_order = OrderSerializer(
        Order.objects.filter(driver = driver).order_by("picked_at").last()
    ).data

    return JsonResponse({"latest_order": latest_order})

def driver_complete_order(request):
    return JsonResponse({})

def driver_get_revenue(request):
    return JsonResponse({})