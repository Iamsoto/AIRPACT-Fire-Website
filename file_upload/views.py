from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
import json
from time import time
from base64 import b64decode
from django.core.files.base import ContentFile


from django.shortcuts import render
from django.http import HttpResponse
from file_upload.models import picture
from file_upload.models import tag
from user_profile.models import AuthToken
from user_profile.models import AirpactUser
from user_profile.views import edit_profile
from convos.models import convoPage
from file_upload.forms import picture_upload_form
from django.contrib.auth.decorators import login_required
from convos.models import convoPage


@login_required
def index(request):
	if request.user.is_certified is False:
		return render_to_response('not_certified.html')
	#if there is a file to upload

	if request.method == 'POST':
		form = picture_upload_form(request.POST, request.FILES)
		if form.is_valid():
			newPic = picture(pic = request.FILES['pic'], user=request.user, vr=form.cleaned_data.get('vr'), description=form.cleaned_data.get('description'))
			newPic.save()

			#Creating some conversation stuffs
			conversations = convoPage(picture = newPic)
			conversations.save()

			t = form.cleaned_data['location']

			#20 dollars in my pocket
			newTag = tag(picture = newPic, text = t.lower())
			newTag.save()
			return HttpResponseRedirect(reverse('file_upload.views.index'))
		return render_to_response('index.html', {'form':form}, context_instance=RequestContext(request))
	else:
		form = picture_upload_form()

		return render_to_response(
        'index.html',
        {'form': form},
        context_instance=RequestContext(request))

# used specifically for the android app to send data to this webserver
@csrf_exempt
def upload(request):
	if request.method == 'POST':
		response_data = {}
		s = json.loads(request.body);
		toke = AuthToken.objects.filter(token=s['secretKey'])
		if toke.count() > 0:
			print("USERNAME IS:")
			print(s['user'])
			AuthToken.objects.get(token=s['secretKey']).delete()
			image_data = b64decode(s['image'])
			userob = AirpactUser.objects.get(username=s['user'])

			#create the giant blob of a picture
			newPic = picture(pic = ContentFile(image_data,str(str(time())+".jpg")), 
							description = s['description'], 
							user=userob, 
							vr=s['visualRange'], 
							highColor=int(s['highColor']),
							highX=float(s['highX']), 
							highY=float(s['highY']),
							lowColor=int(s['lowColor']),
							geoX = float(s['geoX']),
							geoY = float(s['geoY'])
							 );

			newPic.save()

			conversations = convoPage(picture = newPic)
			conversations.save()

			#Creating some conversation stuffs
			print(s['tags'])
			tags = s['tags'].split(",")
			for t in tags:
				newTag = tag(picture = newPic, text = t.lower())
				newTag.save()

			#lets make pop some tags yall

			response_data['status'] = 'success'
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		else:
			response_data['status'] = 'keyFailed'
			return HttpResponse(json.dumps(response_data), content_type="application/json")
	else:
		return HttpResponse("For app uploads only")

@login_required
def delete_picture(request, id):
	if request.user.is_certified is False:
		return render_to_response('not_certified.html')
	img = picture.objects.get(id = id)
	print("users id: "+str(request.user.id)+"pictureid:"+str(img.id))
	if request.user.id == img.user.id:
		print("deleteing shit")
		img.delete()
	return edit_profile(request)

def test(request):
	userob = AirpactUser.objects.get(username='JZTD')
	print(userob.id)
	return HttpResponse(userob.id)

def view_picture(request, picId = -1):
	pictures = None
	if picId != -1:
		
		# good picture id
		p = picture.objects.get(id = picId)
		cur_tag = tag.objects.filter(picture= p)
		conversation = convoPage.objects.get(picture = p)

		#THIS NEEDS TO BE LOOKED AT CLOSER, WE ARE GETTIGN ONLY THE FIRST TAG WHICH MIGHT NOT BE THE LOCATION!!!! (but hacked so our demo worked)
		# If the user wants to see more images:
		location = cur_tag[0].text
		picture_tags = tag.objects.filter(text=location).order_by("picture__uploaded")
		pictures = []
		for picture_tag in picture_tags:
			pictures.append(picture_tag.picture)

		#setup range of image numbers for the 

		return render_to_response( 'convos.html', {'picture': p,'pictures':pictures, 'convos':conversation, 
			'convo_id':conversation.pk,'tag':cur_tag[0]}, context_instance=RequestContext(request))


	else:
		return HttpResponseRedirect("/gallery")
		#redirect back to gallery

