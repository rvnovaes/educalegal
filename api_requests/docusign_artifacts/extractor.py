from bs4 import BeautifulSoup


with open('T2020-02-16T16_08_05.6311441.xml', 'r') as data:
    xml = BeautifulSoup(data, "xml")
    envelope_id = xml.EnvelopeStatus.EnvelopeID.string
    time_generated = xml.EnvelopeStatus.TimeGenerated.string
    recipient_statuses = xml.find_all("RecipientStatus")

    for i in recipient_statuses:
        recipient_email = i.Email.string
        recipient_user_name = i.UserName.string
        recipient_routing_order = i.RoutingOrder.string


