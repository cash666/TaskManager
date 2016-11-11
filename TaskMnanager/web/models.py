#coding:utf8
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
project_model_choices=(
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
		(u'重要',u'重要'),
		(u'一般',u'一般'),
	)
test_choices=(
		('0',u'否'),
		('1',u'是'),
	)

task_handle_choices=(
		(u'接受',u'接受'),
		(u'拒绝',u'拒绝'),
		(u'转接',u'转接'),
	)

class Tasks(models.Model):
	task_id=models.CharField(max_length=10,unique=True)
	project_model=models.CharField(max_length=64,verbose_name=u'项目模块',choices=project_model_choices)
	task_name=models.ForeignKey('Projects')
	task_title=models.CharField(max_length=32,verbose_name=u'任务标题',null=True,blank=True)
	related_task=models.URLField(max_length=100,verbose_name=u'关联任务',null=True,blank=True)
	task_type=models.CharField(max_length=32,verbose_name=u'任务类型',choices=task_type_choices)
	task_priority=models.CharField(max_length=10,choices=task_priority_choices)
	task_promoter=models.CharField(max_length=32,verbose_name=u'任务发起人')
	task_assign=models.CharField(max_length=32,verbose_name=u'任务指派人',null=True,blank=True)
	task_cc=models.CharField(max_length=32,verbose_name=u'任务抄送人',null=True,blank=True)
	is_test=models.CharField(max_length=5,choices=test_choices)
	start_time=models.DateTimeField(null=True,blank=True)
	end_time=models.DateTimeField(null=True,blank=True)
	task_target=models.CharField(max_length=100,verbose_name=u'任务目标',null=True,blank=True)
	task_description=models.TextField(verbose_name=u'任务描述')
	task_status=models.CharField(max_length=20,default=u'待创建',verbose_name=u'任务状态')
	task_attachment=models.FileField(upload_to='uploads',null=True,blank=True)
	task_history=models.TextField(null=True,blank=True)
	create_time=models.DateTimeField(auto_now_add=True)

	def __unicode__(self):        
                return '%s' % self.task_title

        class Meta:        
                verbose_name = u'任务创建表'        
                verbose_name_plural = u'任务创建表'

class TasksHandle(models.Model):
	task_id=models.CharField(max_length=10,unique=True)
	task_handle_id=models.ForeignKey(Tasks)
        task_promoter=models.CharField(max_length=32,verbose_name=u'任务发起人',null=True,blank=True)
        task_assign=models.CharField(max_length=32,verbose_name=u'任务指派人',null=True,blank=True)
        task_transfer=models.CharField(max_length=32,verbose_name=u'任务转接人',null=True,blank=True)
	task_cc=models.CharField(max_length=32,verbose_name=u'任务抄送人',null=True,blank=True)
	task_cc2=models.CharField(max_length=32,verbose_name=u'任务转接时抄送人',null=True,blank=True)
        task_status=models.CharField(max_length=20,default=u'待接受',verbose_name=u'任务状态')
	start_time=models.DateTimeField(null=True,blank=True)
        end_time=models.DateTimeField(null=True,blank=True)
        finish_time=models.DateTimeField(null=True,blank=True)
	delay_start_time=models.DateTimeField(null=True,blank=True,verbose_name=u'任务设置延迟时的开始时间')
	delay_end_time=models.DateTimeField(null=True,blank=True,verbose_name=u'任务设置延迟时的结束时间')
	is_accept=models.BooleanField(default=0)
	is_reject=models.BooleanField(default=0)
        is_transfer=models.BooleanField(default=0)
        is_delay=models.BooleanField(default=0)
        is_finish=models.BooleanField(default=0)
        is_close=models.BooleanField(default=0)
        task_history=models.TextField(null=True,blank=True)
	task_remark=models.TextField(null=True,blank=True)
	task_attachment=models.FileField(upload_to='uploads',null=True,blank=True)
        create_time=models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
                return '%s------%s' % (self.task_id,self.task_assign)

        class Meta:
                verbose_name = u'任务处理表'
                verbose_name_plural = u'任务处理表'
	
