#coding:utf8
from django import forms
from web import models

task_model_choices=(
                (u'2345网址导航',u'2345网址导航'),
                (u'2345软件',u'2345软件'),
                (u'其它',u'其它'),
        )

task_type_choices=(
                (u'需求开发',u'需求开发'),
                (u'版本升级',u'版本升级'),
                (u'行政事务',u'行政事务'),
                (u'人事',u'人事'),
        )

task_priority_choices=(
                (u'紧急',u'紧急'),
                (u'关键',u'关键'),
                (u'重要',u'重要'),
                (u'一般',u'一般'),
        )
test_choices=(
                ('0',u'否'),
                ('1',u'是'),
        )
class CreateTaskForm(forms.Form):
	project_model=forms.CharField(widget=forms.widgets.Select(choices=task_model_choices))
	task_name=forms.CharField(widget=forms.Select())
	task_title=forms.CharField(max_length=64)
	related_task=forms.URLField(max_length=100,required=False)
	task_type=forms.CharField(widget=forms.widgets.Select(choices=task_type_choices))
	task_priority=forms.CharField(widget=forms.widgets.Select(choices=task_priority_choices))
	start_time=forms.DateTimeField(error_messages={'invalid':u'日期格式不正确'},widget=forms.DateTimeInput())
	end_time=forms.DateTimeField(error_messages={'invalid':u'日期格式不正确'},widget=forms.DateTimeInput())
	task_assign=forms.CharField(max_length=32,required=False)
	task_cc=forms.CharField(max_length=32,required=False)
	is_test=forms.CharField(widget=forms.widgets.Select(choices=test_choices))
	task_target=forms.CharField(max_length=256,widget=forms.widgets.Textarea(attrs={'class':'form-control','rows':6}))
	task_description=forms.CharField(max_length=512,widget=forms.widgets.Textarea(attrs={'class':'form-control ckeditor','placeholder':u'任务详细描述','rows':20}))
	task_attachment=forms.FileField(required=False)

	def __init__(self,*args,**kwargs):
                super(CreateTaskForm,self).__init__(*args,**kwargs)
                self.fields['task_name'].widget.choices=models.Projects.objects.all().values_list('id','project_name')
