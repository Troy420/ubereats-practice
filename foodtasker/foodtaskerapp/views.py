from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from foodtaskerapp.forms import UserForm, RestaurantForm, UserFormForEdit, MealForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from foodtaskerapp.models import Meal, Order

# Create your views here.


def home(request):
    return redirect(restaurant_home)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_home(request):
    return redirect(restaurant_order)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_account(request):
    user_form = UserFormForEdit(instance = request.user)
    restaurant_form = RestaurantForm(instance = request.user.restaurant)

    if request.method == "POST":
        user_form = UserFormForEdit(request.POST, instance = request.user)
        restaurant_form = RestaurantForm(request.POST, request.FILES, instance = request.user.restaurant)

        if user_form.is_valid() and restaurant_form.is_valid():
            user_form.save()
            restaurant_form.save()

    return render(request, 'restaurant/account.html', {
        "user_form": user_form,
        "restaurant_form": restaurant_form
    })


@login_required(login_url='/restaurant/sign-in/')
def restaurant_meal(request):
    meals = Meal.objects.filter(restaurant = request.user.restaurant).order_by("-id")
    return render(request, 'restaurant/meal.html', {"meals": meals})


@login_required(login_url='/restaurant/sign-in/')
def restaurant_add_meal(request):
    addMeal_form = MealForm()

    if request.method == "POST":
        addMeal_form = MealForm(request.POST, request.FILES)

        if addMeal_form.is_valid():
            meal = addMeal_form.save(commit=False) # Save in the memory, not in the database yet
            meal.restaurant = request.user.restaurant
            meal.save() # now save to database
            return redirect(restaurant_meal)

    return render(request, 'restaurant/add_meal.html', {
        "addMeal_form": addMeal_form
    })

@login_required(login_url='/restaurant/sign-in/')
def restaurant_edit_meal(request, meal_id):
    editMeal_form = MealForm(instance = Meal.objects.get(id = meal_id))

    if request.method == "POST":
        editMeal_form = MealForm(request.POST, request.FILES, instance = Meal.objects.get(id = meal_id))

        if editMeal_form.is_valid():
            editMeal_form.save() # now save to database
            return redirect(restaurant_meal)

    return render(request, 'restaurant/edit_meal.html', {
        "editMeal_form": editMeal_form
    })


@login_required(login_url='/restaurant/sign-in/')
def restaurant_order(request):
    if hasattr(request.user, "restaurant"):
        if request.method == "POST":
            order = Order.objects.get(id = request.POST["id"], restaurant = request.user.restaurant)

            if order.status == Order.COOKING:
                order.status = Order.READY
                order.save()
            # elif order.status == Order.READY:
            #     order.status = Order.OTW
            #     order.save()
            # elif order.status == Order.OTW:
            #     order.status = Order.DELIVERED
            #     order.save()
            # else:
            #     order.status = "Already Delivered"

        orders = Order.objects.filter(restaurant = request.user.restaurant).order_by("-id")
        return render(request, 'restaurant/order.html', {"orders": orders})

    else:
        return redirect(restaurant_sign_up)

@login_required(login_url='/restaurant/sign-in/')
def restaurant_report(request):
    # calculate revenue and number of order by current week
    from datetime import datetime, timedelta

    revenue = []
    orders = []

    #calculate weekdays
    today = datetime.now()
    current_weekdays = [today + timedelta(days = i) for i in range(0 - today.weekday(), 7 - today.weekday() )]

    for day in current_weekdays:
        deliveredOrders = Order.objects.filter(
            restaurant = request.user.restaurant,
            status = Order.DELIVERED,
            created_at__year = day.year,
            created_at__month = day.month,
            created_at__day = day.day,
        )
        revenue.append(sum(order.total for order in deliveredOrders))
        orders.append(deliveredOrders.count())

    return render(request, 'restaurant/report.html', {
        "revenue": revenue,
        "orders": orders
    })


def restaurant_sign_up(request):
    user_form = UserForm()
    restaurant_form = RestaurantForm()

    if request.method == "POST":
        if request.user.is_authenticated:

            restaurant_form = RestaurantForm(request.POST, request.FILES)

            if  restaurant_form.is_valid():
                new_restaurant = restaurant_form.save(commit=False)
                new_restaurant.user = request.user
                new_restaurant.save()

                return redirect(restaurant_home)

        else:
            user_form = UserForm(request.POST)
            restaurant_form = RestaurantForm(request.POST, request.FILES)

            if user_form.is_valid() and restaurant_form.is_valid():
                new_user = User.objects.create_user(**user_form.cleaned_data)
                new_restaurant = restaurant_form.save(commit=False)
                new_restaurant.user = new_user
                new_restaurant.save()

                login(request, authenticate(
                    username=user_form.cleaned_data["username"],
                    password=user_form.cleaned_data["password"]
                ))

                return redirect(restaurant_home)

    if request.user.is_authenticated:
        return render(request, 'restaurant/sign_up_restaurant.html', {
            "restaurant_form": restaurant_form,
        })
    else:
        return render(request, 'restaurant/sign_up.html', {
            "user_form": user_form,
            "restaurant_form": restaurant_form,
        })
