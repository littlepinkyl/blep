# -*- coding:utf-8 -*-
from django.db import models
from djangotoolbox.fields import EmbeddedModelField
from .forms import ObjectListCharField,ObjectListFloatField,ObjectListParklotStatusField
import datetime
import re
from bson.objectid import ObjectId
from save_the_change.mixins import SaveTheChange
from django.utils.translation import ugettext_lazy as _
#add belows to rewrite update/save
from mongoengine import connect
from django.utils.html import format_html
from pymongo import MongoClient
import logging
from django.conf import settings
db_conf = settings.DATABASES['default']
client = MongoClient(db_conf['HOST'], int(db_conf['PORT']))
db = eval("client.{0}".format(db_conf['NAME']))

logger = logging.getLogger('django')


class EmbedOverrideCharField(EmbeddedModelField):
    def formfield(self, **kwargs):
        return models.Field.formfield(self, ObjectListCharField, **kwargs)


class EmbedOverrideFloatField(EmbeddedModelField):#
    def formfield(self, **kwargs):
        return models.Field.formfield(self, ObjectListFloatField, **kwargs)

class EmbedOverrideParklotStatusfield(EmbeddedModelField):
    def formfield(self,**kwargs):
        return models.Field.formfield(self, ObjectListParklotStatusField, **kwargs)
# Create your models here.


class ObjectIdField(models.TextField):
    """    model Fields for objectID    """
    #http://django-chinese-docs.readthedocs.io/en/latest/howto/custom-model-fields.html?highlight=to_python#django.db.models.Field.to_python
    __metaclass__ = models.SubfieldBase
    # prepare_value used as first and ObjectIdfield can used be searched, but sth unknown changed and  ObjectId search got failure
    # 1.5 django doc doesn't mention prepare_value but get_prep_value so use this one instead
    # and it WORKS!!!!!! DON'T KNOW WHY!!!!
    #def prepare_value(self, value):
    #    '''python to human'''
    #    if not value:
    #        return value
#
    #    try:
#
    #        logger.debug('objectid_prepare_value---------{0}'.format(re.findall(r'ObjectId\("([a-zA-Z0-9]+)"\)',value)))
    #        return re.findall(r'ObjectId\(\'([a-z0-9]+)\'\)',value)
    #    except Exception:
    #        return value

    def get_prep_value(self,value):
        logger.debug('get_prep_value-------{0}----{1}'.format(value,type(value)))
        if not isinstance(value,ObjectId):
            return ObjectId(value)
        return value


    def to_python(self, value):
        ''' human to python'''
        if not value:#
            return value
        logger.debug('objectid_to_python---------{0}-------{1}'.format(value, type(value)))
        return value

        #try:#
        #    r=ObjectId(value)
        #    logger.debug('objectid_to_python---------{0}-------{1}'.format(r,type(r)))
        #    return r
        #except Exception:
        #    return value


#class ObjectIdListField(ObjectIdField):
#
#    def __init__(self, *args, **kwargs):
#        super(ObjectIdField, self).__init__(*args, **kwargs)
#
#    def prepare_value(self, value):
#        if not value:
#            return value
#
#        if isinstance(value, list):
#            logger.debug('------heyhey---enter isinstance')
#            return map(super(ObjectIdField,self).prepare_value,value)
#
#        #return ast.literal_eval(value)
#        return super(ObjectIdField,self).prepare_value(value)
#
#    def to_python(self, value):
#        if value is None:
#            return value
#
#        if isinstance(value,list):
#            return [i for i in value if isinstance(i,ObjectId)] | [ObjectId(i) for i in value if not isinstance(i,ObjectId)]
#
#        return super(ObjectIdField,self).to_python(value)
        #
        #if isinstance(value,list):
        #    return eval(value)
        #return unicode(value)


class addr(models.Model):
    province=models.CharField(max_length=10)
    city=models.CharField(max_length=10)
    district=models.CharField(max_length=10)
    street=models.CharField(max_length=20)

    def __unicode__(self):
        return "%s,%s,%s,%s" % (self.province,self.city,self.district,self.street)



class gps(models.Model):
    ##
    longitude=models.FloatField()
    latitude=models.FloatField()
    def __unicode__(self):
        return "%f,%f" % (self.longitude,self.latitude)

class status(models.Model):
    free=models.IntegerField()#
    total=models.IntegerField()
    update_on=models.DateTimeField()
    #todo next should be objectId
    update_by=models.CharField(max_length=20)
    #def __unicode__(self):
    #    return "%d, %d, %s, %s " % (self.free,self.total,self.update_on,self.update_by)

