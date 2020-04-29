recipients = list()

new_recipient = dict()
new_recipient['name'] = 'Luís'
new_recipient['email'] = 'luis.paimadv@gmail.com'
new_recipient['group'] = 'signers'
new_recipient['routingOrder'] = 1
new_recipient['tabs'] = [
  {
      'type': 'signHere',
      'anchorString': 'generate_anchor(signHere, item.email)'
  },
]
recipients.append(new_recipient)

def Luis(recipients):
    for index, recipient in enumerate(recipients):
        if "tabs" in recipient.keys():
            # rotated_tabs = {}
            for tab in recipient["tabs"]:
                if "type" not in tab.keys():
                    raise
        return tab

print(Luis(recipients))
