#!/usr/bin/env python
#coding:utf8

from django.shortcuts import render,HttpResponse,redirect
from django.utils.safestring import mark_safe
from web.forms import create_project_form,create_task_form,task_handle_form,task_handle2_form,search_task_form
from django.http import StreamingHttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib.auth import authenticate,login,logout
from TaskMnanager import settings
from web import models
import datetime
import calendar
import urllib
import json
import time
import os,sys
import re
# Create your views here.

def check_login():
        '''
        装饰器检查登录
        '''
        def decorator(func):
                def wrapper(request):
                        if request.user.is_authenticated:
                                return func(request)
                        else:
                                return redirect('/')
                return wrapper
        return decorator

def acc_login(request):
        '''
        登录
        '''
        message=''
        if request.method == 'POST':
                username=request.POST.get('username')
                password=request.POST.get('password')
                user=authenticate(username=username,password=password)
                if user is not None:
                        login(request,user)
                        return redirect('/task/index/')
                else:
                        message=u"用户名或密码错误"
        return render(request,'login.html',{'message':message})

def acc_logout(request):
        logout(request)
        return redirect('/')

@check_login()
def index(request):
	accepting_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=0,is_reject=0,is_transfer=0).count()
	handling_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=1,is_finish=0,is_transfer=0).count()
	tasks_count=models.Tasks.objects.filter(Q(task_promoter=request.user.userinfo.name)|Q(task_assign=request.user.userinfo.name)|Q(task_cc__icontains=request.user.userinfo.name)).select_related().count()
	accepting_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=0,is_reject=0,is_transfer=0).select_related().count()
	handling_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=1,is_finish=0,is_transfer=0).select_related().count()
	delaying_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_reject=1).select_related().count()
	return render(request,'index.html',{'accepting_tasks_count':accepting_tasks_count,'':handling_tasks_count,'tasks_count':tasks_count,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'delaying_tasks_count':delaying_tasks_count})

@check_login()
def create_project(request):
	accepting_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=0,is_reject=0,is_transfer=0).count()
	handling_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=1,is_finish=0,is_transfer=0).count()
	CreateProjectForm=create_project_form.CreateProjectForm()
	message=request.GET.get('message','')
	if request.method == 'POST':
		ProjectList=create_project_form.CreateProjectForm(request.POST,request.FILES)
		if ProjectList.is_valid():
			data=ProjectList.clean()
			data['project_promoter']=request.user.userinfo.name
			data['project_status']=u'已创建'
			if data['project_attachment']:
				file_obj=data['project_attachment']
				file_name=file_obj.name
				f=open('uploads/'+file_name,'wb')
				for line in file_obj.chunks():
					f.write(line)
				f.close()
				data['project_attachment']="uploads/%s" % file_name
			start_time=str(data['start_time']).split('+')[0]
                        end_time=str(data['end_time']).split('+')[0]
                        start_timestamp=time.mktime(time.strptime(start_time,'%Y-%m-%d %H:%M:%S'))
                        end_timestamp=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M:%S'))
                        if end_timestamp<=start_timestamp:
                                message=u'任务结束的时间不能小于或者等于开始的时间'
                        else:   
				is_ok=models.Projects.objects.create(**data)
				if is_ok:
					message=u'添加成功'
				else:
					message=u'添加失败'
		return redirect('/task/create_project/?message=%s' % message)
	return render(request,'create_project.html',{'CreateProjectForm':CreateProjectForm,'message':message,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count})

@check_login()
def create_task(request):
	accepting_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=0,is_reject=0,is_transfer=0).count()
	handling_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=1,is_finish=0,is_transfer=0).count()
	CreateTaskForm=create_task_form.CreateTaskForm()
	title=u"新建任务"
	message=request.GET.get('message','')
	template_obj=models.TaskTemplate.objects.filter(task_promoter=request.user.userinfo.name)
	html="<select name='template_name'>"
	html+="<option>%s</option>" % u'选择模板'
	for item in template_obj:
		html+="<option value='%s'>%s</option>" % (item.id,item.template_name)
	html+="</select>"
	t_id=request.GET.get('t_id','')
	if t_id:
		edit_task_obj=models.Tasks.objects.get(task_id=t_id)
		title=u'编辑任务'
	else:
		edit_task_obj=''
	if request.method == 'POST':
		TaskList=create_task_form.CreateTaskForm(request.POST,request.FILES)
		if TaskList.is_valid():
			data=TaskList.clean()
			id_obj=models.Tasks.objects.all().values('id').order_by('-id')[0:1]
			if not id_obj:
				TaskId=1
			else:
				TaskId=id_obj[0]['id']
			TaskId=int(TaskId+1)
			data['task_id']='tk%06d' % TaskId
			task_name_obj=models.Projects.objects.get(id=data['task_name'])
			data['task_name']=task_name_obj
			data['task_promoter']=request.user.userinfo.name
			if data['task_attachment']:
				file_obj=data['task_attachment']
                        	file_name=file_obj.name
                        	f=open('uploads/'+file_name,'wb')
                        	for line in file_obj.chunks():
                                	f.write(line)
                        	f.close()
                        	data['task_attachment']="uploads/%s" % file_name
			data['task_status']=u'已编辑'
			start_time=str(data['start_time']).split('+')[0]
			end_time=str(data['end_time']).split('+')[0]
			start_timestamp=time.mktime(time.strptime(start_time,'%Y-%m-%d %H:%M:%S'))
			end_timestamp=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M:%S'))
			now_timestamp=time.time()
			if start_timestamp<now_timestamp or end_timestamp<now_timestamp:
				message=u'开始时间或结束时间不能小于现在的时间'
			elif end_timestamp<=start_timestamp:
				message=u'任务结束的时间不能小于或者等于开始的时间'
			else:
				is_exists=models.Tasks.objects.filter(task_id=data['task_id'])
				if is_exists:
					last_history=is_exists.all().values_list('task_history')
					if last_history:
						task_history="%s\n" % last_history[0]
						task_history+=u"%s %s编辑了任务" % (time.strftime("%Y-%m-%d %H:%M:%S"),request.user.userinfo.name)
					else:
						task_history=u"%s %s编辑了任务" % (time.strftime("%Y-%m-%d %H:%M:%S"),request.user.userinfo.name)
				else:
					task_history=u"%s %s创建了任务" % (time.strftime("%Y-%m-%d %H:%M:%S"),request.user.userinfo.name)
				data['task_history']=task_history
				is_ok=models.Tasks.objects.create(**data)
				if is_ok:
					message=u'添加成功'
					task_obj=models.Tasks.objects.get(task_id=data['task_id'])
                                	models.TasksHandle.objects.create(task_handle_id=task_obj,task_id=data['task_id'],task_assign=data['task_assign'],task_status=u'待接受',task_promoter=request.user.userinfo.name,task_cc=data['task_cc'])
                        	else:
                                	message=u'添加失败'
                return redirect('/task/create_task/?message=%s' % message)
	return render(request,'create_task.html',{'CreateTaskForm':CreateTaskForm,'html':html,'template_obj':template_obj,'message':message,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'edit_task_obj':edit_task_obj,'title':title})

@check_login()
def create_template(request):
	id=request.GET.get('id','')
	t_id=request.GET.get('t_id','')
	if request.method == 'POST':
		TemplateTaskList=create_task_form.CreateTaskForm(request.POST,request.FILES)
		if TemplateTaskList.is_valid():
			TemplateData={}
			data=TemplateTaskList.clean()
			TemplateData['template_name']=data['task_title']
			TemplateData['project_model']=data['project_model']
			task_name_obj=models.Projects.objects.get(id=data['task_name'])
			TemplateData['task_name']=task_name_obj
			TemplateData['task_title']=data['task_title']
			TemplateData['related_task']=data['related_task']
			TemplateData['task_type']=data['task_type']
			TemplateData['task_priority']=data['task_priority']
			TemplateData['task_promoter']=request.user.userinfo.name
			TemplateData['task_assign']=data['task_assign']
			TemplateData['task_cc']=data['task_cc']
			TemplateData['is_test']=data['is_test']
			TemplateData['task_target']=data['task_target']
			TemplateData['task_description']=data['task_description']
			if data['task_attachment']:
                                file_obj=data['task_attachment']
                                file_name=file_obj.name
                                f=open('uploads/'+file_name,'wb')
                                for line in file_obj.chunks():
                                        f.write(line)
                                f.close()
                                TemplateData['task_attachment']="uploads/%s" % file_name
			is_ok=models.TaskTemplate.objects.create(**TemplateData)
			if is_ok:
				message=u'创建模板成功'
			else:
				message=u'创建模板失败'
		return HttpResponse(message)
	if t_id:
		data={}
		t_obj=models.TaskTemplate.objects.get(id=t_id)
		data['project_model']=t_obj.project_model
		data['task_name']=t_obj.task_name
		data['task_title']=t_obj.task_title
		data['related_task']=t_obj.related_task
		data['task_type']=t_obj.task_type
		data['task_priority']=t_obj.task_priority
		data['task_assign']=t_obj.task_assign
		data['task_cc']=t_obj.task_cc
		data['is_test']=t_obj.is_test
		data['task_target']=t_obj.task_target
		data['task_description']=t_obj.task_description
		json_data=json.dumps(data)
		return HttpResponse(json_data)
	if id:
		is_ok=models.TaskTemplate.objects.filter(id=id).delete()
		if is_ok:
			ret=u'删除成功'
		else:
			ret=u'删除失败'
		return HttpResponse(ret)

