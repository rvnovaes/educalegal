import xmltodict

from datetime import datetime as dt

from web.api.docusign_translations import envelope_statuses, recipient_statuses_dict, recipient_types_dict


def docusign_xml_parser(data):
    envelope_data = dict()
    xml = xmltodict.parse(data)["DocuSignEnvelopeInformation"]
    envelope_data["envelope_id"] = xml["EnvelopeStatus"]["EnvelopeID"]
    envelope_data["envelope_status"] = xml["EnvelopeStatus"]["Status"]
    envelope_data["envelope_created"] = xml["EnvelopeStatus"]["Created"]
    envelope_data["envelope_sent"] = xml["EnvelopeStatus"]["Sent"]
    envelope_data["envelope_time_generated"] = xml["EnvelopeStatus"]["TimeGenerated"]

    envelope_data_translated = envelope_data.copy()

    #formatting strings: 2020-04-15T11:20:19.693
    envelope_data_translated['envelope_created'] = envelope_data_translated['envelope_created'].replace("T", " ").split(".")[0]
    envelope_data_translated['envelope_sent'] = envelope_data_translated['envelope_sent'].replace("T", " ").split(".")[0]
    envelope_data_translated['envelope_time_generated'] = envelope_data_translated['envelope_time_generated'].replace("T", " ").split(".")[0]

    #converting US dates to Brazil dates
    envelope_data_translated['envelope_created'] = str(dt.strptime(envelope_data_translated['envelope_created'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S'))
    envelope_data_translated['envelope_sent'] = str(dt.strptime(envelope_data_translated['envelope_sent'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S'))
    envelope_data_translated['envelope_time_generated'] = str(dt.strptime(envelope_data_translated['envelope_time_generated'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S'))

    envelope_data_translated["envelope_status"] = str(envelope_data_translated["envelope_status"]).lower()
    if envelope_data_translated["envelope_status"] in envelope_statuses.keys():
        envelope_data_translated["envelope_status"] = envelope_statuses[envelope_data_translated["envelope_status"]]
    else:
        envelope_data_translated["envelope_status"] = 'não encontrado'

    e_status_detail = (
        "ID do envelope: "
        + envelope_data["envelope_id"]
        + "<br>"
        + "Status do envelope: "
        + envelope_data_translated["envelope_status"]
        + "<br>"
        + "Data de criação: "
        + envelope_data["envelope_created"]
        + "<br>"
        + "Data de envio: "
        + envelope_data["envelope_sent"]
        + "<br>"
        + "Criação do envelope: "
        + envelope_data["envelope_time_generated"]
        + "<br>"
    )
    envelope_data["envelope_status_detail_message"] = e_status_detail
    recipient_statuses = xml["EnvelopeStatus"]["RecipientStatuses"]["RecipientStatus"]

    # translation of the type and status of the recipient
    for recipient_status in recipient_statuses:
        recipient_status['Type'] = str(recipient_status['Type']).lower()
        if recipient_status['Type'] in recipient_types_dict.keys():
            recipient_status['Type'] = recipient_types_dict[recipient_status['Type']]
        else:
            recipient_status['Type'] = 'não encontrado'
        recipient_status['Status'] = str(recipient_status['Status']).lower()
        if recipient_status['Status'] in recipient_statuses_dict.keys():
            recipient_status['Status'] = recipient_statuses_dict[recipient_status['Status']]
        else:
            recipient_status['Status'] = 'não encontrado'

    r_status_detail = ""
    for r in recipient_statuses:
        r_status_detail += (
                r['RoutingOrder']
                + " - "
                + r['UserName']
                + " - "
                + r['Email']
                + " - "
                + r['Type']
                + " - "
                + r['Status']
                + "\n"
        )
    envelope_data['envelope_recipient_status_detail_message'] = r_status_detail
    all_details = (
            "### Detalhes do Envelope ###\n"
            + e_status_detail
            + "\n"
            + "### Detalhes dos Destinatários ###\n"
            + r_status_detail
            + "\n"
    )
    envelope_data['envelope_all_details_message'] = all_details
    envelope_status = str(envelope_data["envelope_status"]).lower()

    if envelope_status == "completed":
        print("Teste Completed")

        for pdf in xml['DocumentPDFs']['DocumentPDF']:
            if pdf['DocumentType'] == "CONTENT":
                print("CONTENT")

    return envelope_data


if __name__ == '__main__':

    with open("2020-02-29T10_49_11.6502835.xml", 'r') as file:
        print(docusign_xml_parser(file.read())['envelope_all_details_message'])

    with open("2020-02-29T10_52_19.4028499.xml", 'r') as file:
        print(docusign_xml_parser(file.read())['envelope_all_details_message'])

    with open("2020-02-29T10_52_54.4970792.xml", 'r') as file:
        print(docusign_xml_parser(file.read())['envelope_all_details_message'])