class parklot(models.Model):
    pk_id=models.CharField(max_length=24,db_column='id',verbose_name='parklotId')
    description=models.CharField(max_length=50)
    addr = EmbedOverrideCharField('addr')
    create_on=models.DateTimeField('create_on')
    gps=EmbedOverrideFloatField('gps')
    #gps#.longitude=models.FloatField()
    #gps.latitude=models.FloatField()

    #todo:next should be optional
    status=EmbedOverrideParklotStatusfield('status',blank=True)
    #status=EmbedOverrideCharField('status',blank=True)
    class Meta:
        db_table='parklot'

    def __unicode__(self):
        return "%s ------ %s, %s, %s, %s" % (self.description, self.addr.province, self.addr.city,\
                                             self.addr.district, self.addr.street)

    #def get_pk_id(self):
    #    pk_id=models.CharField(db_column='id')
    #    return pk_id.__unicode__
    #db.parklot.update({"addr.province": ''}, {$set:{"addr.district": ""}}, false, true);

    def save(self):

        #TODO: once changed the form of embeded fields, this logic should be updated
        current = {
            "description":self.description,
            "addr":{
                "province":self.addr.province,
                "city":self.addr.city,
                "district":self.addr.district,
                "street":self.addr.street,
            },
            "gps":{
                "longitude":self.gps.longitude,
                "latitude":self.gps.latitude,
            },
        }
        #print "this***! " , self.status.free
        parklot = db.parklot
        pre = parklot.find_one({'_id': ObjectId(self.pk)})
        #print "***************** %s" % (type(self.pk),)
        if pre == None:
            now = datetime.datetime.now()
            current['create_on']=now
            current['update_on']=now
            #status
            if hasattr(self,'status'):
                current['status']={
                    "free":self.status.free,
                    "total":self.status.total,
                    "update_on":self.status.update_on,
                    "update_by": self.status.update_by,
                }

            pre_id = parklot.insert_one(current).inserted_id
            # if not exist, insert and print id here, if true then success
        else:
            # if exist, update it manually
            now = datetime.datetime.now()
            current['update_on'] = now
            if hasattr(self,'status'):
                current['status']={
                    "free":self.status.free,
                    "total":self.status.total,
                    "update_on":self.status.update_on,
                    "update_by":self.status.update_by,
                }
            #logger.debug('123123123123............')
            res = parklot.update_one({'_id': ObjectId(self.pk)},
                                   {'$set': current})
            if res == 1:
                #print '[DEBUG]:save successfully!'
                pass
#
class regcheck(models.Model):
    #pk_id = models.CharField(max_length=24, db_column='id', verbose_name='regcheckId')
    pk_id=ObjectIdField(db_column='id',verbose_name='regcheckId')
    #todo:next should be objectid
    #agent=models.CharField(max_length=24,verbose_name='agentId')
    #parklot=models.CharField(max_length=24, verbose_name='parklotId')
    parklot=ObjectIdField(db_column='parklot',verbose_name='parklotId')
    agent=ObjectIdField(db_column='agent',verbose_name='agentId')
    car_plate=models.CharField(max_length=24)
    create_on=models.DateTimeField()
    update_on=models.DateTimeField()
    #todo ( pic string & state 0 ) or state in (1,2,3) enum
    regcheckStatus=(
        (0,u'start'),
        (1,u'working'),
        (2,u'finished'),
        (3,u'other')
    )
    state=models.IntegerField(choices=regcheckStatus)
    pic=models.CharField(max_length=100,blank=True)
    class Meta:
        db_table='regcheck'
    def detail_parklot(self):
        parklot=db.parklot
        result=parklot.find_one({'_id':ObjectId(self.parklot)})
        logger.debug('herehere---------------{0}'.format(self.parklot))
        #return "%s---%s,%s,%s# <%s>" % (result['description'],result['city'],result['district'],result['street'],result['id'])
        if result:
            return "%s---%s,%s,%s,%s <%s>" % (result['description'],result['addr']['province'],result['addr']['city'],result['addr']['district'],result['addr']['street'],result['_id'])
        else:
            return self.parklot
    #search_parklot.short_cut
    def detail_agent(self):
        agent=db.agent
        result=agent.find_one({'_id':ObjectId(self.agent)})
        if result:
            return "%s,%s <%s>" % (result['nick'],result['phone'],result['_id'])
        else:
            return self.agent


