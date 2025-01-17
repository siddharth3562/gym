from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.shortcuts import render, get_object_or_404, redirect
import os
from django.conf import settings
from django.utils.timezone import now


# Create your views here.


def e_login(req):
    if 'shop' in req.session:
        return redirect(shop_home)
    if 'user' in req.session:
        return redirect(user_home)
    if req.method=='POST':
        uname=req.POST['uname']
        password=req.POST['password']
        data=authenticate(username=uname,password=password)
        if data:
            login(req,data)
            if data.is_superuser:
                req.session['shop']=uname
                return redirect(shop_home)
            else:
                req.session['user']=uname
                return redirect(user_home)
        else:
            messages.warning(req, "invalid username or password")
            return redirect(e_login)
    else:
        return render(req,'login.html')
    
def shop_home(req):
    if 'shop' in req.session:
        return render(req, 'shop/home.html')
    else:
        return redirect(e_login)


# user-----------------------


def user_home(req):
    if 'user' in req.session:
        # Fetch the latest supplements
        latest_supplements = Supplement.objects.order_by('-id')[:4]
        supplements_with_stock = []
        for supplement in latest_supplements:
            stock = Stock.objects.filter(supplement=supplement).first()
            supplements_with_stock.append({
                'supplement': supplement,
                'stock': stock
            })
        
        # Fetch the latest equipment
        latest_equipment = Equipment.objects.order_by('-id')[:4]
        equipment_with_stock = []
        for equipment in latest_equipment:
            stock = Stock.objects.filter(equipment=equipment).first()
            equipment_with_stock.append({
                'equipment': equipment,
                'stock': stock
            })
        
        # Pass both to the template
        return render(req, 'user/home.html', {
            'supplements_with_stock': supplements_with_stock,
            'equipment_with_stock': equipment_with_stock
        })
    else:
        return redirect(e_login)
    
def user_reg(req):
    if req.method=='POST':
        uname=req.POST['uname']
        email=req.POST['email']
        pswd=req.POST['pswd']
        try:
            data=User.objects.create_user(first_name=uname,email=email,username=email,password=pswd)
            data.save()
        except:
            messages.warning(req, "email already in use")
            return redirect(user_reg)
        
        return redirect(e_login)
    else:
        return render(req,'user/register.html')
    
def e_logout(req):
    logout(req)
    req.session.flush()
    return redirect(e_login)

def user_supp(req):
    if 'user' in req.session:
        # Fetch all supplements
        all_supplements = Supplement.objects.all()
        supplements_with_stock = []

        # Add stock details to each supplement
        for supplement in all_supplements:
            stock = Stock.objects.filter(supplement=supplement).first()
            supplements_with_stock.append({
                'supplement': supplement,
                'stock': stock
            })

        return render(req, "user/supplements.html", {
            "supplements_with_stock": supplements_with_stock
        })
    else: 
        return redirect(e_login)  
    
def user_equip(req):
    if 'user' in req.session:
        # Fetch all equipment
        all_equipment = Equipment.objects.all()
        equipment_with_stock = []

        # Add stock details to each equipment
        for equipment in all_equipment:
            stock = Stock.objects.filter(equipment=equipment).first()
            equipment_with_stock.append({
                'equipment': equipment,
                'stock': stock
            })

        return render(req, "user/equipments.html", {
            "equipment_with_stock": equipment_with_stock
        })
    else: 
        return redirect(e_login)



    
def not_found(req):
    if 'user' in req.session:
        return render(req,"user/not_found.html")
    else: 
        return redirect(e_login)  

def buy_product(request, product_id):
    if 'user' in request.session:
        # Get the stock entry by its primary key (product_id)
        stock = Stock.objects.filter(id=product_id).first()

        if stock is None:
            return redirect(not_found)  # Redirect if product not found

        # Get all stock entries related to the same supplement or equipment
        if stock.supplement:
            stock_entries = Stock.objects.filter(supplement=stock.supplement)
        else:
            stock_entries = Stock.objects.filter(equipment=stock.equipment)

        # Get the selected weight from query parameters (if any)
        selected_weight_id = request.GET.get('weight', '')

        # Filter for the specific weight details if selected
        weight_details = None
        if selected_weight_id:
            weight_details = stock_entries.filter(pk=selected_weight_id).first()

        return render(request, 'user/buy.html', {
            'stock': stock,
            'stock_entries': stock_entries,
            'weight_details': weight_details,
            'selected_weight_id': selected_weight_id,
        })
    else:
        return redirect(e_login)
    
