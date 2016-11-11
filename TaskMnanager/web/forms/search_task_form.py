#coding:utf8
from django import forms
from web import models

class SearchTaskForm(forms.Form):
	start_time=forms.DateField(error_messages={'invalid':u'日期格式不正确'},widget=forms.DateInput(),required=False)
	end_time=forms.DateField(error_messages={'invalid':u'日期格式不正确'},widget=forms.DateInput(),required=False)
	search_text=forms.CharField(max_length=32,required=False)
