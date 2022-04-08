# from django.shortcuts import render

# # Create your views here.
# def index(request):
# 		return render(request,"index.html")
		
#******************************************************************************************************
from django.shortcuts import render,redirect
from .models import Product, Contact, Orders, OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
#from .PayTm import Checksum
# Create your views here.
from django.http import HttpResponse, JsonResponse
MERCHANT_KEY = 'kbzk1DSbJiV_03p5'

def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'index.html', params)

def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<4:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'search.html', params)



def about(request):
    return render(request, 'about.html')


def contact(request):
    thank = False
    if request.method=="POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    return render(request, 'contact.html', {'thank': thank})


def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'tracker.html')



def productView(request, myid):

    # Fetch the product using the id
    product = Product.objects.filter(id=myid)
    return render(request, 'prodView.html', {'product':product[0]})


def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone, amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank = True
        id = order.order_id
        # return render(request, 'checkout.html', {'thank':thank, 'id': id})
        # Request paytm to transfer the amount to your account after payment by user
        param_dict = {

                'MID': 'WorldP64425807474247',
                'ORDER_ID': str(order.order_id),
                'TXN_AMOUNT': str(amount),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return  render(request, 'paytm.html', {'param_dict': param_dict})
    else:
           return render(request, 'checkout.html')
  


@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    print(request.POST)
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]
            verify = Checksum.verify_checksum(response_dict, "kbzk1DSbJiV_03p5", checksum)
            if verify:
                if response_dict['RESPCODE'] == '01':
                    print('order successful')
                else:
                    print('order was not successful because' + response_dict['RESPMSG'])
            else:
                return render(request, 'paymentstatus.html', {'response': response_dict})

    return JsonResponse(verify)




#**************************************Authantication**********************************************************

from django.contrib.auth.models import User

from django.contrib.auth import authenticate,login,logout

# register user admin authantication
def auth_registration(request):
     return render(request,"auth_registration.html" )

def auth_save(request):
    if request.method == "POST":
            fname = request.POST["fname"]
            lname = request.POST["lname"]
            email = request.POST["email"]
            password = request.POST["password"]

            au=User.objects.create_user(username=email,password=password,first_name=fname,last_name=lname)
            au.save()

            messages.success(request,"Successfully Registion")
            return redirect("/auth_login")
    else:
             messages.warning(request,"Fail")
             return redirect("/auth_registration")



# login user admin authantication
def auth_login(request):
     return render(request,"auth_login.html" )

def auth_login_check(request):
    if request.method=="POST":
        email=request.POST["email"]  
        password=request.POST["password"]   

        au=authenticate(username=email,password=password)

        if au:
            login(request,au) #session start
            return redirect("/welcome")
        else:
            messages.warning(request,"Login Faill")
            return redirect("/auth_login") 
    else:
        messages.success(request,"Login Sucessfully Completed")
        return render(request,"auth_login.html")
        

# logout
def auth_logout(request):
    logout(request) #session end
    messages.success(request,"Logout Sucessfully ")
    return redirect("/")

# reset Password
def reset(request):
    return render(request,"reset.html" )

def reset_pass(request):
    if request.method=="POST":
        email=request.POST["email"]  
        old_password=request.POST["old_password"] 
        new_password=request.POST["new_password"]   

        au=authenticate(username=email,password=old_password)

        if au:
            au.set_password(new_password)
            au.save()
            return HttpResponse("Password Update Successfully")
        else:
            return HttpResponse("incorect old password")
    else:
        return render(request,"reset.html")
		

# welcome page
def welcome(request):
    data=Product.objects.all()   # select
    return render(request,"welcome.html",{'data':data})


#delete data   
def delete(request):
    id=request.GET["id"]
    Product.objects.filter(id=id).delete() #delete
    return redirect("/welcome")   

#update data
def edit(request):
    id=request.GET["id"]
    data = Product.objects.all().filter(id=id)
    return render(request,"edit.html",{'data':data})   

def update(request):
    if request.method=="POST":
        id=request.POST["id"]
        product_name=request.POST["product_name"]
        category=request.POST["category"]
        subcategory = request.POST["subcategory"]
        price = request.POST["price"]
        desc= request.POST["desc"]
        pub_date=request.POST["pub_date"]

        # update
        Product.objects.filter(id=id).update(product_name=product_name,category=category,subcategory=subcategory,price=price,desc=desc,pub_date=pub_date)
        
        messages.info(request,"Updated Sucessfully Completed")
        return redirect("/welcome")
    else:
        messages.warning(request,"Fail")
        return redirect("/welcome")
