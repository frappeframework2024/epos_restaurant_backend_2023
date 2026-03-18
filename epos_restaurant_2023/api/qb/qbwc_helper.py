import xml.etree.ElementTree as ET
import json



def qbxml_to_json(xml_string):
    root = ET.fromstring(xml_string)
    result = {
        "customery_type":[],
        "customer": [],
        "vendor_type": [],
        "item": [],
        "payment_method": [],
        "class": [],
        "account": []
    }

    # Helper to convert XML element to dict
    def elem_to_dict(elem):
        data = {}
        for child in elem:
            # Recursively parse nested elements if any
            if len(child):
                data[child.tag] = elem_to_dict(child)
            else:
                data[child.tag] = child.text
        return data

    # Map QBXML response tags to our JSON keys
    tag_map = {
        "CustomerTypeQueryRs":"customery_type",
        "CustomerQueryRs": "customer",
        "VendorTypeQueryRs": "vendor_type",
        "ItemQueryRs": "item",
        "PaymentMethodQueryRs": "payment_method",
        "ClassQueryRs": "class",
        "AccountQueryRs": "account"
    }

    for resp in root.findall(".//QBXMLMsgsRs/*"):
        key = tag_map.get(resp.tag)
        if key:
            # QBWC can return a single Ret object or multiple Ret objects
            ret_tag = resp.tag.replace("QueryRs", "Ret")  # e.g., CustomerQueryRs -> CustomerRet
            ret_elements = resp.findall(ret_tag)
            if not ret_elements:
                # Sometimes it's just one object
                if resp.find(ret_tag) is not None:
                    ret_elements = [resp.find(ret_tag)]
            for ret in ret_elements:
                result[key].append(elem_to_dict(ret))

    return result