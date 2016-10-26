#-*- coding=utf-8 -*-
from django import forms
import datetime
import json

def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True

class ObjectListCharField(forms.CharField):
    #self.widget
    def prepare_value(self, value):
        if not value:
            return ''

        newvalue = {}
        for key, val in value.__dict__.items():
            #print "***** %s  %s  %s " % (key, type(val),(type(val) is unicode))
            if type(val) is unicode:
                newvalue[key] = val
        # Integer, Date,  Float,
        #return ", ".join(["%s=%s" % (k, v) for k, v in newvalue.items()])
        return json.dumps(newvalue,indent=4,ensure_ascii=False)

    def to_python(self, value):
        if not value:
            return {}
        obj = {}
        if is_json(value):
            obj=json.loads(value)
        return obj

class ObjectListFloatField(forms.FloatField):
    def prepare_value(self, value):
        if not value:
            return ''
        newvalue = {}

        for key, val in value.__dict__.items():
            if type(val) is float:
                newvalue[key] = val
        # Integer, Date,  Float,
        return json.dumps(newvalue,indent=4)
    def to_python(self, value):
        if not value:
            return {}
        obj = {}
        if is_json(value):
            obj=json.loads(value)
        return obj
class ObjectListParklotStatusField(forms.CharField,forms.IntegerField):
    def prepare_value(self,value):
        if not value:
            return ''

        newvalue = {}

        for key, val in value.__dict__.items():
            if type(val) is unicode or type(val) is int:
                newvalue[key] = val
            elif  type(val) is datetime.datetime :
                newvalue[key] = str(val)
        return json.dumps(newvalue,indent=4)

    def to_python(self,value):
        if not value:
            return {}
        obj={}
        if is_json(value):
            obj=json.loads(value)
            #del obj['update_by']
            #del obj['update_on']
        return obj