def add_to_cart(request, product_id):
    # Fetch the stock entry for the product
    stock = Stock.objects.filter(id=product_id).first()

    if stock is None:
        return redirect(user_home)  # Redirect if the product doesn't exist

    # Handle selected weight (if applicable)
    selected_weight_id = request.GET.get('weight')
    if selected_weight_id:
        stock = Stock.objects.filter(id=selected_weight_id).first()
        if stock is None:
            return redirect(user_home)  # Redirect if selected weight doesn't exist

    # Check if the user already has this item in the cart
    existing_cart_item = Cart.objects.filter(user=request.user, stock=stock).first()

    if existing_cart_item:
        # If the item is already in the cart, update the quantity and total price
        existing_cart_item.qty += 1
        existing_cart_item.total_price = existing_cart_item.qty * stock.offer_price  # Update total price
        existing_cart_item.save()
    else:
        # Otherwise, create a new cart item with total price
        total_price = stock.offer_price * 1  # Initial quantity is 1
        Cart.objects.create(user=request.user, stock=stock, qty=1, total_price=total_price)

    return redirect(cart)
# Redirect to the cart view


def qty_in(req, cid):
    if 'user' in req.session:
        username = req.session['user']
        data = get_object_or_404(Cart, pk=cid, user__username=username)
        
        # Increment the quantity
        data.qty += 1
        
        # Update the total price
        data.total_price = data.qty * data.stock.offer_price
        
        # Save the changes
        data.save()
        return redirect(cart)
    else:
        return redirect(e_login)

def qty_dec(req, cid):
    if 'user' in req.session:
        username = req.session['user']
        data = get_object_or_404(Cart, pk=cid, user__username=username)
        
        # Decrement the quantity
        data.qty -= 1
        
        if data.qty == 0:
            # Remove the item from the cart if qty reaches zero
            data.delete()
        else:
            # Update the total price
            data.total_price = data.qty * data.stock.offer_price
            
            # Save the changes
            data.save()
        return redirect(cart)
    else:
        return redirect(e_login)

def cart(request):
    if 'user' in request.session:
        cart_items = Cart.objects.filter(user=request.user)
        return render(request, 'user/cart.html', {'cart_items': cart_items})
    else: 
        return redirect(e_login)  
    
def delete_from_cart(request, cid):

    if 'user' in request.session:
        username = request.session['user']
        
        cart_item = get_object_or_404(Cart, pk=cid, user__username=username)
        
        # Delete the item from the cart
        cart_item.delete()
        
        # Redirect to the cart view
        return redirect(cart)
    else:
        # Redirect to login if the user is not authenticated
        return redirect(e_login)
    


def place_order(request, stock_id=None):
    if stock_id:
        # Single product purchase from the product detail page
        stock_item = get_object_or_404(Stock, id=stock_id)

        # Handle selected weight
        selected_weight_id = request.GET.get('weight')
        if selected_weight_id:
            stock_item = get_object_or_404(Stock, id=selected_weight_id)

    else:
        # Bulk purchase logic (from cart)
        cart_items = Cart.objects.filter(user=request.user)
        total_price = sum(item.qty * item.stock.offer_price for item in cart_items)

    if request.method == 'POST':
        # Collect address and phone number
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')

        if stock_id:  # Single product purchase logic
            qty = 1  # Default quantity is always set to 1

            # Check if there's enough stock
            if qty > stock_item.stock:
                messages.error(request, f"Insufficient stock for {stock_item.name}.")
                return redirect(buy_product, stock_id=stock_item.id)

            # Create Buy record for single product purchase
            Buy.objects.create(
                product=stock_item,
                user=request.user,
                qty=qty,
                price=qty * stock_item.offer_price,  # Using offer price
                date=now(),
                address=address,
                phone_number=phone_number,
            )
            stock_item.stock -= qty
            stock_item.save()

            return redirect(order_history)

        else:  # Bulk purchase logic from cart
            for cart_item in cart_items:
                stock_item = cart_item.stock
                qty = cart_item.qty

                if qty > stock_item.stock:
                    messages.error(request, f"Insufficient stock for {stock_item.name}.")
                    return redirect(cart)

                # Create Buy records and reduce stock
                Buy.objects.create(
                    product=stock_item,
                    user=request.user,
                    qty=qty,
                    price=cart_item.qty * stock_item.offer_price,  # Using offer price
                    date=now(),
                    address=address,
                    phone_number=phone_number,
                )
                stock_item.stock -= qty
                stock_item.save()

            # Clear the cart after bulk purchase
            cart_items.delete()

            return redirect('order_history')

    return render(request, 'user/buy_product.html', {
        'stock_item': stock_item if stock_id else None,
        'cart_items': cart_items if not stock_id else None,
        'total_price': total_price if not stock_id else None,
    })