class parkticket(models.Model):
    #pk_id = models.CharField(max_length=24, db_column='id', verbose_name='parkticketId')
    pk_id= ObjectIdField(db_column='id',verbose_name='parkticketId')
    car_plate=models.CharField(max_length=20)
    #todo next 2 should be objectid field
    #parklot=models.CharField(max_length=24)
    #agent=models.CharField(max_length=24)
    parklot=ObjectIdField(db_column='parklot',verbose_name='parklotId')
    agent=ObjectIdField(db_column='agent',verbose_name='agentId')

    create_on=models.DateTimeField()
    update_on=models.DateTimeField()
    payment_state = models.CharField(max_length=30,db_column='payment_state', blank=True)
    #next 2 are float but they seems not support blank=True, so define as char
    amount= models.CharField(max_length=10,blank=True)
    duration=models.CharField(max_length=10,blank=True)
    transaction_no=models.CharField(max_length=30,blank=True)


    class Meta:
        db_table="parkticket"

    def detail_parklot(self):
        parklot=db.parklot
        result=parklot.find_one({'_id':ObjectId(self.parklot)})
        logger.debug('herehere---------------{0}'.format(self.parklot))
        #return "%s---%s,%s,%s# <%s>" % (result['description'],result['city'],result['district'],result['street'],result['id'])
        if result:
            return "%s---%s,%s,%s,%s <%s>" % (result['description'],result['addr']['province'],result['addr']['city'],result['addr']['district'],result['addr']['street'],result['_id'])
        else:
            return self.parklot
    #search_parklot.short_description
    def detail_agent(self):
        agent=db.agent
        result=agent.find_one({'_id':ObjectId(self.agent)})
        if result:
            return "%s,%s <%s>" % (result['nick'],result['phone'],result['_id'])
        else:
            return self.agent

class agent(models.Model):
    pk_id = models.CharField(max_length=24, db_column='id', verbose_name='agentId')
    nick=models.CharField(max_length=20)
    pic=models.CharField(max_length=24,blank=True,default='img/test.jpg')
    parklot=models.CharField(max_length=200,blank=True)
    #parklot=ObjectIdField()
    #parklot=models.ManyToManyField(parklot,blank=True,editable=False)
    #parklot=models.ForeignKey(parklot)
#
    #def get_parklot_desc(self,obj):
    #    return obj.parklot.description
    #get_parklot_desc.short_description='parklot description '

    pas=models.CharField(max_length=100,blank=True,verbose_name='password',db_column='pass',editable=False,default='xxxxxx')
    update_on=models.DateTimeField()
    phone=models.CharField(max_length=11)
    create_on=models.DateTimeField()
    agentStatus=(
        (0,u'valid'),
        (1,u'invalid'),
    )
    status=models.IntegerField(choices=agentStatus,verbose_name='(Status)')

    def show_parklot(self):
        result=[]
        if isinstance(self.parklot,list):
            for i in self.parklot:
                tmp=db.parklot.find_one({"_id":i})
                if tmp:
                    result.append("%s-%s%s%s%s <%s>".encode("gbk") % (tmp['description'],tmp['addr']['province'],tmp['addr']['city'],tmp['addr']['district'],tmp['addr']['street'],tmp['_id']))
                else:
                    result.append(self.parklot)
                return result
        else:
            tmp = db.parklot.find_one({"_id": self.parklot})
            if tmp:
                return "%s-%s%s%s%s <%s>" % (tmp['description'],tmp['addr']['province'],tmp['addr']['city'],tmp['addr']['district'],tmp['addr']['street'],tmp['_id'])
            else:
                return self.parklot
    show_parklot.short_description='ParklotDetails'



    class Meta:
        db_table='agent'

    def __unicode__(self):
        return "%s----%s" % (self.nick,self.phone )


    def save(self):
        current = {
            "phone":self.phone,
            "nick":self.nick,

        }
        if hasattr(self,'parklot'):
            an=re.search('ObjectId',self.parklot)
            #logger.debug('-----------------{0}'.format( self.parklot))
            if an :

                parklot=re.sub('ObjectId\(\'|\'\)|[\[\] ]', '', self.parklot)

            else:
                parklot=self.parklot
            current['parklot'] = [ObjectId(i) for i in parklot.split(',')]
        agent = db.agent
        #print "***************%s" % (type(self.pk),)
        pre = agent.find_one({'_id': ObjectId(self.pk)})
        if pre == None:
            #current
            now = datetime.datetime.now()
            current['create_on']=now
            current['update_on']=now
            current['status']=0
            current['pass']='empty pass'
            pre_id = agent.insert_one(current).inserted_id
            # if not exist, insert and print id here, if true then success
        else:
            # if exist, update it manually
            now = datetime.datetime.now()
            current['update_on'] = now
            res = agent.update_one({'_id': ObjectId(self.pk)},
                                   {'$set': current})
            if res == 1:
                #print '[DEBUG]:save successfully!'
                pass