@check_login()
def accepting_task(request):
	accepting_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=0,is_reject=0,is_transfer=0).count()
	handling_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=1,is_finish=0,is_transfer=0).count()
	accepting_task_obj=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=0,is_reject=0,is_transfer=0)
	if accepting_task_obj:
		for item in accepting_task_obj:
			task_obj=models.Tasks.objects.filter(task_id=item.task_id)
			for item2 in task_obj:
				task_title=item2.task_title
				task_assign=item2.task_assign
				task_priority=item2.task_priority
        			task_type=item2.task_type
        			task_promoter=item2.task_promoter
				start_time=item2.start_time
				end_time=item2.end_time
				return render(request,'accepting_task.html',{'accepting_task_obj':accepting_task_obj,'task_title':task_title,'task_promoter':task_promoter,'end_time':end_time,'task_priority':task_priority,'task_type':task_type,'task_assign':task_assign,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count})
	else:
		return render(request,'accepting_task.html',{'accepting_task_obj':accepting_task_obj,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count})

@check_login()
def show_accepting_task(request):
	accepting_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=0,is_reject=0,is_transfer=0).count()
	handling_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=1,is_finish=0,is_transfer=0).count()
	task_id=request.GET.get('t_id','')
	HandleTaskForm=task_handle_form.HandleTaskForm()
	show_accepting_task_obj=models.TasksHandle.objects.filter(Q(task_assign=request.user.userinfo.name) | Q(task_cc__icontains=request.user.userinfo.name) | Q(task_promoter=request.user.userinfo.name) | Q(task_transfer=request.user.userinfo.name),task_id=task_id,task_status=u'待接受')
	html=""
	if task_id:
		is_ok=models.TaskTalk.objects.filter(task_id=task_id)
		if is_ok:
			talk_task_obj=models.TaskTalk.objects.filter(task_id=task_id)
			for item in talk_task_obj:
                        	html+="<div style='width:200px;border:1px solid blue;margin-top:2px'>"
                        	html+="<p style='font-size:4px;'>"+item.talk_name+":</p>"
                        	html+="<p style='font-weight:bold'>"+item.talk_content+"</p>"
                                html+="<p style='font-size:4px;margin-left:80px'>"+str(item.talk_time).split('+')[0]+"</p>"
                                html+="</div>"
	for item in show_accepting_task_obj:
		task_obj=models.Tasks.objects.get(task_id=task_id)
		task_priority=task_obj.task_priority
		task_title=task_obj.task_title
		task_type=task_obj.task_type
		task_promoter=task_obj.task_promoter
		task_assign=task_obj.task_assign
		task_cc=task_obj.task_cc
		task_description=task_obj.task_description
		task_attachment=task_obj.task_attachment
		start_time=task_obj.start_time
		end_time=task_obj.end_time
		start_time2=str(start_time).split('+')[0]
                end_time2=str(end_time).split('+')[0]
                start_timestamp=time.mktime(time.strptime(start_time2,'%Y-%m-%d %H:%M:%S'))
                end_timestamp=time.mktime(time.strptime(end_time2,'%Y-%m-%d %H:%M:%S'))
		time_delta=end_timestamp-start_timestamp
		task_attachment=task_obj.task_attachment
		hour="%.2f" % (float(time_delta)/3600)
	create_task_history_obj=models.Tasks.objects.get(task_id=task_id)
	#handle_task_history_obj=models.TasksHandle.objects.get(task_id=task_id)
	return render(request,'show_accepting_task.html',{'show_accepting_task_obj':show_accepting_task_obj,'hour':hour,'task_priority':task_priority,'task_type':task_type,'task_promoter':task_promoter,'task_assign':task_assign,'task_cc':task_cc,'task_attachment':task_attachment,'start_time':start_time,'end_time':end_time,'task_title':task_title,'task_description':task_description,'HandleTaskForm':HandleTaskForm,'create_task_history_obj':create_task_history_obj,'accepting_tasks_count':accepting_tasks_count,'task_id':task_id,'handling_tasks_count':handling_tasks_count,'html':mark_safe(html)})

def download(request):
	'''
	下载附件
	'''
	def file_iterator(file_name, chunk_size=512):
        	with open(file_name) as f:
            		while True:
                		c = f.read(chunk_size)
                		if c:
                    			yield c
                		else:
                    			break
	t_id=request.GET.get('t_id','')
	download_task_obj=models.Tasks.objects.filter(task_assign=request.user.userinfo.name,task_id=t_id)
	for item in download_task_obj:
		file_name=item.task_attachment.name
	file_name=u"%s/%s" % (settings.BASE_DIR,file_name)
	response = StreamingHttpResponse(file_iterator(file_name))
	response['Content-Type'] = 'application/octet-stream'
	response['Content-Disposition'] = 'attachment;filename="{0}"'.format(os.path.basename(file_name).encode('utf8'))
	return response

@check_login()
def handle_task(request):
	'''
	处理任务
	'''
	if request.method == 'POST':
		if request.POST.get('status') == 'close':
			task_id=request.POST.get('task_id')
			is_exists=models.TasksHandle.objects.filter(task_id=task_id)
                        if is_exists:
				last_history=is_exists.all().values_list('task_history')
                                if last_history:
					task_history="%s\n" % last_history[0]
					task_history+=u"%s %s关闭了任务,备注:按期完成" % (time.strftime("%Y-%m-%d %H:%M:%S"),request.user.userinfo.name)
					is_ok=models.TasksHandle.objects.filter(task_id=task_id).update(task_status=u'已关闭',task_history=task_history,is_close='1')
					if is_ok:
						return HttpResponse('关闭任务成功')
		HandleTaskForm=task_handle_form.HandleTaskForm(request.POST,request.FILES)
		if HandleTaskForm.is_valid():
			data=HandleTaskForm.clean()
			if data['task_handle'] == '0':
				start_time=str(data['start_time']).split('+')[0]
                		end_time=str(data['end_time']).split('+')[0]
				start_timestamp=time.mktime(time.strptime(start_time,'%Y-%m-%d %H:%M:%S'))
                        	end_timestamp=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M:%S'))
                        	now_timestamp=time.time()
				task_obj=models.Tasks.objects.get(task_id=data['task_id'])
				old_start_time=task_obj.start_time
				old_end_time=task_obj.end_time
				old_start_time=str(old_start_time).split('+')[0]
                		old_end_time=str(old_end_time).split('+')[0]
				old_start_timestamp=time.mktime(time.strptime(old_start_time,'%Y-%m-%d %H:%M:%S'))
                                old_end_timestamp=time.mktime(time.strptime(old_end_time,'%Y-%m-%d %H:%M:%S'))
				if start_timestamp > old_end_timestamp or start_timestamp < old_start_timestamp or end_timestamp > old_end_timestamp or end_timestamp<old_start_timestamp:
					message=u'工期请设置在该任务提交时设置的工期之内'
					return redirect('/task/show_accepting_task/?t_id=%s&message=%s' % (data['task_id'],message))
                        	if start_timestamp<now_timestamp or end_timestamp<now_timestamp:
                                	message=u'开始时间或结束时间不能小于现在的时间'
					return redirect('/task/show_accepting_task/?t_id=%s&message=%s' % (data['task_id'],message))
                        	elif end_timestamp<=start_timestamp:
                                	message=u'任务结束的时间不能小于或者等于开始的时间'
					return redirect('/task/show_accepting_task/?t_id=%s&message=%s' % (data['task_id'],message))
				else:
					if data['task_remark']:
						task_history=u"%s %s接受了任务,工期设置为%s 至 %s,备注:%s" % (time.strftime("%Y-%m-%d %H:%M:%S"),request.user.userinfo.name,start_time,end_time,data['task_remark'])
						is_ok=models.TasksHandle.objects.filter(task_id=data['task_id']).update(task_status=u'解决中',is_accept=1,task_history=task_history,task_remark=data['task_remark'],start_time=data['start_time'],end_time=data['end_time'])
					else:
						task_history=u"%s %s接受了任务,工期设置为%s 至 %s" % (time.strftime("%Y-%m-%d %H:%M:%S"),request.user.userinfo.name,start_time,end_time)
						is_ok=models.TasksHandle.objects.filter(task_id=data['task_id']).update(task_status=u'解决中',is_accept=1,task_history=task_history,start_time=data['start_time'],end_time=data['end_time'])
					if is_ok:
						return redirect('/task/show_handling_task/?t_id=%s' % data['task_id'])
			elif data['task_handle'] == '1':
				if data['task_remark']:
					task_history=u"%s %s拒绝了任务,备注:%s" % (time.strftime("%Y-%m-%d %H:%M:%S"),request.user.userinfo.name,data['task_remark'])
					is_ok=models.TasksHandle.objects.filter(task_id=data['task_id']).update(task_status=u'已拒绝',is_reject=1,task_history=task_history,task_remark=data['task_remark'])
				else:
					task_history=u"%s %s拒绝了任务" % (time.strftime("%Y-%m-%d %H:%M:%S"),request.user.userinfo.name)
					is_ok=models.TasksHandle.objects.filter(task_id=data['task_id']).update(task_status=u'已拒绝',is_reject=1,task_history=task_history)
				if is_ok:
					return redirect('/task/show_handling_task/?t_id=%s' % data['task_id'])
			else:
				if not data['task_transfer']:
					message=u'请填写转接人';
					return redirect('/task/show_accepting_task/?t_id=%s&message=%s' % (data['task_id'],message))
				else:
					if data['task_attachment']:
						file_obj=data['task_attachment']
						file_name=file_obj.name
						f=open('uploads/'+file_name,'wb')
						for line in file_obj.chunks():
							f.write(line)
						f.close()
						data['task_attachment']="uploads/%s" % file_name
					if data['task_remark']:
						task_history=u"%s %s转接任务给了%s,备注:%s" % (time.strftime("%Y-%m-%d %H:%M:%S"),request.user.userinfo.name,data['task_transfer'],data['task_remark'])
                                        	is_ok=models.TasksHandle.objects.filter(task_id=data['task_id']).update(task_status=u'已转接',is_transfer=1,task_history=task_history,task_remark=data['task_remark'],task_cc2=data['task_cc2'],task_transfer=data['task_transfer'])
					else:
						task_history=u"%s %s转接任务给了%s" % (time.strftime("%Y-%m-%d %H:%M:%S"),request.user.userinfo.name,data['task_transfer'])
                                                is_ok=models.TasksHandle.objects.filter(task_id=data['task_id']).update(task_status=u'已转接',is_transfer=1,task_history=task_history,task_cc2=data['task_cc2'],task_transfer=data['task_transfer'])
					if is_ok:
						return redirect('/task/show_handling_task/?t_id=%s' % data['task_id'])
		#else:
		#	error_msg=HandleTaskForm.errors
		#	return HttpResponse(error_msg)

