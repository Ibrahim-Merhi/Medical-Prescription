"""Explicit transaction-scoped discharge/reactivation, gated for staging validation."""
import frappe
from medical_prescription.permissions import require_roles
from medical_prescription.services.common import lock_admission, require_validation

ACTIVE = ['Admission Scheduled','Admitted','Discharge Scheduled']


def transition(inpatient_record, reactivate=False, reason=None):
    require_roles({'System Manager','Reactivate Admission'} if reactivate else
                  {'System Manager','Pharmacist','Discharge Patient'})
    require_validation('discharge')
    if not reason:
        frappe.throw('A reason is required')
    ip=frappe.get_doc('Inpatient Record',inpatient_record)
    ip.check_permission('read')
    # Patient lock serializes transitions across distinct admissions of one patient.
    frappe.db.sql('select name from `tabPatient` where name=%s for update',(ip.patient,))
    lock_admission(ip.name)
    ip.reload()
    if ip.docstatus==2:
        frappe.throw('Cancelled admissions cannot be changed')
    if reactivate and ip.status!='Discharged':
        frappe.throw('Only discharged admissions can be reactivated')
    if reactivate and frappe.db.exists('Inpatient Record',{'patient':ip.patient,
        'name':['!=',ip.name],'docstatus':['!=',2],'status':['in',ACTIVE]}):
        frappe.throw('Patient already has another active admission')
    if not reactivate and ip.status=='Discharged':
        return {'success':True,'already_recorded':True}
    status='Admission Scheduled' if reactivate else 'Discharged'
    frappe.db.set_value('Inpatient Record',ip.name,{'status':status,
        'custom_discharge_status':'Not Started' if reactivate else 'Discharged'})
    another=frappe.db.exists('Inpatient Record',{'patient':ip.patient,'name':['!=',ip.name],
        'docstatus':['!=',2],'status':['in',ACTIVE]})
    values={'custom_admission_status':'Active' if reactivate or another else 'Discharged'}
    if reactivate:
        values.update(inpatient_record=ip.name,inpatient_status=status)
    elif not another:
        values.update(inpatient_record='',inpatient_status='')
    frappe.db.set_value('Patient',ip.patient,values)
    names=frappe.get_all('Medical Prescription',filters={'patient':ip.patient,
        'inpatient_record':ip.name,'docstatus':['!=',2]},fields=['name'],
        order_by='prescription_date desc, creation desc, name desc')
    selected=names[:1] if reactivate else names
    for record in selected:
        rx=frappe.get_doc('Medical Prescription',record.name)
        frappe.db.set_value('Medical Prescription',rx.name,{'status':'Active' if reactivate else 'Discharged',
            'discharge_initiated':0 if reactivate else rx.discharge_initiated,
            'discharge_finalized':0 if reactivate else 1,'locked':0 if reactivate else 1})
        for row in rx.administration_schedule:
            # Completed row contents are immutable in both directions.
            if not row.completed:
                frappe.db.set_value('Medication Administration Schedule',row.name,
                    {'disabled':0 if reactivate else 1,'locked':0 if reactivate else 1})
        rx.add_comment('Info',('Admission reactivated: ' if reactivate else 'Discharge finalized: ')+str(reason))
    ip.add_comment('Info',('Reactivated: ' if reactivate else 'Discharged: ')+str(reason))
    return {'success':True,'inpatient_record':ip.name,'status':status,'prescriptions_updated':len(selected)}

