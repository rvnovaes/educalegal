import xmltodict

def docusign_xml_parser(data):
    envelope_data = dict()
    xml = xmltodict.parse(data)['DocuSignEnvelopeInformation']
    envelope_data['envelope_id'] = xml['EnvelopeStatus']['EnvelopeID']
    envelope_data['envelope_status'] = xml['EnvelopeStatus']['Status']
    envelope_data['envelope_created'] = xml['EnvelopeStatus']['Created']
    envelope_data['envelope_sent'] = xml['EnvelopeStatus']['Sent']
    envelope_data['envelope_time_generated'] = xml['EnvelopeStatus']['TimeGenerated']

    e_status_detail = (
            "Envelope ID: "
            + envelope_data['envelope_id']
            + "\n"
            + "Envelope Status: "
            + envelope_data['envelope_status']
            + "\n"
            + "Envelope Created: "
            + envelope_data['envelope_created']
            + "\n"
            + "Envelope Sent: "
            + envelope_data['envelope_sent']
            + "\n"
            + "Time Generated: "
            + envelope_data['envelope_time_generated']
            + "\n"
    )
    envelope_data['envelope_status_detail_message'] = e_status_detail
    recipient_statuses = xml['EnvelopeStatus']['RecipientStatuses']['RecipientStatus']

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

    if envelope_data['envelope_status'] == "Completed":
        print("Teste Completed")

        for pdf in xml['DocumentPDFs']['DocumentPDF']:
            if pdf['DocumentType'] == "CONTENT":
                print("CONTENT")

    return envelope_data


if __name__ == '__main__':

    with open("2020-02-29T08_46_47.7061489.xml", 'r') as file:
        print(docusign_xml_parser(file.read())['envelope_all_details_message'])

    with open("2020-02-29T08_51_25.6544563.xml", 'r') as file:
        print(docusign_xml_parser(file.read())['envelope_all_details_message'])


    with open("2020-02-29T08_56_02.6043592.xml", 'r') as file:
        print(docusign_xml_parser(file.read())['envelope_all_details_message'])







