# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DistributionSchedule(models.Model):
    _name = 'ngo.distribution.schedule'
    _description = 'Distribution Schedule'

    name = fields.Char(required=True)
    color = fields.Integer(string=_(u"olor Index"))
    hour_from = fields.Float(string=_(u"From"), default=8, required=True, track_visibility='onchange' )
    hour_to = fields.Float(string=_(u"To"), default=18, required=True, track_visibility='onchange')
    monday = fields.Boolean(default=True)
    monday_hour_from = fields.Float(string=_(u"From"), default=8)
    monday_hour_to = fields.Float(string=_(u"To"), default=18, required=True)   
    monday_hour_from2 = fields.Float(string=_(u"From"), default=18)
    monday_hour_to2 = fields.Float(string=_(u"To"), default=18, required=True)        
    tuesday = fields.Boolean(default=True)
    tuesday_hour_from = fields.Float(string=_(u"From"), default=8)
    tuesday_hour_to = fields.Float(string=_(u"To"), default=18, required=True)   
    tuesday_hour_from2 = fields.Float(string=_(u"From"), default=18)
    tuesday_hour_to2 = fields.Float(string=_(u"To"), default=18, required=True)      
    wednesday = fields.Boolean(default=True)
    wednesday_hour_from = fields.Float(string=_(u"From"), default=8)
    wednesday_hour_to = fields.Float(string=_(u"To"), default=18, required=True)   
    wednesday_hour_from2 = fields.Float(string=_(u"From"), default=18)
    wednesday_hour_to2 = fields.Float(string=_(u"To"), default=18, required=True)          
    thursday = fields.Boolean(default=True)
    thursday_hour_from = fields.Float(string=_(u"From"), default=8)
    thursday_hour_to = fields.Float(string=_(u"To"), default=18, required=True)   
    thursday_hour_from2 = fields.Float(string=_(u"From"), default=18)
    thursday_hour_to2 = fields.Float(string=_(u"To"), default=18, required=True)          
    friday = fields.Boolean(default=True)
    friday_hour_from = fields.Float(string=_(u"From"), default=8)
    friday_hour_to = fields.Float(string=_(u"To"), default=11, required=True)   
    friday_hour_from2 = fields.Float(string=_(u"From"), default=13)
    friday_hour_to2 = fields.Float(string=_(u"To"), default=18, required=True)          
    saturday = fields.Boolean()
    saturday_hour_from = fields.Float(string=_(u"From"), default=8)
    saturday_hour_to = fields.Float(string=_(u"To"), default=18, required=True)   
    saturday_hour_from2 = fields.Float(string=_(u"From"), default=18)
    saturday_hour_to2 = fields.Float(string=_(u"To"), default=18, required=True)          
    sunday = fields.Boolean()
    sunday_hour_from = fields.Float(string=_(u"From"), default=8)
    sunday_hour_to = fields.Float(string=_(u"To"), default=18, required=True)   
    sunday_hour_from2 = fields.Float(string=_(u"From"), default=18)
    sunday_hour_to2 = fields.Float(string=_(u"To"), default=18, required=True)          
    distribution_intervals = fields.Integer(_('Intervals'))


    _sql_constraints = [
        ('time_check1', "CHECK (hour_from <= hour_to)", "The hour_to must be greater than the hour_from."),
        ('monday_time_check1', "CHECK (monday_hour_from <= monday_hour_to)", "The monday_hour_to must be greater than the monday_hour_from."),
        ('monday_time_check2', "CHECK (monday_hour_from2 <= monday_hour_to2)", "The monday_hour_to2 must be greater than the monday_hour_from2."),
        ('monday_time_check3', "CHECK (monday_hour_to <= monday_hour_from2)", "The monday_hour_from2 must be greater than the monday_hour_to."),
        ('tuesday_time_check1', "CHECK (tuesday_hour_from <= tuesday_hour_to)", "The tuesday_hour_to must be greater than the tuesday_hour_from."),
        ('tuesday_time_check2', "CHECK (tuesday_hour_from2 <= tuesday_hour_to2)", "The tuesday_hour_to2 must be greater than the tuesday_hour_from2."),
        ('tuesday_time_check3', "CHECK (tuesday_hour_to <= tuesday_hour_from2)", "The tuesday_hour_from2 must be greater than the tuesday_hour_to."),
        ('wednesday_time_check1', "CHECK (wednesday_hour_from <= wednesday_hour_to)", "The wednesday_hour_to must be greater than the wednesday_hour_from."),
        ('wednesday_time_check2', "CHECK (wednesday_hour_from2 <= wednesday_hour_to2)", "The wednesday_hour_to2 must be greater than the wednesday_hour_from2."),
        ('wednesday_time_check3', "CHECK (wednesday_hour_to <= wednesday_hour_from2)", "The wednesday_hour_from2 must be greater than the wednesday_hour_to."),
        ('thursday_time_check1', "CHECK (thursday_hour_from <= thursday_hour_to)", "The thursday_hour_to must be greater than the thursday_hour_from."),
        ('thursday_time_check2', "CHECK (thursday_hour_from2 <= thursday_hour_to2)", "The thursday_hour_to2 must be greater than the thursday_hour_from2."),
        ('thursday_time_check3', "CHECK (thursday_hour_to <= thursday_hour_from2)", "The thursday_hour_from2 must be greater than the thursday_hour_to."),
        ('friday_time_check1', "CHECK (friday_hour_from <= friday_hour_to)", "The friday_hour_to must be greater than the friday_hour_from."),
        ('friday_time_check2', "CHECK (friday_hour_from2 <= friday_hour_to2)", "The friday_hour_to2 must be greater than the friday_hour_from2."),
        ('friday_time_check3', "CHECK (friday_hour_to <= friday_hour_from2)", "The friday_hour_from2 must be greater than the friday_hour_to."),
        ('saturday_time_check1', "CHECK (saturday_hour_from <= saturday_hour_to)", "The saturday_hour_to must be greater than the saturday_hour_from."),
        ('saturday_time_check2', "CHECK (saturday_hour_from2 <= saturday_hour_to2)", "The saturday_hour_to2 must be greater than the saturday_hour_from2."),
        ('saturday_time_check3', "CHECK (saturday_hour_to <= saturday_hour_from2)", "The saturday_hour_from2 must be greater than the saturday_hour_to."),
        ('sunday_time_check1', "CHECK (sunday_hour_from <= sunday_hour_to)", "The sunday_hour_to must be greater than the sunday_hour_from."),
        ('sunday_time_check2', "CHECK (sunday_hour_from2 <= sunday_hour_to2)", "The sunday_hour_to2 must be greater than the sunday_hour_from2."),
        ('sunday_time_check3', "CHECK (sunday_hour_to <= sunday_hour_from2)", "The sunday_hour_from2 must be greater than the sunday_hour_to."),]


    @api.onchange('hour_from')
    def _change_hour_from(self):
        self.monday_hour_from = self.hour_from
        self.tuesday_hour_from = self.hour_from
        self.wednesday_hour_from = self.hour_from        
        self.thursday_hour_from = self.hour_from
        self.friday_hour_from = self.hour_from
        self.saturday_hour_from = self.hour_from
        self.sunday_hour_from = self.hour_from


    @api.onchange('hour_to')
    def _change_hour_to(self):
        self.monday_hour_to = self.hour_to
        self.tuesday_hour_to = self.hour_to
        self.wednesday_hour_to = self.hour_to        
        self.thursday_hour_to = self.hour_to
        # self.friday_hour_to = self.hour_to
        self.saturday_hour_to = self.hour_to
        self.sunday_hour_to = self.hour_to

        self.monday_hour_from2 = self.hour_to
        self.tuesday_hour_from2 = self.hour_to
        self.wednesday_hour_from2 = self.hour_to        
        self.thursday_hour_from2 = self.hour_to
        # self.friday_hour_from2 = self.hour_to
        self.saturday_hour_from2 = self.hour_to
        self.sunday_hour_from2 = self.hour_to

        self.monday_hour_to2 = self.hour_to
        self.tuesday_hour_to2 = self.hour_to
        self.wednesday_hour_to2 = self.hour_to        
        self.thursday_hour_to2 = self.hour_to
        # self.friday_hour_to2 = self.hour_to
        self.saturday_hour_to2 = self.hour_to
        self.sunday_hour_to2 = self.hour_to  


    @api.constrains('hour_from', 'hour_to','monday_hour_from', 'monday_hour_to','monday_hour_from2', 'monday_hour_to2','tuesday_hour_from', 'tuesday_hour_to','tuesday_hour_from2', 'tuesday_hour_to2','wednesday_hour_from', 'wednesday_hour_to','wednesday_hour_from2', 'wednesday_hour_to2','thursday_hour_from', 'thursday_hour_to','thursday_hour_from2', 'thursday_hour_to2','friday_hour_from', 'friday_hour_to','friday_hour_from2', 'friday_hour_to2','saturday_hour_from', 'saturday_hour_to','saturday_hour_from2', 'saturday_hour_to2','sunday_hour_from', 'sunday_hour_to','sunday_hour_from2', 'sunday_hour_to2' )
    def _check_hour_interval(self):
        if (self.hour_from < 0.0 or self.hour_to > 24.0 or
                self.hour_from >= self.hour_to):
            raise ValidationError(_(
                'Error ! You can not set hour_from greater or equal than hour_to'))
        if (self.monday_hour_from < 0.0 or self.monday_hour_to > 24.0 or
                self.monday_hour_from >= self.monday_hour_to):
            raise ValidationError(_(
                'Error ! for monday You can not set hour_from greater or equal than hour_to'))      
        if (self.monday_hour_from2 < 0.0 or self.monday_hour_to2 > 24.0 or
                self.monday_hour_from2 > self.monday_hour_to2):
            raise ValidationError(_(
                'Error ! for monday you can not set hour_from2 greater or equal than hour_to2'))                         
        if (self.tuesday_hour_from < 0.0 or self.tuesday_hour_to > 24.0 or 
                self.tuesday_hour_from >= self.tuesday_hour_to):
            raise ValidationError(_(
                'Error ! for tuesday you can not set hour_from greater or equal than hour_to'))    
        if (self.tuesday_hour_from2 < 0.0 or self.tuesday_hour_to2 > 24.0 or
                self.tuesday_hour_from2 > self.tuesday_hour_to2):
            raise ValidationError(_(
                'Error ! for tuesday you can not set hour_from2 greater or equal than hour_to2'))                    
        if (self.wednesday_hour_from < 0.0 or self.wednesday_hour_to > 24.0 or
                self.wednesday_hour_from >= self.wednesday_hour_to):
            raise ValidationError(_(
                'Error ! for wednesday you can not set hour_from greater or equal than hour_to')) 
        if (self.wednesday_hour_from2 < 0.0 or self.wednesday_hour_to2 > 24.0 or
                self.wednesday_hour_from2 > self.wednesday_hour_to2):
            raise ValidationError(_(
                'Error ! for wednesday you can not set hour_from2 greater or equal than hour_to2'))                       
        if (self.thursday_hour_from < 0.0 or self.thursday_hour_to > 24.0 or
                self.thursday_hour_from >= self.thursday_hour_to):
            raise ValidationError(_(
                'Error ! for thursday you can not set hour_from greater or equal than hour_to')) 
        if (self.thursday_hour_from2 < 0.0 or self.thursday_hour_to2 > 24.0 or
                self.thursday_hour_from2 > self.thursday_hour_to2):
            raise ValidationError(_(
                'Error ! for thursday you can not set hour_from2 greater or equal than hour_to2'))                       
        if (self.friday_hour_from < 0.0 or self.friday_hour_to > 24.0 or
                self.friday_hour_from >= self.friday_hour_to):
            raise ValidationError(_(
                'Error ! for friday you can not set hour_from greater or equal than hour_to'))    
        if (self.saturday_hour_from < 0.0 or self.saturday_hour_to > 24.0 or
                self.saturday_hour_from >= self.saturday_hour_to):
            raise ValidationError(_(
                'Error ! for saturday you can not set hour_from greater or equal than hour_to'))   
        if (self.saturday_hour_from2 < 0.0 or self.saturday_hour_to2 > 24.0 or
                self.saturday_hour_from2 > self.saturday_hour_to2):
            raise ValidationError(_(
                'Error ! for saturday you can not set hour_from2 greater or equal than hour_to2'))                  
        if (self.sunday_hour_from < 0.0 or self.sunday_hour_to > 24.0 or
                self.sunday_hour_from >= self.sunday_hour_to):
            raise ValidationError(_(
                'Error ! for sunday you can not set hour_from greater or equal than hour_to'))     
        if (self.sunday_hour_from2 < 0.0 or self.sunday_hour_to2 > 24.0 or
                self.sunday_hour_from2 > self.sunday_hour_to2):
            raise ValidationError(_(
                'Error ! for sunday you can not set hour_from2 greater or equal than hour_to2'))                                                                                                                                       
        return True

    @api.constrains(
        'monday', 'tuesday', 'wednesday', 'wednesday', 'thursday', 'friday',
        'saturday', 'sunday'
    )
    def _check_day_selected(self):
        if not any([self[x[0]] for x in self._days_of_week()]):
            raise ValidationError(
                _('Error ! You must set one day to delivery.')
            )
        return True

    def _days_of_week(self):
        return [
            ('monday', _('Monday')),
            ('tuesday', _('Tuesday')),
            ('wednesday', _('Wednesday')),
            ('thursday', _('Thursday')),
            ('friday', _('Friday')),
            ('saturday', _('Saturday')),
            ('sunday', _('Sunday')),
        ]

    # @api.multi
    def name_get(self):
        result = []
        for schedule in self:
            hour_from = '{0:02.0f}:{1:02.0f}'.format(
                *divmod(schedule.hour_from * 60, 60))
            hour_to = '{0:02.0f}:{1:02.0f}'.format(
                *divmod(schedule.hour_to * 60, 60))
            days_accepted = [d[1][:2] for d in self._days_of_week()
                             if schedule[d[0]]]
            days = (
                days_accepted and len(days_accepted) > 0 and
                len(days_accepted) < 7 and ', '.join(days_accepted) or
                _('All days')
            )
            result.append(
                (schedule.id, "{hour_from}-{hour_to} ({days})".format(
                    hour_from=hour_from,
                    hour_to=hour_to,
                    days=days)
                 )
            )
        return result
