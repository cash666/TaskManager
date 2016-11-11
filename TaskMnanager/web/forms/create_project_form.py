#coding:utf8
from django import forms
from web import models
from web.models import Projects

project_model_choices=(
                (u'2345网址导航',u'2345网址导航'),
                (u'2345软件',u'2345软件'),
                (u'其它',u'其它'),
        )

project_type_choices=(
                (u'需求开发',u'需求开发'),
                (u'版本升级',u'版本升级'),
                (u'行政事务',u'行政事务'),
                (u'人事',u'人事'),
        )

project_priority_choices=(
                (u'紧急',u'紧急'),
                (u'重要',u'重要'),
                (u'一般',u'一般'),
        )

class CreateProjectForm(forms.Form):
	project_model=forms.CharField(widget=forms.widgets.Select(choices=project_model_choices))
	project_name=forms.CharField(max_length=32)
	project_type=forms.CharField(widget=forms.widgets.Select(choices=project_type_choices))
	project_priority=forms.CharField(widget=forms.widgets.Select(choices=project_priority_choices))
	start_time=forms.DateTimeField(error_messages={'invalid':u'日期格式不正确'},widget=forms.DateTimeInput())
	end_time=forms.DateTimeField(error_messages={'invalid':u'日期格式不正确'},widget=forms.DateTimeInput())
	product_leader=forms.CharField(max_length=20,required=False)
	design_leader=forms.CharField(max_length=20,required=False)
	frontend_leader=forms.CharField(max_length=20,required=False)
	backend_leader=forms.CharField(max_length=20,required=False)
	test_leader=forms.CharField(max_length=20,required=False)
	project_participants=forms.CharField(max_length=20,required=False)
	default_cc=forms.CharField(max_length=20,required=False)
	project_description=forms.CharField(required=False,max_length=256,widget=forms.widgets.Textarea(attrs={'class':'form-control ckeditor','placeholder':u'项目详细描述','rows':20}))
	project_attachment=forms.FileField(required=False)
