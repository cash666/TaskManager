#coding:utf8
from django import forms
from web import models

task_handle_choices=(
                ('0',u'接受'),
                ('1',u'拒绝'),
                ('2',u'转接'),
        )

class HandleTaskForm(forms.Form):
	task_id=forms.CharField(widget=forms.HiddenInput())
	task_handle=forms.CharField(widget=forms.widgets.Select(choices=task_handle_choices))
	start_time=forms.DateTimeField(error_messages={'invalid':u'日期格式不正确'},widget=forms.DateTimeInput(),required=False)
	end_time=forms.DateTimeField(error_messages={'invalid':u'日期格式不正确'},widget=forms.DateTimeInput(),required=False)
	task_transfer=forms.CharField(max_length=32,required=False)
	task_cc2=forms.CharField(max_length=32,required=False)
	task_remark=forms.CharField(max_length=512,widget=forms.widgets.Textarea(attrs={'placeholder':u'任务详细描述','rows':5,'cols':50}),required=False)
	task_attachment=forms.FileField(required=False)