@check_login()
def handling_task(request):
	handling_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=1,is_finish=0,is_transfer=0).count()
	accepting_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=0,is_reject=0,is_transfer=0).count()
        handling_task_obj=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=1,is_finish=0,is_transfer=0)
        if handling_task_obj:
                for item in handling_task_obj:
                        task_obj=models.Tasks.objects.filter(task_id=item.task_id)
                        for item2 in task_obj:
                                task_title=item2.task_title
                                task_assign=item2.task_assign
                                task_priority=item2.task_priority
                                task_type=item2.task_type
                                task_promoter=item2.task_promoter
                                start_time=item2.start_time
                                end_time=item2.end_time
                                return render(request,'handling_task.html',{'handling_task_obj':handling_task_obj,'task_title':task_title,'task_promoter':task_promoter,'end_time':end_time,'task_priority':task_priority,'task_type':task_type,'task_assign':task_assign,'handling_tasks_count':handling_tasks_count,'accepting_tasks_count':accepting_tasks_count})
        else:
                return render(request,'handling_task.html',{'handling_task_obj':handling_task_obj,'handling_tasks_count':handling_tasks_count,'accepting_tasks_count':accepting_tasks_count})

@check_login()
def show_handling_task(request):
        accepting_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=0,is_reject=0,is_transfer=0).count()
        handling_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=1,is_finish=0,is_transfer=0).count()
        task_id=request.GET.get('t_id','')
	is_finished=request.GET.get('is_finished','')
	is_closed='0'
        HandleTaskForm2=task_handle2_form.HandleTaskForm2()
        show_handling_task_obj=models.TasksHandle.objects.filter(Q(task_status=u'解决中') | Q(task_status=u'已解决') | Q(task_status=u'已拒绝') | Q(task_status=u'已转接') | Q(task_status=u'已延迟') | Q(task_status=u'已关闭'),task_id=task_id)
        show_handled_task_obj=models.TasksHandle.objects.filter(Q(task_status=u'已解决') | Q(task_status=u'已拒绝') | Q(task_status=u'已转接') | Q(task_status=u'已关闭'),task_id=task_id)
        show_handled_task_obj2=models.TasksHandle.objects.filter(Q(task_status=u'已关闭'),task_id=task_id)
	create_task_history_obj=models.Tasks.objects.get(task_id=task_id)
        handle_task_history_obj=models.TasksHandle.objects.get(task_id=task_id)
	html=""
        if task_id:
                is_ok=models.TaskTalk.objects.filter(task_id=task_id)
                if is_ok:
                        talk_task_obj=models.TaskTalk.objects.filter(task_id=task_id)
                        for item in talk_task_obj:
                                html+="<div style='width:200px;border:1px solid blue;margin-top:2px'>"
                                html+="<p style='font-size:4px;'>"+item.talk_name+":</p>"
                                html+="<p style='font-weight:bold'>"+item.talk_content+"</p>"
                                html+="<p style='font-size:4px;margin-left:80px'>"+str(item.talk_time).split('+')[0]+"</p>"
                                html+="</div>"
	if show_handling_task_obj:
	        for item in show_handling_task_obj:
			if show_handled_task_obj:
				is_finished='1'
			if show_handled_task_obj2:
				is_closed='1'
	                task_obj=models.Tasks.objects.get(task_id=task_id)
	                task_priority=task_obj.task_priority
	                task_title=task_obj.task_title
	                task_type=task_obj.task_type
	                task_promoter=task_obj.task_promoter
	                task_cc=task_obj.task_cc
	                task_description=task_obj.task_description
	                task_attachment=task_obj.task_attachment
	                start_time=task_obj.start_time
	                end_time=task_obj.end_time
	                start_time2=str(start_time).split('+')[0]
	                end_time2=str(end_time).split('+')[0]
	                start_timestamp=time.mktime(time.strptime(start_time2,'%Y-%m-%d %H:%M:%S'))
	                end_timestamp=time.mktime(time.strptime(end_time2,'%Y-%m-%d %H:%M:%S'))
	                time_delta=end_timestamp-start_timestamp
	                task_attachment=task_obj.task_attachment
	                hour="%.2f" % (float(time_delta)/3600)
		return render(request,'show_handling_task.html',{'show_handling_task_obj':show_handling_task_obj,'hour':hour,'task_priority':task_priority,'task_type':task_type,'task_promoter':task_promoter,'task_cc':task_cc,'task_attachment':task_attachment,'start_time':start_time,'end_time':end_time,'task_title':task_title,'task_description':task_description,'create_task_history_obj':create_task_history_obj,'handle_task_history_obj':handle_task_history_obj,'accepting_tasks_count':accepting_tasks_count,'task_id':task_id,'handling_tasks_count':handling_tasks_count,'HandleTaskForm2':HandleTaskForm2,'is_finished':is_finished,'is_closed':is_closed,'html':mark_safe(html)})

