import os
import sys
import click
import pathlib
import logging
import calendar
import time
import pathlib
from colorama import Fore, Style
from datetime import datetime
from datetime import date

g_lookup = {}
g_message_to_field_name_lookup = {}

DEFAULT_OUTDIR = "/tmp/" + os.path.basename(__file__) + '/' + str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))

g_reminders = ["Consider whether you need to add any options", "Consider whether you need to reserve any tags or positions"]

LOGGING_FORMAT = "%(levelname)s : %(asctime)s : %(pathname)s : %(lineno)d : %(message)s"

LOG_LEVEL = logging.INFO


def display_reminders():
    """Display friendly reminders
    """
    print("\n\n====================\nReminders:\n")
    for i, reminder in enumerate(g_reminders, start=1):
        print("{}. {}".format(i, reminder))


def display_messages():
    """Display the message definitions
    """
    print("\n\n====================\nHere are the message definitions:")
    for count, message in enumerate(g_lookup, start=1):
        print("\n{}. {} has the following fields:".format(count, message))
        # position = 0
        for position, field_name in enumerate(g_lookup[message]):
            position += 1
            datatype = g_lookup[message][field_name]
            print("  {} {} = {};".format(datatype, field_name, position))


def write_proto_file(outfile):
    """Write the protocol buffer message definitions to the output file
    """
    with open(outfile, "w") as f:
        f.write("syntax = \"proto3\";\n\n")


        for count, message in enumerate(g_lookup, start=1):
            logging.info("Writing definition for message '{}'".format(message))
            f.write("message {} {{\n".format(message))
            field_list = []
            for position, field_name in enumerate(g_lookup[message]):
                position += 1
                datatype = g_lookup[message][field_name]
                field_list.append("  {} {} = {}".format(datatype, field_name, position))
            f.write(";\n".join(field_list))
            f.write("\n}\n\n")
    
    print("\nWrote '{}'".format(outfile))


def prompt_for_message_details(msg_num):
    """Prompt the user for the details for this protocol buffers message
    """    
    print("\nReady for details for message number '{}'".format(msg_num))
    msg_name = input("What is the message name? ")
    while (msg_name is None or msg_name == ''):
        msg_name = input("What is the message name? ")

    msg_name = msg_name.strip()

    if not msg_name[0].isupper():
        msg_name = msg_name.capitalize()

    if not msg_name.endswith('Message'):
        msg_name += 'Message'

    print("\nWhat are the fields for message '{}'?".format(msg_name))
    prompt_for_field_details(msg_name, 1)

    ans = input("Add another message? [Y/n] ")
    if ans is None or ans == '':
        ans = 'y'

    ans = ans.strip()
    ans = ans.lower()

    if ans == 'y':
        msg_num += 1
        prompt_for_message_details(msg_num)


def prompt_for_field_details(msg_name, field_num):
    """Prompt the user for details for this protocol buffers message's field
    """
    global g_message_to_field_name_lookup

    field_name = input("\nfield name? ")
    while field_name is None or field_name == '':
        field_name = input("\nfield name? ")

    field_name = field_name.strip()
    if msg_name not in g_message_to_field_name_lookup:
        g_message_to_field_name_lookup[msg_name] = {}

    while field_name in g_message_to_field_name_lookup[msg_name]:
        print("field name '{}' has already been specified for message '{}".format(field_name, msg_name))

    field_name = field_name.lower()
    g_message_to_field_name_lookup[msg_name] = field_name

    datatype = input("\ndatatype? ")
    while datatype is None or datatype == '':
        datatype = input("\ndatatype? ")

    global g_lookup
    if msg_name not in g_lookup:
        g_lookup[msg_name] = {}

    g_lookup[msg_name][field_name] = datatype

    ans = input("Add another field? [Y/n] ")
    if ans is None or ans == '':
        ans = 'y'

    ans = ans.strip()
    ans = ans.lower()
    if ans == 'y':
        field_num += 1
        prompt_for_field_details(msg_name, field_num)
    

@click.command()
@click.option('--outdir', help='The output directory, default is /tmp/proto_builder.py/[timestamp]')
@click.option('--outfile', help='The output file, default is [outdir]/proto_builder.py.proto')
@click.option('--logfile', help="The log file, default is [outdir]/proto_builder.py.log")
def main(outdir, outfile, logfile):
    """Script for building protocol buffer proto3 files
    """

    error_ctr = 0

    if outdir is None:
        outdir = DEFAULT_OUTDIR
        print(Fore.YELLOW + "--outdir was not specified and therefore was set to '{}'".format(outdir))
        print(Style.RESET_ALL + '', end='')

    assert isinstance(outdir, str)

    if not os.path.exists(outdir):
        pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
        print(Fore.YELLOW + "Created output directory '{}'".format(outdir))
        print(Style.RESET_ALL + '', end='')

    if logfile is None:
        logfile = outdir + '/' + os.path.basename(__file__) + '.log'
        print(Fore.YELLOW + "--logfile was not specified and therefore was set to '{}'".format(logfile))
        print(Style.RESET_ALL + '', end='')

    assert isinstance(logfile, str)

    if outfile is None:
        outfile = outdir + '/' + os.path.basename(__file__) + '.proto'
        print(Fore.YELLOW + "--outfile was not specified and therefore was set to '{}'".format(outfile))
        print(Style.RESET_ALL + '', end='')

    assert isinstance(outfile, str)
 
 
    logging.basicConfig(filename=logfile, format=LOGGING_FORMAT, level=LOG_LEVEL)

    prompt_for_message_details(1)
    display_messages()
    write_proto_file(outfile)
    display_reminders()


if __name__ == "__main__":
    main()