def order_history(request):
    orders = Buy.objects.filter(user=request.user).order_by('-id')  # Order by ID in reverse (descending)

    return render(request, 'user/history.html', {'orders': orders})


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        if name and email and message:
            # Save the contact message to the database
            Contact.objects.create(name=name, email=email, message=message)
            messages.success(request, 'Your message has been sent successfully!')
            return redirect(contact_view)
        else:
            messages.error(request, 'Please fill in all fields.')

    return render(request, 'user/contact.html')

def search_view(request):
    query = request.GET.get('q')
    results = []
    
    if query:
        # Get supplements and equipment that match the query
        supplements = Supplement.objects.filter(name__icontains=query)
        equipment = Equipment.objects.filter(name__icontains=query)
        
        # Get stock information for display, but keep product IDs for links
        results = []
        for supplement in supplements:
            # Get the first stock entry for this supplement
            stock = Stock.objects.filter(supplement=supplement).first()
            if stock:
                results.append({
                    'id': stock.id,  # Changed: Use stock.id instead of supplement.id
                    'product': supplement,
                    'stock': stock,
                    'type': 'supplement'
                })
                
        for equipment in equipment:
            # Get the first stock entry for this equipment
            stock = Stock.objects.filter(equipment=equipment).first()
            if stock:
                results.append({
                    'id': stock.id,  # Changed: Use stock.id instead of equipment.id
                    'product': equipment,
                    'stock': stock,
                    'type': 'equipment'
                })

    return render(request, 'user/search_results.html', {'query': query, 'results': results})

def admin_order_history(request):
    # Fetch all orders from the Buy model
    orders = Buy.objects.all().order_by('-date')
    return render(request, 'shop/order_history.html', {'orders': orders})

# admin---------------------------


def add_brand(request):
    # Check if the user is authorized via session
    if 'shop' in request.session:
        if request.method == 'POST':
            name = request.POST.get('name')
            if name:  # Ensure the name is not empty
                Brand.objects.create(name=name.lower())
            else:
                return redirect(add_brand)  # Redirect to the same view to display the updated list
        
        brands = Brand.objects.all()
        return render(request, 'shop/add_brand.html', {"brands": brands})
    else:
        return redirect(e_login)


def delete_brand(request, brand_id):
    if 'shop' in request.session:
        try:
            brand = Brand.objects.get(id=brand_id)
            brand.delete()
        except Brand.DoesNotExist:
            pass
        return redirect(add_brand)
    else:
        return redirect(e_login)
    
def s_category(request):
    if 'shop' not in request.session:
        return redirect(e_login) 
    if request.method == 'POST':
        name = request.POST.get('sname') 
        Supplement_Category.objects.create(name=name)
        return redirect(s_category) 
    return render(request, 'shop/add_category.html')

def e_category(request):
    if 'shop' not in request.session:
        return redirect(e_login) 
    if request.method == 'POST':
        name = request.POST.get('ename') 
        Equipment_Category.objects.create(name=name)
        return redirect(e_category) 
    return render(request, 'shop/add_category.html')



def add_equipment(request):
    if 'shop' not in request.session:
        return redirect(e_login)
    
    if request.method == "POST":
        name = request.POST["name"]
        brand = Brand.objects.get(id=request.POST['brand'])
        description = request.POST["description"]
        category = Equipment_Category.objects.get(id=request.POST['category'])
        material = request.POST.get("material")
        img = request.FILES["img"]
        
        equipment = Equipment(
            name=name,
            brand=brand,
            description=description,
            category=category,
            material=material if material else None,
            img=img,
        )
        equipment.save()
        
        return redirect(f'/add_stock?equipment_id={equipment.id}')
    
    brands = Brand.objects.all()
    equipment_categories = Equipment_Category.objects.all()
    
    return render(request, "shop/add_equipment.html", {
        "brands": brands,
        "equipment_categories": equipment_categories,
    })


