from django.contrib import admin
from .models import parklot,regcheck,parkticket,addr,gps,status,agent
from django.contrib.contenttypes import generic
from bson.objectid import ObjectId
from django import forms
import datetime
import logging
logger = logging.getLogger('django')

#c#lass parklotShipInline(admin.TabularInline):
#    model = agent.p#arklot.through
#    fieldsets=[
#        (None,)
#    ]

class parklotAdmin(admin.ModelAdmin):
    #display with it's address link
    list_display=('description','pk_id','addr')
    #specify the widget of embeded fields
    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(parklotAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in ['status','gps','addr']:
            formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)
        return formfield
    fields = ['pk_id', 'description', 'addr', 'gps', 'status', 'create_on']
    #todo: filter according to addr
    search_fields=['description','pk_id']

    readonly_fields=['create_on','pk_id',]

    def get_search_results(self,request,queryset,search_term):
        queryset,use_distinct=super(parklotAdmin,self).get_search_results(request,queryset,search_term)
        try:
            logger.debug('heyheyhey-----{0}'.format(search_term))
            search_term_as_object = ObjectId(search_term)
        except ValueError:
            pass
        else:
            queryset |= self.model.objects.filter(pk_id=search_term_as_object)
        return queryset,use_distinct

    def queryset(self,request):
        qs=super(parklotAdmin,self).queryset(request)
        logger.debug('heyheyhey-----{0}'.format(request.GET))
        return qs

    def save_model(self, request, obj, form, change):
        #save with the time and the operator id
        if hasattr(obj,'status'):
            #logger.debug('--------------No!!')
            obj.status.update_by = ObjectId(request.user.id)
            now=datetime.datetime.now()
            obj.status.update_on=now
        #logger.debug('--------------------------{0}--------------{1}'.format(obj, obj.status))
        obj.save()

class regcheckAdmin(admin.ModelAdmin):
    list_display=('pk_id','agent','parklot','car_plate','create_on','state')
    search_fields=['car_plate']
    readonly_fields=['pk_id','agent','parklot','car_plate','create_on','update_on','state','pic']
    fields=['pk_id','agent','parklot','car_plate','pic','state','create_on','update_on']
    list_filter=['create_on']
    #date_hierarchy='create_on'

class parkticketAdmin(admin.ModelAdmin):
    search_fields=['car_plate']
    readonly_fields = ['pk_id','car_plate', 'parklot', 'agent', 'create_on', 'update_on', 'payment_state', 'amount',
                       'duration','transaction_no']
    fieldsets =[
        ('Main Data',{'fields':['pk_id','car_plate','parklot','agent','create_on','update_on']}),
        ('Status Details',{'fields':['payment_state','amount','duration','transaction_no'],'classes':['collapse']}),
        #(None,{'fields':['create_on','update_on']}),
    ]
    list_display=('pk_id','car_plate','parklot','agent','create_on','payment_state')
    #fields = ['car_plate', 'parklot', 'agent', 'State Details', 'create_on', 'update_on']
    list_filter=['create_on']
    #date_hierarchy='create_on'

class agentAdmin(admin.ModelAdmin):
    list_display=('nick','phone','pk_id','parklot')
    fields=['pk_id','phone','nick','pic','parklot','status','create_on','update_on']

    search_fields=['nick','phone','pk_id']
    readonly_fields=('status','create_on','update_on','pic','pk_id')
    list_per_page=10

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(agentAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in ['parklot']:
            formfield.widget = forms.Textarea(attrs=formfield.widget.attrs)
        return formfield

admin.site.register(parklot, parklotAdmin)
admin.site.register(regcheck,regcheckAdmin)
admin.site.register(parkticket,parkticketAdmin)
admin.site.register(agent,agentAdmin)

