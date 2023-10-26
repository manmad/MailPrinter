import imaplib
import email
import os
import sys
import time  # Import the time module for adding a delay

from mailprinter.core import printer
from mailprinter.core import config

def read_email():
    configuration = config.get_config()
    print('Checking for emails')

    while True:  # Keep trying in case of network errors
        try:
            if configuration['SSL_required']:
                m = imaplib.IMAP4_SSL(configuration['IMAP_server'], configuration['IMAP_port'])
            else:
                m = imaplib.IMAP4(configuration['IMAP_server'], configuration['IMAP_port'])

            try:
                username = os.environ['MAIL_PRINTER_USERNAME']
                password = os.environ['MAIL_PRINTER_PASSWORD']
            except KeyError:
                print('Please set the username and password as environment variables. '
                      'See README.md for more details.', file=sys.stderr)
                sys.exit(-1)

            m.login(username, password)
            m.select('Inbox')

            # only check unseen emails
            typ, data = m.search(None, '(UNSEEN)')
            for num in data[0].split():
                typ, data = m.fetch(num, '(RFC822)')
                msg = email.message_from_bytes(data[0][1])

                for part in msg.walk():
                    if part.get_content_type() == 'application/pdf':
                        printer.print_pdf(part.get_payload(decode=True),
                                          configuration['printer_name'])

            m.logout()  # Logout to release resources
            break  # Break out of the loop if everything is successful

        except (imaplib.IMAP4.error, ConnectionError) as e:
            print(f"Error: {e}")
            print("Retrying in 10 seconds...")
            time.sleep(10)  # Wait for 10 seconds before retrying