def add_supplement(request):
    if 'shop' not in request.session:
        return redirect(e_login) 

    if request.method == 'POST':
        name = request.POST['name']
        brand = Brand.objects.get(id=request.POST['brand'])
        description = request.POST['description']
        category = Supplement_Category.objects.get(id=request.POST['category'])
        flavor = request.POST.get('flavor')  
        img = request.FILES['img']

        # Create the supplement
        supplement = Supplement.objects.create(
            name=name,
            brand=brand,
            description=description,
            category=category,
            flavor=flavor,
            img=img
        )

        # Redirect to add_stock with the new supplement ID
        return redirect(f'/add_stock?supplement_id={supplement.id}')

    # Render the add supplement form
    brands = Brand.objects.all()
    categories = Supplement_Category.objects.all()
    return render(request, 'shop/add_supplement.html', {'brands': brands, 'categories': categories})




def add_stock(req):
    if 'shop' in req.session:
        # Get the equipment_id and supplement_id from URL parameters
        equipment_id = req.GET.get('equipment_id')
        supplement_id = req.GET.get('supplement_id')  # Add this line

        if req.method == 'POST':
            # Existing POST handling code
            stock_quantity = req.POST.get('stock')
            price = req.POST.get('price')
            offer_price = req.POST.get('offer_price')
            weight = req.POST.get('weight')
            supplement_id = req.POST.get('supplement')
            equipment_id = req.POST.get('equipment')

            supplement = None
            equipment = None

            if supplement_id:
                supplement = get_object_or_404(Supplement, pk=supplement_id)
            if equipment_id:
                equipment = get_object_or_404(Equipment, pk=equipment_id)

            if supplement and equipment:
                return render(req, 'shop/addweight.html', {
                    'error': "You can only add stock for either a Supplement or Equipment, not both.",
                    'supplements': Supplement.objects.all(),
                    'equipments': Equipment.objects.all(),
                })

            if not supplement and not equipment:
                return render(req, 'shop/addweight.html', {
                    'error': "Please select either a Supplement or Equipment.",
                    'supplements': Supplement.objects.all(),
                    'equipments': Equipment.objects.all(),
                })

            Stock.objects.create(
                supplement=supplement,
                equipment=equipment,
                stock=stock_quantity,
                weight=weight,
                price=price,
                offer_price=offer_price
            )

            return redirect(add_stock)

        # On GET request, display the form
        supplements = Supplement.objects.all()
        equipments = Equipment.objects.all()
        
        selected_equipment = None
        selected_supplement = None

        if equipment_id:
            selected_equipment = get_object_or_404(Equipment, pk=equipment_id)
        if supplement_id:  # Add this block
            selected_supplement = get_object_or_404(Supplement, pk=supplement_id)

        return render(req, 'shop/add_stock.html', {
            'supplements': supplements,
            'equipments': equipments,
            'selected_equipment': selected_equipment,  # Pass to template
            'selected_supplement': selected_supplement  # Pass to template
        })

    return redirect(e_login)




def view_supplements(request):
    supplements = Supplement.objects.all()
    return render(request, "shop/view_supp.html", {"supplements": supplements})

def view_equipments(request):
    equipments = Equipment.objects.all()
    return render(request, "shop/view_eqp.html", {"equipments": equipments})



def edit_supplement(request, supplement_id):
    if 'shop' in request.session:  # Check if the user is logged in
        supplement = get_object_or_404(Supplement, id=supplement_id)  # Retrieve the supplement by its ID
        brands = Brand.objects.all()  # Fetch all brands
        categories = Supplement_Category.objects.all()  # Fetch all categories
        if request.method == 'POST':  # Handle the form submission
            name = request.POST['name']
            description = request.POST['description']
            img = request.FILES.get('img')  # Get the uploaded image file
            brand = request.POST['brand']  # Get the selected brand
            flavor = request.POST['flavor']  # Get the flavor (optional)
            category = request.POST['category']  # Get the selected category
            
            # Update supplement details
            supplement.name = name
            supplement.description = description
            supplement.brand = Brand.objects.get(id=brand)
            supplement.flavor = flavor if flavor else None
            supplement.category = Supplement_Category.objects.get(id=category)

            if img:
                # If a new image is uploaded, delete the old one
                if supplement.img:
                    old_img_path = supplement.img.path
                    if os.path.isfile(old_img_path):
                        os.remove(old_img_path)
                supplement.img = img  # Assign the new image

            supplement.save()  # Save the updated supplement

            # Filter the stock instance by supplement
            stock_instance = Stock.objects.filter(supplement=supplement).first()  # Use supplement to filter stock
            if stock_instance:
                return redirect('edit_stock', stock_id=stock_instance.id)  # Redirect to the edit_stock view, passing stock_id
            else:
                return redirect('add_stock')  # Redirect to the add_stock view if no stock is found

        else:
            return render(request, 'shop/edit_pro.html', {
                'supplement': supplement,
                'brands': brands,
                'categories': categories,
            })  # Render the form with existing data

    return redirect(e_login)


