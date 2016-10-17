from django.db import models
from djangotoolbox.fields import EmbeddedModelField,ListField
from .forms import ObjectListCharField,ObjectListFloatField,ObjectListParklotStatusField
import datetime
import re
import ast
from save_the_change.mixins import SaveTheChange
from django.utils.translation import ugettext_lazy as _
#add belows to rewrite update/save
from mongoengine import connect
import logging
logger = logging.getLogger('django')
from pymongo import MongoClient
from bson.objectid import ObjectId
client = MongoClient('localhost', 27017)
db = client.bleparking


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
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        '''python to human'''
        if not value:
            return value

        try:
            return re.findall(r'ObjectId\("([a-zA-Z0-9]+")\)',value)
        except Exception:
            return value

    def prepare_value(self, value):
        ''' human to python'''
        if not value:
            return value
        try:
            return ObjectId(value)
        except Exception:
            return value


class ObjectIdListField(ObjectIdField):

    def __init__(self, *args, **kwargs):
        super(ObjectIdField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return value

        if isinstance(value, list):
            logger.debug('------heyhey---enter isinstance')
            return map(super(ObjectIdField,self).to_python,value)

        #return ast.literal_eval(value)
        return super(ObjectIdField,self).to_python(value)

    def prepare_value(self, value):
        if value is None:
            return value

        if isinstance(value,list):
            return [i for i in value if isinstance(i,ObjectId)] | [ObjectId(i) for i in value if not isinstance(i,ObjectId)]

        return super(ObjectIdField,self).to_python(value)
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
    #pk_id=models.CharField(max_length=24,db_column='id',verbose_name='parklotId')
    pk_id=ObjectIdField(db_column='id',verbose_name='ParklotId')
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
            #now = datetime.datetime.now()
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
            #now = datetime.datetime.now()
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

class regcheck(models.Model):
    #pk_id = models.CharField(max_length=24, db_column='id', verbose_name='regcheckId')
    pk_id = ObjectIdField(db_column='id',verbose_name='regcheckId')
    #todo:next should be objectid
    #agent=models.CharField(max_length=24,verbose_name='agentId')
    #parklot=models.CharField(max_length=24, verbose_name='parklotId')
    agent=ObjectIdField()
    parklot=ObjectIdField()
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


class parkticket(models.Model):
    #pk_id = models.CharField(max_length=24, db_column='id', verbose_name='parkticketId')
    pk_id = ObjectIdField(db_column='id', verbose_name='parkticketId')
    car_plate=models.CharField(max_length=20)
    #todo next 2 should be objectid field
    #parklot=models.CharField(max_length=24)
    parklot=ObjectIdField()
    #agent=models.CharField(max_length=24)
    agent=ObjectIdField()
    create_on=models.DateTimeField()
    update_on=models.DateTimeField()
    payment_state = models.CharField(max_length=30,db_column='payment_state', blank=True)
    #next 2 are float but they seems not support blank=True, so define as char
    amount= models.CharField(max_length=10,blank=True)
    duration=models.CharField(max_length=10,blank=True)
    transaction_no=models.CharField(max_length=30,blank=True)

    class Meta:
        db_table="parkticket"



class agent(models.Model):
    #pk_id = models.CharField(max_length=24, db_column='id', verbose_name='agentId')
    pk_id = ObjectIdField(db_column='id', verbose_name='agentId')
    nick=models.CharField(max_length=20)
    pic=models.CharField(max_length=24,blank=True,default='img/test.jpg')
    parklot=models.CharField(max_length=200,blank=True)
    #parklot=ObjectIdListField(db_column='parklot',verbose_name='parklotList')

    #parklot=objectIDField()
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












