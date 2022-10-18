from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.conf import settings
import os
import base64
from django.contrib.auth.models import User
from django.contrib import auth
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpRequest
import json
from auction import models
import dateutil.parser
import datetime

# Create your views here.
def index(request):
	username='Login to bid'
	li_disabled=True
	if request.user.is_authenticated:
		username=request.user
		li_disabled=False
	return render(request,'index.html',{'username':username,'li_flag':li_disabled})	

@csrf_exempt
def user_login(request):
	if 'user_name' in request.POST:
		username=request.POST['user_name']
		password=request.POST['password']
		user=auth.authenticate(username=username,password=password)
		if user:
			auth.login(request,user)
			return HttpResponse('/auction/index')
		return
	context=dict()
	return render(request,'user_login.html',context)

def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('/auction/user_login')

def sell(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect('/auction/user_login')
	return render(request,'sell_page.html')

def add_product(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect('/auction/user_login')
	if 'prod_details' in request.POST:
		prod_details=json.loads(request.POST['prod_details'])
		prod_details['valid_date']=dateutil.parser.parse(prod_details['valid_date'])
		poduct_id=models.product.objects.create(**prod_details).id
	if request.FILES:
		img_path=os.path.join(settings.BASE_DIR,'auction/static/images/product_images',str(poduct_id))
		destination = open(img_path, 'wb+')
		for chunk in request.FILES['image'].chunks():
			destination.write(chunk)
		destination.close()
	return HttpResponse('done')

def buy(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect('/auction/user_login')
	return get_all_products_page()

def get_all_products_page(prod_ids=None):
	context=dict()
	if prod_ids==None:
		products=models.product.objects.all().values()
	else:
		products=models.product.objects.filter(id__in=prod_ids).values()
	product_list=[]
	for p in products:
		if (datetime.datetime.now().replace(tzinfo=None)+datetime.timedelta(hours=5, minutes=30))>p['valid_date'].replace(tzinfo=None):
			continue
		p['image']='/static/images/product_images/'+str(p['id'])
		product_list.append(p)
	context['products']=product_list
	header=['S No.','Product Name','Min Bid','Valid Till','Image','Category']
	context['header']=header		
	
	return render(None,'buy_page.html',context)

def get_meta_fields(model_name):
	fields = model_name._meta.fields
	fields_l=[]
	for field in fields:
		fields_l.append(field.get_attname_column()[0])
	return fields_l

def display_prod(request,prod_id=None):	
	context=dict()
	if prod_id==None:
		prod_id=[request.GET['prod_id']]
	product=models.product.objects.filter(id__in=prod_id).values()[0]
	context['product']=product
	context['no_bid']=False
	if 'no_bid' in request.GET:
		context['no_bid']=True
	return render(None,'product_description_template.html',context)

def make_bid(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect('/auction/user_login')
	data_dict=json.loads(request.GET['data_dict'])
	user_id=request.user.id
	data_dict.update({'user_id':user_id})
	models.bids.objects.create(**data_dict)
	return HttpResponse('done')

def check_your_bids(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect('/auction/user_login')
	user_id=request.user.id	
	bids=models.bids.objects.filter(user_id=user_id)
	context=dict()
	context['user']=request.user
	bids_list=[]
	for b in bids:
		if (datetime.datetime.now().replace(tzinfo=None)+datetime.timedelta(hours=5, minutes=30))>b.product.valid_date.replace(tzinfo=None):
			continue
		bids_list.append(b)
	context['bids']=bids_list
	expired_bids=models.bids.objects.filter(product__valid_date__lte=(datetime.datetime.now().replace(tzinfo=None)+datetime.timedelta(hours=5, minutes=30)))	
	product_dict={}
	for bids in expired_bids:
		if bids.product not in product_dict:
			product_dict[bids.product]={'max_bid':0,'user_id':bids.user.id}
		if product_dict[bids.product]['max_bid']<bids.bid_amount:
			product_dict[bids.product]['max_bid']=bids.bid_amount
			product_dict[bids.product]['user_id']=bids.user.id
	
	successfully_executed_list=[]
	for prod,value in product_dict.items():
		if value['user_id']==user_id:
			successfully_executed_list.append({'product':prod,'bid_amt':value['max_bid']})	
	context['successfully_executed_list']=successfully_executed_list

	return render(None,'check_your_bid.html',context)

def remove_bid(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect('/auction/user_login')
	bid_id=request.GET['bid_id']
	models.bids.objects.filter(id=bid_id).delete()
	return check_your_bids(request)