def edit_stock(request, stock_id):
    if 'shop' in request.session:  # Check if the user is logged in
        stock = get_object_or_404(Stock, id=stock_id)  # Retrieve the stock instance by its ID

        supplement = None
        equipment = None
        brands = Brand.objects.all()
        categories = None  # Default categories will be None

        # Fetch the related objects (supplements or equipment)
        if stock.supplement:
            supplement = stock.supplement
            categories = Supplement_Category.objects.all()  # Categories for supplement
            stocks = Stock.objects.filter(supplement=supplement)  # All stocks for the supplement
        elif stock.equipment:
            equipment = stock.equipment
            categories = Equipment_Category.objects.all()  # Categories for equipment
            stocks = Stock.objects.filter(equipment=equipment)  # All stocks for the equipment

        # Handle the form submission
        if request.method == 'POST':
            for stock_item in stocks:
                stock_id_str = str(stock_item.id)
                stock_amount = request.POST.get(f'stock_{stock_id_str}')
                price = request.POST.get(f'price_{stock_id_str}')
                offer_price = request.POST.get(f'offer_price_{stock_id_str}')
                weight = request.POST.get(f'weight_{stock_id_str}')

                # Update each stock instance
                if stock_amount is not None:
                    stock_item.stock = int(stock_amount)
                if price is not None:
                    stock_item.price = float(price)
                if offer_price is not None:
                    stock_item.offer_price = float(offer_price) if offer_price else None
                if weight is not None:
                    stock_item.weight = weight

                stock_item.save()  # Save the updated stock item

            return redirect(view_supplements)

        return render(request, 'shop/edit_stock.html', {
            'stocks': stocks,
            'brands': brands,
            'categories': categories,
            'supplement': supplement,
            'equipment': equipment,
        })
    return redirect(e_login)





def delete_product(req,supp_id):
    data=Supplement.objects.get(id=supp_id)
    file=data.img.url
    file=file.split('/')[-1]
    os.remove('media/'+file)
    data.delete()
    return redirect(view_supplements)

def delete_eqp(req,eqp_id):
    data=Equipment.objects.get(id=eqp_id)
    file=data.img.url
    file=file.split('/')[-1]
    os.remove('media/'+file)
    data.delete()
    return redirect(view_equipments)


def edit_equipment(request, equipment_id):
    if 'shop' in request.session:  # Check if the user is logged in
        equipment = get_object_or_404(Equipment, id=equipment_id)  # Retrieve the equipment by its ID
        brands = Brand.objects.all()  # Fetch all brands
        categories = Equipment_Category.objects.all()  # Fetch all categories
        if request.method == 'POST':  # Handle the form submission
            name = request.POST['name']
            description = request.POST['description']
            img = request.FILES.get('img')  # Get the uploaded image file
            brand = request.POST['brand']  # Get the selected brand
            material = request.POST['material']  # Get the material (optional)
            category = request.POST['category']  # Get the selected category
            
            # Update equipment details
            equipment.name = name
            equipment.description = description
            equipment.brand = Brand.objects.get(id=brand)
            equipment.material = material if material else None
            equipment.category = Equipment_Category.objects.get(id=category)

            if img:
                # If a new image is uploaded, delete the old one
                if equipment.img:
                    old_img_path = equipment.img.path
                    if os.path.isfile(old_img_path):
                        os.remove(old_img_path)
                equipment.img = img  # Assign the new image

            equipment.save()  # Save the updated equipment

            # Filter the stock instance by equipment
            stock_instance = Stock.objects.filter(equipment=equipment).first()  # Use equipment to filter stock
            if stock_instance:
                return redirect('edit_stock', stock_id=stock_instance.id)  # Redirect to the edit_stock view, passing stock_id
            else:
                return redirect(add_stock)  # Redirect to the add_stock view if no stock is found

        else:
            return render(request, 'shop/edit_eqp.html', {
                'equipment': equipment,
                'brands': brands,
                'categories': categories,
            })  # Render the form with existing data

    return redirect(e_login)  # Redirect to login if the user is not logged in

