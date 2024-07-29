# Copyright (c) 2024, Ayenda Kemp and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import pm4py
from pm4py.statistics.traces.generic.log import case_statistics
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.visualization.petri_net import visualizer as pn_visualizer

class LogenyProcessQuery(Document):

    def on_submit(self):
        self.run_process_mining()

    def update_doc_count(self):
        self.doc_count = frappe.db.count(self.doctype_selector, {
            'creation': ['between', [self.from_date, self.to_date]]
        })

@frappe.whitelist()
def get_all_doctypes(doctype, txt, searchfield, start, page_len, filters):
    doctypes = frappe.get_all('DocType', filters={'istable': 0}, fields=['name'])
    return [[doctype.name] * 2 for doctype in doctypes]

@frappe.whitelist()
def get_fields(doctype):
    meta = frappe.get_meta(doctype)
    fields = [(df.fieldname) for df in meta.fields if df.fieldtype in ['Data', 'Select', 'Link']]
    return fields

@frappe.whitelist()
def run_process_mining(data):
    import json
    import pandas as pd
    from pm4py.objects.log.util import dataframe_utils
    from pm4py.objects.conversion.log import factory as conversion_factory

    data = json.loads(data)
    doctype = data.get('doctype')
    activity_key = data.get('activity_key')
    from_date = data.get('from_date')
    to_date = data.get('to_date')

    # Fetch data from the database
    records = frappe.get_all(doctype, fields=['name as case_id', activity_key, 'creation'],
                             filters={'creation': ['between', [from_date, to_date]]})

    # Convert to DataFrame
    df = pd.DataFrame(records)
    df = dataframe_utils.convert_timestamp_columns_in_df(df)

    # Convert DataFrame to Event Log
    log = conversion_factory.apply(df)

    # Calculate statistics
    statistics = {
        'doc_count': len(log),
        'variants_count': len(case_statistics.get_variant_statistics(log)),
        'most_common_variant': case_statistics.get_variant_statistics(log)[0]['variant']
    }

    # Discover Petri Net
    net, initial_marking, final_marking = alpha_miner.apply(log)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    petri_net_path = '/assets/process_geni/petri_net.png'
    pn_visualizer.save(gviz, frappe.utils.get_files_path(petri_net_path))

    return {
        'statistics': statistics,
        'petri_net_url': frappe.utils.get_url(petri_net_path)
    }
