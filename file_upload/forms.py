from django import forms

from file_upload.models import picture
from file_upload.models import tag

#from django.contrib.gis.geos import GEOSGeometry
#from django.contrib.gis.db import models
#from django.contrib.gis import forms 

#from simple_autocomplete.widgets import AutoCompleteWidget
from dal import autocomplete

def getChoices():
	T = tag.objects.values('text').distinct()

	x = []
	for g in T:
		for i,k in g.items():
			#print(i)
			x.append((k,k))
	return x

class picture_upload_form(forms.Form):
	pic = forms.FileField(label="select picture")
	vr = forms.DecimalField(label="visual range")
	nearDistance = forms.DecimalField(label="distance to near Target")
	farDistance = forms.DecimalField(label = "distance to far Target")
	location = forms.CharField(label='Location', required=True)
	description = forms.CharField(label='Description', required=True)
	lowColorX = forms.DecimalField(label="Near Object X Coordinate", widget=forms.HiddenInput())
	lowColorY = forms.DecimalField(label="Near Object Y Coordinate", widget=forms.HiddenInput())
	highColorX = forms.DecimalField(label="far Object X Coordinate", widget=forms.HiddenInput())
	highColorY = forms.DecimalField(label="far Object Y Coordinate", widget=forms.HiddenInput())

	#location = forms.DecimalField(label="location")


def getNames():
	qs = tag.objects.all()
	tag_names = []

	for tagy in qs:
		if (tagy.text not in tag_names):
			tag_names.append(tagy.text)
	return tag_names


# The search form for the gallery
class GallerySortForm(forms.Form):


	vr_choices=[(0, "None"), (1,'0-10'),(2,'10-30'), (3,'30-100'), (4,'100-500'), (5,'500+')]
	ascending_choices = [(0,"Ascending time"), (1,"Descending time"), 
	(2,"Ascending visual Range"),(3,"Descending visual Range")]

	ascending = forms.ChoiceField(ascending_choices, label = "Order by:", widget = forms.Select())
   
	visual_range = forms.ChoiceField(choices=vr_choices, label = "Visual Range(in Kilometers):",
		widget= forms.Select(attrs={'id':'vr','name':'Visual Range(in meters)','class':'form-control'}))


   	#auto complete on location
	location = autocomplete.Select2ListChoiceField(required = False, label = "Location:", choice_list = getNames() ,
		widget=autocomplete.ListSelect2(url='location-autocomplete') )

	date1 = forms.CharField(required=False,label = "Beginning date", widget=forms.TextInput( attrs={'id':'date1','name':'date-begin',
		'class':'form-control'}))

	date2 = forms.CharField(required=False,label = "End date", widget=forms.TextInput( attrs={'id':'date2','name':'date-end',
		'class':'form-control'}))



