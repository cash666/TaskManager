#coding:utf8

from django import template
from django.utils.safestring import mark_safe
  
register = template.Library()

@register.simple_tag
def split_str(str):
	if str:
		new_str=str.split('/')[1]
		return new_str

@register.simple_tag
def list_content(str):
	if str:
		new_str=str.split('\n')
		return new_str