class TaskTemplate(models.Model):
	template_name=models.CharField(max_length=32)
	project_model=models.CharField(max_length=64,verbose_name=u'项目模块')
	task_name=models.CharField(max_length=32,verbose_name=u'任务名称')
	task_title=models.CharField(max_length=32,verbose_name=u'任务标题',null=True,blank=True)
	related_task=models.URLField(max_length=100,verbose_name=u'关联任务',null=True,blank=True)
	task_type=models.CharField(max_length=32,verbose_name=u'任务类型')
	task_priority=models.CharField(max_length=10)
	task_promoter=models.CharField(max_length=32,verbose_name=u'任务发起人')
	task_assign=models.CharField(max_length=32,verbose_name=u'任务指派人',null=True,blank=True)
	task_cc=models.CharField(max_length=32,verbose_name=u'任务抄送人',null=True,blank=True)
	is_test=models.CharField(max_length=5)
	task_target=models.CharField(max_length=100,verbose_name=u'任务目标',null=True,blank=True)
        task_description=models.TextField(verbose_name=u'任务描述')
	task_attachment=models.FileField(upload_to='uploads',null=True,blank=True)
	create_time=models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
                return '%s' % self.template_name

        class Meta:
                verbose_name = u'任务模板表'
                verbose_name_plural = u'任务模板表'

class Projects(models.Model):
	project_model=models.CharField(max_length=64,verbose_name=u'项目模块',choices=project_model_choices)
	project_name=models.CharField(max_length=32,verbose_name=u'项目名称')
	project_type=models.CharField(max_length=32,verbose_name=u'任务类型',choices=task_type_choices)
	project_priority=models.CharField(max_length=10,choices=task_priority_choices)
	start_time=models.DateTimeField(null=True,blank=True)
        end_time=models.DateTimeField(null=True,blank=True)
	project_promoter=models.CharField(max_length=32,verbose_name=u'项目发起人')
	product_leader=models.CharField(max_length=20,null=True,blank=True,verbose_name=u'产品负责人')
	design_leader=models.CharField(max_length=20,null=True,blank=True,verbose_name=u'设计负责人')
	frontend_leader=models.CharField(max_length=20,null=True,blank=True,verbose_name=u'前端负责人')
	backend_leader=models.CharField(max_length=20,null=True,blank=True,verbose_name=u'后端负责人')
	test_leader=models.CharField(max_length=20,null=True,blank=True,verbose_name=u'测试负责人')
	project_participants=models.CharField(max_length=20,null=True,blank=True,verbose_name=u'项目参与者')
	default_cc=models.CharField(max_length=32,verbose_name=u'项目抄送人',null=True,blank=True)
	project_description=models.TextField(verbose_name=u'项目描述')
	project_attachment=models.FileField(upload_to='./uploads/',null=True,blank=True)
	project_status=models.CharField(max_length=10,default=u'待创建',verbose_name=u'项目状态')
	create_time=models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
                return '%s' % self.project_name

        class Meta:
                verbose_name = u'项目表'      
                verbose_name_plural = u'项目表'

class TaskTalk(models.Model):
	talk_name=models.CharField(max_length=32,verbose_name=u'讨论者')
	talk_content=models.TextField(verbose_name=u'讨论内容')
	task_id=models.CharField(max_length=10)
	talk_time=models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
                return '%s-----%s' % (self.talk_name,self.talk_content)

        class Meta:
                verbose_name = u'讨论区'
                verbose_name_plural = u'讨论区'
		ordering=['-talk_time']

class UserInfo(models.Model):
	user=models.OneToOneField(User)
        name=models.CharField(max_length=32)

	def __unicode__(self):
                return self.name

        class Meta:
                verbose_name=u'账户信息'
                verbose_name_plural=u'账户信息'