@check_login()
def handle_accepting_task(request):
	if request.method == 'POST':
		if request.FILES:
			HandleTaskForm2=task_handle2_form.HandleTaskForm2(request.POST,request.FILES)
		else:
			HandleTaskForm2=task_handle2_form.HandleTaskForm2(request.POST)
		if HandleTaskForm2.is_valid():
			data=HandleTaskForm2.clean()
			task_id=data['task_id']
                        task_obj=models.TasksHandle.objects.get(task_id=task_id)
                        task_history="%s\n" % task_obj.task_history
			if data['task_handle'] == '0':
				if data['task_remark']:
					task_history+=u"%s %s解决了任务,备注:%s" % (time.strftime("%Y-%m-%d %H:%M:%S"),request.user.userinfo.name,data['task_remark'])
					is_ok=models.TasksHandle.objects.filter(task_id=task_id).update(task_remark=data['task_remark'],task_history=task_history,task_status=u'已解决',is_finish=1,finish_time=time.strftime("%Y-%m-%d %H:%M:%S"))
				else:
					task_history+=u"%s %s解决了任务" % (time.strftime("%Y-%m-%d %H:%M:%S"),request.user.userinfo.name)
					is_ok=models.TasksHandle.objects.filter(task_id=task_id).update(task_history=task_history,task_status=u'已解决',is_finish=1,finish_time=time.strftime("%Y-%m-%d %H:%M:%S"))
				if is_ok:
					return redirect('/task/show_handling_task/?t_id=%s&is_finished=1' % task_id)
			elif data['task_handle'] == '2':
                                if data['task_remark']:
					task_history+=u"%s %s不予解决此任务,备注:%s" % (time.strftime("%Y-%m-%d %H:%M:%S"),request.user.userinfo.name,data['task_remark'])
                                        is_ok=models.TasksHandle.objects.filter(task_id=task_id).update(task_remark=data['task_remark'],task_history=task_history,task_status=u'已解决',is_finish=1)
                                else:
					task_history+=u"%s %s不予解决此任务" % (time.strftime("%Y-%m-%d %H:%M:%S"),request.user.userinfo.name,data['task_remark'])
                                        is_ok=models.TasksHandle.objects.filter(task_id=task_id).update(task_history=task_history,task_status=u'已解决',is_finish=1)
                                if is_ok:
                                        return redirect('/task/show_handling_task/?t_id=%s&is_finished=1' % task_id)
			elif data['task_handle'] == '1':
				if not data['start_time'] or not data['end_time']:
					message=u'请填写工期时间';
                                        return redirect('/task/show_handling_task/?t_id=%s&message=%s' % (data['task_id'],message))
				else:
					data['start_time']=str(data['start_time']).split('+')[0]
                        		data['end_time']=str(data['end_time']).split('+')[0]
					if data['task_remark']:
						task_history+=u"%s %s修改了工期，工期设置为%s 至 %s，备注:%s" % (time.strftime("%Y-%m-%d %H:%M:%S"),request.user.userinfo.name,data['start_time'],data['end_time'],data['task_remark'])
						is_ok=models.TasksHandle.objects.filter(task_id=task_id).update(task_history=task_history,task_status=u'已延迟',is_delay=1,delay_start_time=data['start_time'],delay_end_time=data['end_time'],task_remark=data['task_remark'])
					else:
						task_history+=u"%s %s修改了工期，工期设置为%s 至 %s" % (time.strftime("%Y-%m-%d %H:%M:%S"),request.user.userinfo.name,data['start_time'],data['end_time'])
						is_ok=models.TasksHandle.objects.filter(task_id=task_id).update(task_history=task_history,task_status=u'已延迟',is_delay=1,delay_start_time=data['start_time'],delay_end_time=data['end_time'])
					if is_ok:
						 return redirect('/task/show_handling_task/?t_id=%s' % task_id)
			elif data['task_handle'] == '3':
				if not data['task_assign']:
					message=u'请指定转接人'
					return redirect('/task/show_handling_task/?t_id=%s&message=%s' % (data['task_id'],message))
				else:
					if data['task_attachment']:
						file_obj=data['task_attachment']
                                		file_name=file_obj.name
                                		f=open('uploads/'+file_name,'wb')
                                		for line in file_obj.chunks():
                                        		f.write(line)
                                		f.close()
                                		data['task_attachment']="uploads/%s" % file_name
					if data['task_remark']:
						task_history+=u"%s %s转接任务给了%s,备注:%s" % (time.strftime("%Y-%m-%d %H:%M:%S"),request.user.userinfo.name,data['task_assign'],data['task_remark'])
						is_ok=models.TasksHandle.objects.filter(task_id=task_id).update(task_history=task_history,task_status=u'已转接',is_transfer=1,task_transfer=data['task_assign'],task_cc2=data['task_cc'],task_attachment=data['task_attachment'],task_remark=data['task_remark'])
					else:
						task_history+=u"%s %s转接任务给了%s" % (time.strftime("%Y-%m-%d %H:%M:%S"),request.user.userinfo.name,data['task_assign'])
						is_ok=models.TasksHandle.objects.filter(task_id=task_id).update(task_history=task_history,task_status=u'已转接',is_transfer=1,task_transfer=data['task_assign'],task_cc2=data['task_cc'],task_attachment=data['task_attachment'])
					if is_ok:
						return redirect('/task/show_handling_task/?t_id=%s' % task_id)

@check_login()
def list_all_task(request):
	accepting_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=0,is_reject=0,is_transfer=0).count()
        handling_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=1,is_finish=0,is_transfer=0).count()
	all_task_list=models.Tasks.objects.filter(Q(task_promoter=request.user.userinfo.name)|Q(task_assign=request.user.userinfo.name)|Q(task_cc__icontains=request.user.userinfo.name))
	searchTaskForm=search_task_form.SearchTaskForm()
	search_time=request.GET.get('search','')
	if request.method == 'POST':
                if request.POST.get('status_text',''):
                        status_text=request.POST['status_text']
                        status_text=u'%s' % status_text
                        task_status_obj=models.TasksHandle.objects.filter(task_status=status_text)
                        html="";
                        count=0;
                        for item in task_status_obj:
                                list_task_obj=models.Tasks.objects.filter(task_id=item.task_id)
                                for item2 in list_task_obj:
                                        task_title=item2.task_title
                                        task_promoter=item2.task_promoter
                                        task_assign=item2.task_assign
                                        create_time=item2.create_time
                                        end_time=item2.end_time
                                        task_priority=item2.task_priority
                                        task_type=item2.task_type
                                        count+=1;
                                        html+='<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td> <a onclick="show_task(this)">%s</a></td></tr>' % (count,item.task_id,task_title,task_promoter,task_assign,create_time,end_time,status_text,task_priority,task_type,u'查看')
                        return HttpResponse(mark_safe(html))
		elif request.POST.get('sub',''):
                        if not request.POST['start_time'] and not request.POST['end_time'] and not request.POST['search_text']:
                                message=u'搜索内容不能为空'
                                return redirect('/task/all_task/?message=%s' % message)
                        elif request.POST['start_time'] and request.POST['end_time'] and not request.POST['search_text']:
                                start_time=request.POST['start_time']
                                end_time=request.POST['end_time']
                                start_time="%s 00:00:00" % start_time
                                end_time="%s 00:00:00" % end_time
                                start_timestamp=time.mktime(time.strptime(start_time,'%Y-%m-%d %H:%M:%S'))
                                end_timestamp=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M:%S'))
                                start=datetime.datetime.fromtimestamp(start_timestamp)
                                end=datetime.datetime.fromtimestamp(end_timestamp)
                                search_task_obj=models.Tasks.objects.filter(Q(create_time__gte=start)&Q(create_time__lte=end))
                                return render(request,'all_task.html',{'search_task_obj':search_task_obj,'searchTaskForm':searchTaskForm,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count})
                        elif request.POST['start_time'] and not request.POST['end_time'] and not request.POST['search_text']:
                                start_time=request.POST['start_time']
                                start_time="%s 00:00:00" % start_time
                                start_timestamp=time.mktime(time.strptime(start_time,'%Y-%m-%d %H:%M:%S'))
                                start=datetime.datetime.fromtimestamp(start_timestamp)
                                search_task_obj2=models.Tasks.objects.filter(Q(create_time__gte=start))
                                return render(request,'all_task.html',{'search_task_obj2':search_task_obj2,'searchTaskForm':searchTaskForm,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count})
                        elif not request.POST['start_time'] and request.POST['end_time'] and not request.POST['search_text']:
                                end_time=request.POST['end_time']
                                end_time="%s 00:00:00" % end_time
                                end_timestamp=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M:%S'))
                                end=datetime.datetime.fromtimestamp(end_timestamp)
                                search_task_obj3=models.Tasks.objects.filter(Q(create_time__lte=end))
                                return render(request,'all_task.html',{'search_task_obj3':search_task_obj3,'searchTaskForm':searchTaskForm,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count})
                        elif not request.POST['start_time'] and not request.POST['end_time'] and request.POST['search_text']:
                                search_text=request.POST['search_text']
                                search_task_obj4=models.Tasks.objects.filter(Q(task_id__icontains=search_text) | Q(task_title__icontains=search_text) | Q(task_promoter__icontains=search_text) | Q(task_assign__icontains=search_text) | Q(task_priority__icontains=search_text) | Q(task_type__icontains=search_text))
                                return render(request,'all_task.html',{'search_task_obj4':search_task_obj4,'searchTaskForm':searchTaskForm,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count})
	if search_time:
		return search_tasks(request,search_time)
	else:
        	return render(request,'all_task.html',{'all_task_list':all_task_list,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'searchTaskForm':searchTaskForm})

