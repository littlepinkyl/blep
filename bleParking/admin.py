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
        #qs=super(parklotAdmin,self).queryset(request)
        qs = self.model._default_manager.get_query_set()
        logger.debug('heyheyhey-----{0}'.format(request.GET))
        ###
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)

        # Custom Search
        # 1. Get the query value and clear it from the request
        q = ''
        try:
            q = request.GET['q']
            copy = request.GET.__copy__()
            copy.__delitem__('q')
            request.GET = copy

        except:
            pass

        result_list = []
#
        # Search on main model (parklot)
        if q != '':
            parklot_obj_list = self.model.objects.filter(description__contains=q)
            try:
                parklot_obj_list |= self.model.objects.filter(pk__exact=ObjectId(q))
            except:
                pass
            logger.debug('heyheyhey----resultlo-{0}'.format(parklot_obj_list))
        else:
            parklot_obj_list = self.model.objects.all()
        for parklot in parklot_obj_list:
                result_list.append(parklot.pk)

        # Search on the other related model (Other Name)
        #other_names_obj_list = OtherName.objects.filter(name__contains=q)
        #for other_name in other_names_obj_list:
        #    result_list.append(other_name.person.pk)
        return qs.filter(pk__in=result_list)  # apply the filter
        #return qs

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
    search_fields=['car_plate','agent','parklot']
    readonly_fields=['pk_id','agent','parklot','car_plate','create_on','update_on','state','pic']
    fields=['pk_id','agent','parklot','car_plate','pic','state','create_on','update_on']
    list_filter=['create_on']
    #date_hierarchy='create_on'
    def queryset(self, request):
        # qs=super(parklotAdmin,self).queryset(request)
        qs = self.model._default_manager.get_query_set()
        logger.debug('heyheyhey-----{0}'.format(request.GET))
        ###
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)

        # Custom Search
        # 1. Get the query value and clear it from the request
        q = ''
        try:
            q = request.GET['q']
            copy = request.GET.__copy__()
            copy.__delitem__('q')
            request.GET = copy

        except:
            pass

        result_list = []
        #
        # Search on main model (parklot)
        if q != '':
            regcheck_obj_list = self.model.objects.filter(car_plate__contains=q)
            try:
                regcheck_obj_list |= self.model.objects.filter(pk__exact=ObjectId(q))
                regcheck_obj_list |= self.model.objects.filter(agent__exact=ObjectId(q))
                regcheck_obj_list |= self.model.objects.filter(parklot__exact=ObjectId(q))
            except:
                pass
            logger.debug('heyheyhey----resultlo-{0}'.format(regcheck_obj_list))
        else:
            regcheck_obj_list = self.model.objects.all()
        for regcheck in regcheck_obj_list:
            result_list.append(regcheck.pk)

        # Search on the other related model (Other Name)
        # other_names_obj_list = OtherName.objects.filter(name__contains=q)
        # for other_name in other_names_obj_list:
        #    result_list.append(other_name.person.pk)
        return qs.filter(pk__in=result_list)  # apply the filter

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
    def queryset(self, request):
        # qs=super(parklotAdmin,self).queryset(request)
        qs = self.model._default_manager.get_query_set()
        logger.debug('heyheyhey-----{0}'.format(request.GET))
        ###
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)

        # Custom Search
        # 1. Get the query value and clear it from the request
        q = ''
        try:
            q = request.GET['q']
            copy = request.GET.__copy__()
            copy.__delitem__('q')
            request.GET = copy

        except:
            pass

        result_list = []
        #
        # Search on main model (parklot)
        if q != '':
            parkticket_obj_list = self.model.objects.filter(car_plate__contains=q)
            try:
                parkticket_obj_list |= self.model.objects.filter(pk__exact=ObjectId(q))
                parkticket_obj_list |= self.model.objects.filter(parklot__exact=ObjectId(q))
                parkticket_obj_list |= self.model.objects.filter(agent__exact=ObjectId(q))
            except:
                pass
            logger.debug('heyheyhey----resultlo-{0}'.format(parkticket_obj_list))
        else:
            parkticket_obj_list = self.model.objects.all()
        for parkticket in parkticket_obj_list:
            result_list.append(parkticket.pk)

        # Search on the other related model (Other Name)
        # other_names_obj_list = OtherName.objects.filter(name__contains=q)
        # for other_name in other_names_obj_list:
        #    result_list.append(other_name.person.pk)
        return qs.filter(pk__in=result_list)  # apply the filter

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
    def queryset(self,request):
        #qs=super(parklotAdmin,self).queryset(request)
        qs = self.model._default_manager.get_query_set()
        logger.debug('heyheyhey-----{0}'.format(request.GET))
        ###
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)

        # Custom Search
        # 1. Get the query value and clear it from the request
        q = ''
        try:
            q = request.GET['q']
            copy = request.GET.__copy__()
            copy.__delitem__('q')
            request.GET = copy

        except:
            pass

        result_list = []
#
        # Search on main model (parklot)
        if q != '':
            agent_obj_list = self.model.objects.filter(nick__contains=q)
            agent_obj_list |= self.model.objects.filter(phone__contains=q)
            #agent_obj_list |= self.model.objects.filter(parklot__contains=ObjectId(q))
            try:
                agent_obj_list |= self.model.objects.filter(pk__exact=ObjectId(q))

            except:
                pass
            logger.debug('heyheyhey----resultlo-{0}'.format(agent_obj_list))
        else:
            agent_obj_list = self.model.objects.all()
        for agent in agent_obj_list:
                result_list.append(agent.pk)

        # Search on the other related model (Other Name)
        #other_names_obj_list = OtherName.objects.filter(name__contains=q)
        #for other_name in other_names_obj_list:
        #    result_list.append(other_name.person.pk)
        return qs.filter(pk__in=result_list)  # apply the filter
        #return qs

admin.site.register(parklot, parklotAdmin)
admin.site.register(regcheck,regcheckAdmin)
admin.site.register(parkticket,parkticketAdmin)
admin.site.register(agent,agentAdmin)