def search_tasks(request,search_time,p_id=None):
	accepting_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=0,is_reject=0,is_transfer=0).count()
        handling_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=1,is_finish=0,is_transfer=0).count()
	searchTaskForm=search_task_form.SearchTaskForm()
        if search_time == 'all':
		if p_id:
			task_list_obj=models.Tasks.objects.filter(task_name_id=p_id)
			return render(request,'participated_task.html',{'task_list_obj':task_list_obj,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'p_id':p_id,'searchTaskForm':searchTaskForm})
		else:
                	all_task_list=models.Tasks.objects.filter(task_promoter=request.user.userinfo.name)
			return render(request,'all_task.html',{'all_task_list':all_task_list,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'searchTaskForm':searchTaskForm})
        elif search_time == 'this_week':
                dayOfWeek = datetime.datetime.now().weekday()
                if dayOfWeek == 0:
                        Monday = (datetime.datetime.now() - datetime.timedelta(days = 7))
                else:
                        Monday=(datetime.datetime.now() - datetime.timedelta(days = int(dayOfWeek)))
                now_time=datetime.datetime.today()
		if p_id:
			this_week_obj=models.Tasks.objects.filter(Q(create_time__lte=now_time)&Q(create_time__gte=Monday)&Q(task_name_id=p_id))
			return render(request,'participated_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'this_week_obj':this_week_obj,'p_id':p_id,'searchTaskForm':searchTaskForm})
		else:
                	this_week_obj=models.Tasks.objects.filter(Q(create_time__lte=now_time)&Q(create_time__gte=Monday))
                	return render(request,'all_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'this_week_obj':this_week_obj,'searchTaskForm':searchTaskForm})
        elif search_time == 'last_week':
                dayOfWeek = datetime.datetime.now().weekday()
                if dayOfWeek == 0:
                        sunday = (datetime.datetime.now() - datetime.timedelta(days = 7))
                        Monday=(datetime.datetime.now() - datetime.timedelta(days = 14))
                else:
                        sunday = (datetime.datetime.now() - datetime.timedelta(days = int(dayOfWeek)))
                        Monday=(datetime.datetime.now() - datetime.timedelta(days = int(dayOfWeek+7)))
		if p_id:
                	last_week_obj=models.Tasks.objects.filter(Q(create_time__lte=sunday)&Q(create_time__gte=Monday)&Q(task_name_id=p_id))
			return render(request,'participated_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'last_week_obj':last_week_obj,'p_id':p_id,'searchTaskForm':searchTaskForm})
		else:
                	last_week_obj=models.Tasks.objects.filter(Q(create_time__lte=sunday)&Q(create_time__gte=Monday))
                	return render(request,'all_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'last_week_obj':last_week_obj,'searchTaskForm':searchTaskForm})
        elif search_time == 'this_month':
                day_now = time.localtime()
                wday, days = calendar.monthrange(day_now.tm_year, day_now.tm_mon)
                month_begin = '%d-%02d-01 00:00:00' % (day_now.tm_year, day_now.tm_mon)
                month_end='%d-%02d-01 00:00:00' % (day_now.tm_year,day_now.tm_mon+1)
                month_begin_timestamp=time.mktime(time.strptime(month_begin,'%Y-%m-%d %H:%M:%S'))
                month_end_timestamp=time.mktime(time.strptime(month_end,'%Y-%m-%d %H:%M:%S'))
                start=datetime.datetime.fromtimestamp(month_begin_timestamp)
                end=datetime.datetime.fromtimestamp(month_end_timestamp)
		if p_id:
			this_month_obj=models.Tasks.objects.filter(Q(create_time__gte=start)&Q(create_time__lte=end)&Q(task_name_id=p_id))
                	return render(request,'participated_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'this_month_obj':this_month_obj,'p_id':p_id,'searchTaskForm':searchTaskForm})
		else:
                	this_month_obj=models.Tasks.objects.filter(Q(create_time__gte=start)&Q(create_time__lte=end))
                	return render(request,'all_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'this_month_obj':this_month_obj,'searchTaskForm':searchTaskForm})
        elif search_time == 'last_month':
                day_now = time.localtime()
                wday, days = calendar.monthrange(day_now.tm_year, day_now.tm_mon)
                month_begin = '%d-%02d-01 00:00:00' % (day_now.tm_year, day_now.tm_mon-1)
                month_end='%d-%02d-01 00:00:00' % (day_now.tm_year,day_now.tm_mon)
                month_begin_timestamp=time.mktime(time.strptime(month_begin,'%Y-%m-%d %H:%M:%S'))
                month_end_timestamp=time.mktime(time.strptime(month_end,'%Y-%m-%d %H:%M:%S'))
                start=datetime.datetime.fromtimestamp(month_begin_timestamp)
                end=datetime.datetime.fromtimestamp(month_end_timestamp)
		if p_id:
			last_month_obj=models.Tasks.objects.filter(Q(create_time__gte=start)&Q(create_time__lte=end)&Q(task_name_id=p_id))
                	return render(request,'participated_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'last_month_obj':last_month_obj,'p_id':p_id,'searchTaskForm':searchTaskForm})
		else:
                	last_month_obj=models.Tasks.objects.filter(Q(create_time__gte=start)&Q(create_time__lte=end))
                	return render(request,'all_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'last_month_obj':last_month_obj,'searchTaskForm':searchTaskForm})
	elif search_time == 'lauched_from_me':
		if p_id:
			lauched_from_me_obj=models.Tasks.objects.filter(Q(task_promoter=request.user.userinfo.name)&Q(task_name_id=p_id))
                        return render(request,'participated_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'lauched_from_me_obj':lauched_from_me_obj,'p_id':p_id,'searchTaskForm':searchTaskForm})
		else:
			lauched_from_me_obj=models.Tasks.objects.filter(task_promoter=request.user.userinfo.name)
			return render(request,'all_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'lauched_from_me_obj':lauched_from_me_obj,'searchTaskForm':searchTaskForm})
	elif search_time == 'assign_to_me':
		if p_id:
			assign_to_me_obj=models.Tasks.objects.filter(Q(task_assign=request.user.userinfo.name) & Q(task_name_id=p_id))
                	return render(request,'participated_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'assign_to_me_obj':assign_to_me_obj,'p_id':p_id,'searchTaskForm':searchTaskForm})
		else:
			assign_to_me_obj=models.Tasks.objects.filter(task_assign=request.user.userinfo.name)
			return render(request,'all_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'assign_to_me_obj':assign_to_me_obj,'searchTaskForm':searchTaskForm})
	elif search_time == 'cc_to_me':
		if p_id:
			cc_to_me_obj=models.Tasks.objects.filter(Q(task_cc__icontains=request.user.userinfo.name)&Q(task_name_id=p_id))
                	return render(request,'participated_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'cc_to_me_obj':cc_to_me_obj,'p_id':p_id,'searchTaskForm':searchTaskForm})
		else:
			cc_to_me_obj=models.Tasks.objects.filter(task_cc__icontains=request.user.userinfo.name)
			return render(request,'all_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'cc_to_me_obj':cc_to_me_obj,'searchTaskForm':searchTaskForm})
	else:
		if p_id:
			transfer_by_me_obj=models.TasksHandle.objects.filter(Q(is_transfer='1') & Q(task_assign=request.user.userinfo.name) & Q(task_handle_id__task_name_id=p_id))
                	return render(request,'participated_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'transfer_by_me_obj':transfer_by_me_obj,'p_id':p_id,'searchTaskForm':searchTaskForm})
		else:
			transfer_by_me_obj=models.TasksHandle.objects.filter(Q(is_transfer='1') & Q(task_assign=request.user.userinfo.name))
			return render(request,'all_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'transfer_by_me_obj':transfer_by_me_obj,'searchTaskForm':searchTaskForm})
		
@check_login()
def list_participated_task(request):
	accepting_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=0,is_reject=0,is_transfer=0).count()
        handling_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=1,is_finish=0,is_transfer=0).count()
	searchTaskForm=search_task_form.SearchTaskForm()
	p_id=request.GET.get('p_id','')
	search_time=request.GET.get('search','')
	if request.POST.get('sub',''):
		p_id=int(request.POST.get('p_id',''))
		if not request.POST['start_time'] and not request.POST['end_time'] and not request.POST['search_text']:
                	message=u'搜索内容不能为空'
                        return redirect('/task/participated_task/?p_id=%d&message=%s' % (p_id,message))
		elif request.POST['start_time'] and request.POST['end_time'] and not request.POST['search_text']:
                        start_time=request.POST['start_time']
                        end_time=request.POST['end_time']
                        start_time="%s 00:00:00" % start_time
                        end_time="%s 00:00:00" % end_time
                        start_timestamp=time.mktime(time.strptime(start_time,'%Y-%m-%d %H:%M:%S'))
                        end_timestamp=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M:%S'))
                        start=datetime.datetime.fromtimestamp(start_timestamp)
                        end=datetime.datetime.fromtimestamp(end_timestamp)
                        search_task_obj=models.Tasks.objects.filter(Q(task_promoter=request.user.userinfo.name)|Q(task_assign=request.user.userinfo.name)|Q(task_cc__icontains=request.user.userinfo.name),task_name_id=p_id,create_time__gte=start,create_time__lte=end)
                        return render(request,'participated_task.html',{'search_task_obj':search_task_obj,'searchTaskForm':searchTaskForm,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'p_id':p_id})
		elif request.POST['start_time'] and not request.POST['end_time'] and not request.POST['search_text']:
                	start_time=request.POST['start_time']
                        start_time="%s 00:00:00" % start_time
                        start_timestamp=time.mktime(time.strptime(start_time,'%Y-%m-%d %H:%M:%S'))
                        start=datetime.datetime.fromtimestamp(start_timestamp)
                        search_task_obj2=models.Tasks.objects.filter(Q(task_promoter=request.user.userinfo.name)|Q(task_assign=request.user.userinfo.name)|Q(task_cc__icontains=request.user.userinfo.name),task_name_id=p_id,create_time__gte=start)
                        return render(request,'participated_task.html',{'search_task_obj2':search_task_obj2,'searchTaskForm':searchTaskForm,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'p_id':p_id})
		elif not request.POST['start_time'] and request.POST['end_time'] and not request.POST['search_text']:
                	end_time=request.POST['end_time']
                        end_time="%s 00:00:00" % end_time
                        end_timestamp=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M:%S'))
                        end=datetime.datetime.fromtimestamp(end_timestamp)
                        search_task_obj3=models.Tasks.objects.filter(Q(task_promoter=request.user.userinfo.name)|Q(task_assign=request.user.userinfo.name)|Q(task_cc__icontains=request.user.userinfo.name),task_name_id=p_id,create_time__lte=end)
                        return render(request,'participated_task.html',{'search_task_obj3':search_task_obj3,'searchTaskForm':searchTaskForm,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'p_id':p_id})
		elif not request.POST['start_time'] and not request.POST['end_time'] and request.POST['search_text']:
                        search_text=request.POST['search_text']
                        search_task_obj4=models.Tasks.objects.filter(Q(task_id__icontains=search_text) | Q(task_title__icontains=search_text) | Q(task_promoter__icontains=search_text) | Q(task_assign__icontains=search_text) | Q(task_priority__icontains=search_text) | Q(task_type__icontains=search_text),task_name_id=p_id)
                        return render(request,'participated_task.html',{'search_task_obj4':search_task_obj4,'searchTaskForm':searchTaskForm,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'p_id':p_id})
	if search_time:
		return search_tasks(request,search_time,p_id)
	else:
		if p_id:
        		task_list_obj=models.Tasks.objects.filter(task_name_id=p_id)
        		return render(request,'participated_task.html',{'task_list_obj':task_list_obj,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'p_id':p_id,'searchTaskForm':searchTaskForm})
		else:
			return redirect('/task/participated_project/')

@check_login()
def list_launched_task(request):
	accepting_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=0,is_reject=0,is_transfer=0).count()
        handling_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=1,is_finish=0,is_transfer=0).count()
	search_time=request.GET.get('search','')
	searchTaskForm=search_task_form.SearchTaskForm()
	if request.method == 'POST':
		if request.POST.get('status_text',''):
			status_text=request.POST['status_text']
			status_text=u'%s' % status_text
			task_status_obj=models.TasksHandle.objects.filter(task_status=status_text)
			html="";
			count=0;
			for item in task_status_obj:
				list_task_obj=models.Tasks.objects.filter(task_id=item.task_id)
				for item2 in list_task_obj:
					task_title=item2.task_title
					task_promoter=item2.task_promoter
					task_assign=item2.task_assign
					create_time=item2.create_time
					end_time=item2.end_time
					task_priority=item2.task_priority
					task_type=item2.task_type
					count+=1;
					html+='<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td><a href="/task/create_task/?t_id=%s">%s</a> <a onclick="show_task(this)">%s</a></td></tr>' % (count,item.task_id,task_title,task_promoter,task_assign,create_time,end_time,status_text,task_priority,task_type,item.task_id,u'编辑',u'查看')
			return HttpResponse(mark_safe(html))
		elif request.POST.get('sub',''):
			if not request.POST['start_time'] and not request.POST['end_time'] and not request.POST['search_text']:
				message=u'搜索内容不能为空'
				return redirect('/task/launched_task/?message=%s' % message)
			elif request.POST['start_time'] and request.POST['end_time'] and not request.POST['search_text']:
				start_time=request.POST['start_time']
				end_time=request.POST['end_time']
				start_time="%s 00:00:00" % start_time
				end_time="%s 00:00:00" % end_time
				start_timestamp=time.mktime(time.strptime(start_time,'%Y-%m-%d %H:%M:%S'))
                		end_timestamp=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M:%S'))
				start=datetime.datetime.fromtimestamp(start_timestamp)
                		end=datetime.datetime.fromtimestamp(end_timestamp)
				search_task_obj=models.Tasks.objects.filter(Q(create_time__gte=start)&Q(create_time__lte=end))
				return render(request,'launched_task.html',{'search_task_obj':search_task_obj,'searchTaskForm':searchTaskForm,accepting_tasks_count:'accepting_tasks_count','handling_tasks_count':handling_tasks_count})
			elif request.POST['start_time'] and not request.POST['end_time'] and not request.POST['search_text']:
				start_time=request.POST['start_time']
				start_time="%s 00:00:00" % start_time
				start_timestamp=time.mktime(time.strptime(start_time,'%Y-%m-%d %H:%M:%S'))
				start=datetime.datetime.fromtimestamp(start_timestamp)
				search_task_obj2=models.Tasks.objects.filter(Q(create_time__gte=start))
				return render(request,'launched_task.html',{'search_task_obj2':search_task_obj2,'searchTaskForm':searchTaskForm,accepting_tasks_count:'accepting_tasks_count','handling_tasks_count':handling_tasks_count})
			elif not request.POST['start_time'] and request.POST['end_time'] and not request.POST['search_text']:
                                end_time=request.POST['end_time']
                                end_time="%s 00:00:00" % end_time
                                end_timestamp=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M:%S'))
                                end=datetime.datetime.fromtimestamp(end_timestamp)
                                search_task_obj3=models.Tasks.objects.filter(Q(create_time__lte=end))
                                return render(request,'launched_task.html',{'search_task_obj3':search_task_obj3,'searchTaskForm':searchTaskForm,accepting_tasks_count:'accepting_tasks_count','handling_tasks_count':handling_tasks_count})
			elif not request.POST['start_time'] and not request.POST['end_time'] and request.POST['search_text']:
				search_text=request.POST['search_text']
				search_task_obj4=models.Tasks.objects.filter(Q(task_id__icontains=search_text) | Q(task_title__icontains=search_text) | Q(task_promoter__icontains=search_text) | Q(task_assign__icontains=search_text) | Q(task_priority__icontains=search_text) | Q(task_type__icontains=search_text))
				return render(request,'launched_task.html',{'search_task_obj4':search_task_obj4,'searchTaskForm':searchTaskForm,accepting_tasks_count:'accepting_tasks_count','handling_tasks_count':handling_tasks_count})
	if search_time == 'all':
		launched_task_list=models.Tasks.objects.filter(task_promoter=request.user.userinfo.name)
	elif search_time == 'this_week':
		dayOfWeek = datetime.datetime.now().weekday()
		if dayOfWeek == 0:
			Monday = (datetime.datetime.now() - datetime.timedelta(days = 7))
		else:
			Monday=(datetime.datetime.now() - datetime.timedelta(days = int(dayOfWeek)))
		now_time=datetime.datetime.today()
		this_week_obj=models.Tasks.objects.filter(Q(create_time__lte=now_time)&Q(create_time__gte=Monday))
		return render(request,'launched_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'this_week_obj':this_week_obj,'searchTaskForm':searchTaskForm})
	elif search_time == 'last_week':
		dayOfWeek = datetime.datetime.now().weekday()
		if dayOfWeek == 0:
			sunday = (datetime.datetime.now() - datetime.timedelta(days = 7))
			Monday=(datetime.datetime.now() - datetime.timedelta(days = 14))
		else:
			sunday = (datetime.datetime.now() - datetime.timedelta(days = int(dayOfWeek)))
			Monday=(datetime.datetime.now() - datetime.timedelta(days = int(dayOfWeek+7)))
		last_week_obj=models.Tasks.objects.filter(Q(create_time__lte=sunday)&Q(create_time__gte=Monday))
		return render(request,'launched_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'last_week_obj':last_week_obj,'searchTaskForm':searchTaskForm})
	elif search_time == 'this_month':
		day_now = time.localtime()
		wday, days = calendar.monthrange(day_now.tm_year, day_now.tm_mon)
		month_begin = '%d-%02d-01 00:00:00' % (day_now.tm_year, day_now.tm_mon)
		month_end='%d-%02d-01 00:00:00' % (day_now.tm_year,day_now.tm_mon+1)
		month_begin_timestamp=time.mktime(time.strptime(month_begin,'%Y-%m-%d %H:%M:%S'))
		month_end_timestamp=time.mktime(time.strptime(month_end,'%Y-%m-%d %H:%M:%S'))
		start=datetime.datetime.fromtimestamp(month_begin_timestamp)
		end=datetime.datetime.fromtimestamp(month_end_timestamp)
		this_month_obj=models.Tasks.objects.filter(Q(create_time__gte=start)&Q(create_time__lte=end))
		return render(request,'launched_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'this_month_obj':this_month_obj,'searchTaskForm':searchTaskForm})
	elif search_time == 'last_month':
		day_now = time.localtime()
                wday, days = calendar.monthrange(day_now.tm_year, day_now.tm_mon)
                month_begin = '%d-%02d-01 00:00:00' % (day_now.tm_year,day_now.tm_mon-1)
                month_end='%d-%02d-01 00:00:00' % (day_now.tm_year,day_now.tm_mon)
                month_begin_timestamp=time.mktime(time.strptime(month_begin,'%Y-%m-%d %H:%M:%S'))
                month_end_timestamp=time.mktime(time.strptime(month_end,'%Y-%m-%d %H:%M:%S'))
                start=datetime.datetime.fromtimestamp(month_begin_timestamp)
                end=datetime.datetime.fromtimestamp(month_end_timestamp)
                last_month_obj=models.Tasks.objects.filter(Q(create_time__gte=start)&Q(create_time__lte=end))
                return render(request,'launched_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'last_month_obj':last_month_obj,'searchTaskForm':searchTaskForm})
	else:
		launched_task_list=models.Tasks.objects.filter(task_promoter=request.user.userinfo.name)
	return render(request,'launched_task.html',{'launched_task_list':launched_task_list,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'searchTaskForm':searchTaskForm})

@check_login()
def list_participated_project(request):
	'''
	列举出所有参与的项目，并列出该项目下对应的任务
	'''
	accepting_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=0,is_reject=0,is_transfer=0).count()
        handling_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=1,is_finish=0,is_transfer=0).count()
	search_time=request.GET.get('search','')
	result=[]
	searchTaskForm=search_task_form.SearchTaskForm()
        participated_task_obj=models.Tasks.objects.filter(Q(task_promoter=request.user.userinfo.name)|Q(task_assign=request.user.userinfo.name)|Q(task_cc__icontains=request.user.userinfo.name)).values('task_name').distinct()
	if request.method == 'POST':
		if request.POST.get('sub',''):
                        if not request.POST['start_time'] and not request.POST['end_time'] and not request.POST['search_text']:
                                message=u'搜索内容不能为空'
                                return redirect('/task/participated_project/?message=%s' % message)
                        elif request.POST['start_time'] and request.POST['end_time'] and not request.POST['search_text']:
                                start_time=request.POST['start_time']
                                end_time=request.POST['end_time']
                                start_time="%s 00:00:00" % start_time
                                end_time="%s 00:00:00" % end_time
                                start_timestamp=time.mktime(time.strptime(start_time,'%Y-%m-%d %H:%M:%S'))
                                end_timestamp=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M:%S'))
                                start=datetime.datetime.fromtimestamp(start_timestamp)
                                end=datetime.datetime.fromtimestamp(end_timestamp)
                                search_project_obj=models.Projects.objects.filter(Q(create_time__gte=start)&Q(create_time__lte=end))
                                return render(request,'participated_project.html',{'search_project_obj':search_project_obj,'searchTaskForm':searchTaskForm,accepting_tasks_count:'accepting_tasks_count','handling_tasks_count':handling_tasks_count})
                        elif request.POST['start_time'] and not request.POST['end_time'] and not request.POST['search_text']:
                                start_time=request.POST['start_time']
                                start_time="%s 00:00:00" % start_time
                                start_timestamp=time.mktime(time.strptime(start_time,'%Y-%m-%d %H:%M:%S'))
                                start=datetime.datetime.fromtimestamp(start_timestamp)
                                search_project_obj2=models.Projects.objects.filter(Q(create_time__gte=start))
                                return render(request,'participated_project.html',{'search_project_obj2':search_project_obj2,'searchTaskForm':searchTaskForm,accepting_tasks_count:'accepting_tasks_count','handling_tasks_count':handling_tasks_count})
                        elif not request.POST['start_time'] and request.POST['end_time'] and not request.POST['search_text']:
                                end_time=request.POST['end_time']
                                end_time="%s 00:00:00" % end_time
                                end_timestamp=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M:%S'))
                                end=datetime.datetime.fromtimestamp(end_timestamp)
                                search_project_obj3=models.Projects.objects.filter(Q(create_time__lte=end))
                                return render(request,'participated_project.html',{'search_project_obj3':search_project_obj3,'searchTaskForm':searchTaskForm,accepting_tasks_count:'accepting_tasks_count','handling_tasks_count':handling_tasks_count})
                        elif not request.POST['start_time'] and not request.POST['end_time'] and request.POST['search_text']:
                                search_text=request.POST['search_text']
                                search_project_obj4=models.Projects.objects.filter(Q(project_model__icontains=search_text) | Q(project_name__icontains=search_text) | Q(project_promoter__icontains=search_text) | Q(project_type__icontains=search_text) | Q(project_priority__icontains=search_text))
                                return render(request,'participated_project.html',{'search_project_obj4':search_project_obj4,'searchTaskForm':searchTaskForm,accepting_tasks_count:'accepting_tasks_count','handling_tasks_count':handling_tasks_count})
	for item in participated_task_obj:
		project_obj=models.Projects.objects.get(id=item['task_name'])
                result.append(project_obj)
	if search_time:
		if search_time == 'all':
			return render(request,'participated_project.html',{'result':result,'searchTaskForm':searchTaskForm,accepting_tasks_count:'accepting_tasks_count','handling_tasks_count':handling_tasks_count})
	        elif search_time == 'this_week':
	                dayOfWeek = datetime.datetime.now().weekday()
	                if dayOfWeek == 0:
	                        Monday = (datetime.datetime.now() - datetime.timedelta(days = 7))
	                else:
	                        Monday=(datetime.datetime.now() - datetime.timedelta(days = int(dayOfWeek)))
	                now_time=datetime.datetime.today()
	                this_week_obj=models.Projects.objects.filter(Q(create_time__lte=now_time)&Q(create_time__gte=Monday))
	                return render(request,'participated_project.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'this_week_obj':this_week_obj,'searchTaskForm':searchTaskForm})
	        elif search_time == 'last_week':
	                dayOfWeek = datetime.datetime.now().weekday()
	                if dayOfWeek == 0:
	                        sunday = (datetime.datetime.now() - datetime.timedelta(days = 7))
	                        Monday=(datetime.datetime.now() - datetime.timedelta(days = 14))
	                else:
	                        sunday = (datetime.datetime.now() - datetime.timedelta(days = int(dayOfWeek)))
	                        Monday=(datetime.datetime.now() - datetime.timedelta(days = int(dayOfWeek+7)))
	                last_week_obj=models.Projects.objects.filter(Q(create_time__lte=sunday)&Q(create_time__gte=Monday))
	                return render(request,'participated_project.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'last_week_obj':last_week_obj,'searchTaskForm':searchTaskForm})
	        elif search_time == 'this_month':
	                day_now = time.localtime()
	                wday, days = calendar.monthrange(day_now.tm_year, day_now.tm_mon)
	                month_begin = '%d-%02d-01 00:00:00' % (day_now.tm_year, day_now.tm_mon)
	                month_end='%d-%02d-01 00:00:00' % (day_now.tm_year,day_now.tm_mon+1)
	                month_begin_timestamp=time.mktime(time.strptime(month_begin,'%Y-%m-%d %H:%M:%S'))
	                month_end_timestamp=time.mktime(time.strptime(month_end,'%Y-%m-%d %H:%M:%S'))
	                start=datetime.datetime.fromtimestamp(month_begin_timestamp)
	                end=datetime.datetime.fromtimestamp(month_end_timestamp)
	                this_month_obj=models.Projects.objects.filter(Q(create_time__gte=start)&Q(create_time__lte=end))
	                return render(request,'participated_project.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'this_month_obj':this_month_obj,'searchTaskForm':searchTaskForm})
	        elif search_time == 'last_month':
	                day_now = time.localtime()
	                wday,days=calendar.monthrange(day_now.tm_year, day_now.tm_mon)
	                month_begin='%d-%02d-01 00:00:00' % (day_now.tm_year, day_now.tm_mon-1)
	                month_end='%d-%02d-01 00:00:00' % (day_now.tm_year,day_now.tm_mon)
	                month_begin_timestamp=time.mktime(time.strptime(month_begin,'%Y-%m-%d %H:%M:%S'))
	                month_end_timestamp=time.mktime(time.strptime(month_end,'%Y-%m-%d %H:%M:%S'))
	                start=datetime.datetime.fromtimestamp(month_begin_timestamp)
	                end=datetime.datetime.fromtimestamp(month_end_timestamp)
	                last_month_obj=models.Projects.objects.filter(Q(create_time__gte=start)&Q(create_time__lte=end))
	                return render(request,'participated_project.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'last_month_obj':last_month_obj,'searchTaskForm':searchTaskForm})
	else:
		return render(request,'participated_project.html',{'result':result,'searchTaskForm':searchTaskForm,accepting_tasks_count:'accepting_tasks_count','handling_tasks_count':handling_tasks_count})

@check_login()
def list_delayed_task(request):
	accepting_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=0,is_reject=0,is_transfer=0).count()
        handling_tasks_count=models.TasksHandle.objects.filter(task_assign=request.user.userinfo.name,is_accept=1,is_finish=0,is_transfer=0).count()
	finish_tasks_obj=models.TasksHandle.objects.filter(Q(task_assign=request.user.userinfo.name) & Q(is_finish='1'))
	result=[]
	searchTaskForm=search_task_form.SearchTaskForm()
	search_time=request.GET.get('search','')
	for item in finish_tasks_obj:
		if item.delay_end_time:
			delay_end_time=item.delay_end_time
			delay_end_time=str(delay_end_time).split('+')[0]
			finish_time=item.finish_time
			finish_time=str(finish_time).split('+')[0]
			delay_end_timestamp=time.mktime(time.strptime(delay_end_time,'%Y-%m-%d %H:%M:%S'))
			finish_timestamp=time.mktime(time.strptime(finish_time,'%Y-%m-%d %H:%M:%S'))
			if finish_timestamp > delay_end_timestamp:
				delay_tasks_obj=models.TasksHandle.objects.get(task_id=item.task_id)
				result.append(delay_tasks_obj)
		elif not item.delay_end_time and item.end_time:
			end_time=item.end_time
			end_time=str(end_time).split('+')[0]
			finish_time=item.finish_time
			finish_time=str(finish_time).split('+')[0]
			end_timestamp=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M:%S'))
			finish_timestamp=time.mktime(time.strptime(finish_time,'%Y-%m-%d %H:%M:%S'))
			if finish_timestamp > end_timestamp:
				delay_tasks_obj=models.TasksHandle.objects.get(task_id=item.task_id)
				result.append(delay_tasks_obj)
	if request.POST.get('sub',''):
		if not request.POST['start_time'] and not request.POST['end_time'] and not request.POST['search_text']:
			message=u'搜索内容不能为空'
			return redirect('/task/delayed_task/?message=%s' % message)
		elif request.POST['start_time'] and request.POST['end_time'] and not request.POST['search_text']:
                        start_time=request.POST['start_time']
                        end_time=request.POST['end_time']
                        start_time="%s 00:00:00" % start_time
                        end_time="%s 00:00:00" % end_time
                        start_timestamp=time.mktime(time.strptime(start_time,'%Y-%m-%d %H:%M:%S'))
                        end_timestamp=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M:%S'))
			range_time_result=[]
                        for item in result:
				create_time=str(item.create_time).split('+')[0]
                        	create_timestamp=time.mktime(time.strptime(create_time,'%Y-%m-%d %H:%M:%S'))
				if create_timestamp>=start_timestamp and create_timestamp<=end_timestamp:
					range_time_result.append(item)
                        return render(request,'delayed_task.html',{'range_time_result':range_time_result,'searchTaskForm':searchTaskForm,accepting_tasks_count:'accepting_tasks_count','handling_tasks_count':handling_tasks_count})
		elif request.POST['start_time'] and not request.POST['end_time'] and not request.POST['search_text']:
                	start_time=request.POST['start_time']
                        start_time="%s 00:00:00" % start_time
                       	start_timestamp=time.mktime(time.strptime(start_time,'%Y-%m-%d %H:%M:%S'))
			start_time_result=[]
			for item in result:
                                create_time=str(item.create_time).split('+')[0]
                                create_timestamp=time.mktime(time.strptime(create_time,'%Y-%m-%d %H:%M:%S'))
                                if create_timestamp>=start_timestamp:
                                        start_time_result.append(item)
                        return render(request,'delayed_task.html',{'start_time_result':start_time_result,'searchTaskForm':searchTaskForm,accepting_tasks_count:'accepting_tasks_count','handling_tasks_count':handling_tasks_count})
		elif not request.POST['start_time'] and request.POST['end_time'] and not request.POST['search_text']:
                	end_time=request.POST['end_time']
                        end_time="%s 00:00:00" % end_time
                        end_timestamp=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M:%S'))
			end_time_result=[]
			for item in result:
                                create_time=str(item.create_time).split('+')[0]
                                create_timestamp=time.mktime(time.strptime(create_time,'%Y-%m-%d %H:%M:%S'))
                                if create_timestamp<=end_timestamp:
                                        end_time_result.append(item)
                        return render(request,'delayed_task.html',{'end_time_result':end_time_result,'searchTaskForm':searchTaskForm,accepting_tasks_count:'accepting_tasks_count','handling_tasks_count':handling_tasks_count})
		elif not request.POST['start_time'] and not request.POST['end_time'] and request.POST['search_text']:
                	search_text=request.POST['search_text']
			search_text_result=[]
			for item in result:	
				if re.match(search_text,item.task_promoter) or re.match(search_text,item.task_handle_id.task_assign) or re.match(search_text,item.task_handle_id.task_title) or item.task_id == search_text or re.match(search_text,item.task_handle_id.project_model):                        	
					search_text_result.append(item)
			return render(request,'delayed_task.html',{'search_text_result':search_text_result,'searchTaskForm':searchTaskForm,accepting_tasks_count:'accepting_tasks_count','handling_tasks_count':handling_tasks_count})
	if search_time == 'all':
		return render(request,'delayed_task.html',{'result':result,'searchTaskForm':searchTaskForm})
	elif search_time == 'this_week':
		dayOfWeek = datetime.datetime.now().weekday()
                if dayOfWeek == 0:
                        Monday = (datetime.datetime.now() - datetime.timedelta(days = 7))
                else:
                        Monday=(datetime.datetime.now() - datetime.timedelta(days = int(dayOfWeek)))
		Monday=Monday.strftime("%Y-%m-%d %H:%M:%S")
                monday_timestamp=time.mktime(time.strptime(Monday,'%Y-%m-%d %H:%M:%S'))
                now_timestamp=time.time()
		this_week_result=[]
		for item in result:
			create_time=str(item.create_time).split('+')[0]
			create_timestamp=time.mktime(time.strptime(create_time,'%Y-%m-%d %H:%M:%S'))
			if create_timestamp>=monday_timestamp and create_timestamp<=now_timestamp:
				this_week_result.append(item)
                return render(request,'delayed_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'this_week_result':this_week_result,'searchTaskForm':searchTaskForm})
	elif search_time == 'last_week':
                dayOfWeek = datetime.datetime.now().weekday()
                if dayOfWeek == 0:
                        Sunday = (datetime.datetime.now() - datetime.timedelta(days = 7))
                        Monday=(datetime.datetime.now() - datetime.timedelta(days = 14))
                else:
                        Sunday = (datetime.datetime.now() - datetime.timedelta(days = int(dayOfWeek)))
                        Monday=(datetime.datetime.now() - datetime.timedelta(days = int(dayOfWeek+7)))
		Sunday=Sunday.strftime("%Y-%m-%d %H:%M:%S")
		Monday=Monday.strftime("%Y-%m-%d %H:%M:%S")
		monday_timestamp=time.mktime(time.strptime(Monday,'%Y-%m-%d %H:%M:%S'))
		sunday_timestamp=time.mktime(time.strptime(Sunday,'%Y-%m-%d %H:%M:%S'))
		last_week_result=[]
                for item in result:
			create_time=str(item.create_time).split('+')[0]
                        create_timestamp=time.mktime(time.strptime(create_time,'%Y-%m-%d %H:%M:%S'))
			if create_timestamp>=monday_timestamp and create_timestamp<=sunday_timestamp:
				last_week_result.append(item)
                return render(request,'delayed_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'last_week_result':last_week_result,'searchTaskForm':searchTaskForm})
	elif search_time == 'this_month':
                day_now = time.localtime()
                wday, days = calendar.monthrange(day_now.tm_year, day_now.tm_mon)
                month_begin = '%d-%02d-01 00:00:00' % (day_now.tm_year, day_now.tm_mon)
                month_end='%d-%02d-01 00:00:00' % (day_now.tm_year,day_now.tm_mon+1)
                month_begin_timestamp=time.mktime(time.strptime(month_begin,'%Y-%m-%d %H:%M:%S'))
                month_end_timestamp=time.mktime(time.strptime(month_end,'%Y-%m-%d %H:%M:%S'))
		this_month_result=[]
                for item in result:
                        create_time=str(item.create_time).split('+')[0]
                        create_timestamp=time.mktime(time.strptime(create_time,'%Y-%m-%d %H:%M:%S'))
                        if create_timestamp>=month_begin_timestamp and create_timestamp<=month_end_timestamp:
                                this_month_result.append(item)
                return render(request,'delayed_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'this_month_result':this_month_result,'searchTaskForm':searchTaskForm})
	elif search_time == 'last_month':
                day_now = time.localtime()
                wday, days = calendar.monthrange(day_now.tm_year, day_now.tm_mon)
                month_begin = '%d-%02d-01 00:00:00' % (day_now.tm_year, day_now.tm_mon-1)
                month_end='%d-%02d-01 00:00:00' % (day_now.tm_year,day_now.tm_mon)
                month_begin_timestamp=time.mktime(time.strptime(month_begin,'%Y-%m-%d %H:%M:%S'))
                month_end_timestamp=time.mktime(time.strptime(month_end,'%Y-%m-%d %H:%M:%S'))
		last_month_result=[]
		for item in result:
			create_time=str(item.create_time).split('+')[0]
                        create_timestamp=time.mktime(time.strptime(create_time,'%Y-%m-%d %H:%M:%S'))
			if create_timestamp>=month_begin_timestamp and create_timestamp<=month_end_timestamp:
				last_month_result.append(item)
		return render(request,'delayed_task.html',{'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count,'last_month_result':last_month_result,'searchTaskForm':searchTaskForm})
        else:
		return render(request,'delayed_task.html',{'result':result,'searchTaskForm':searchTaskForm,'accepting_tasks_count':accepting_tasks_count,'handling_tasks_count':handling_tasks_count})

def record_talk(request):
	if request.method == 'POST':
		task_id=request.POST['task_id']
		talk_content=request.POST['talk_content']
		talk_content=talk_content.strip()
		if talk_content:
			is_ok=models.TaskTalk.objects.create(talk_name=request.user.userinfo.name,talk_content=talk_content,task_id=task_id)
			html=""
			if is_ok:
				talk_task_obj=models.TaskTalk.objects.filter(task_id=task_id)
				for item in talk_task_obj:
					html+="<div style='width:200px;border:1px solid blue;margin-top:2px'>"
					html+="<p style='font-size:4px;'>"+item.talk_name+":</p>"
					html+="<p style='font-weight:bold'>"+item.talk_content+"</p>"
					html+="<p style='font-size:4px;margin-left:80px'>"+str(item.talk_time).split('+')[0]+"</p>"
					html+="</div>"
				return HttpResponse(mark_safe(html))
