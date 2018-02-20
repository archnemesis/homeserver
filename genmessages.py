import argparse
import re
import json
import sys
import io
import os
import shutil
import math


TYPES = {
    'uint32_t':     (4, 'I', 'I'),
    'int32_t':      (4, 'i', 'i'),
    'uint16_t':     (2, 'H', 'H'),
    'int16_t':      (2, 'h', 'h'),
    'float':        (4, 'f', 'f'),
    'double':       (8, 'd', 'd'),
    'char':         (1, 'c', 's'),
}

MESSAGE_H_TEMPLATE = """
#ifndef _MESSAGES_H_
#define _MESSAGES_H_

#define MESSAGE_HEADER_SIZE 3
#define MESSAGE_MAX_DATA_SIZE %(max_size_int)d
#define MESSAGE_MAX_TOTAL_SIZE (MESSAGE_HEADER_SIZE + MESSAGE_MAX_DATA_SIZE)

struct __attribute__((__packed__)) message {
    uint8_t id;
    uint16_t size;
    uint32_t data[MESSAGE_MAX_DATA_SIZE];
};

#endif
"""

HEADER_TEMPLATE = """
#ifndef _%(name_uc)s_MESSAGE_H_
#define _%(name_uc)s_MESSAGE_H_

#include "message.h"

struct __attribute__((__packed__)) %(name)s_message {
%(struct_members)s
};

/**
 * Encode a message to a buffer, making it ready to send.
 * @param message
 * @param %(name)s_message
 */
void %(name)s_encode(struct message * message, struct %(name)s_message * %(name)s);

/**
 * Decode a %(name)s_message stored in a message wrapper.
 * @param message
 * @param %(name)s_message
 */
void %(name)s_decode(struct message * message, struct %(name)s_message * %(name)s);

/**
 * Shortcut to send a message.
 * @param message
 */
void %(name)s_send(struct %(name)s_message * %(name)s);

#endif
"""

SOURCE_TEMPLATE = """
#include "%(name)s.h"

void %(name)s_encode(struct message * message, struct %(name)s_message * %(name)s) {
    message->id = %(id)d;
    message->size = %(size)d;
    memcpy((void *)message->data, %(name)s, sizeof(struct %(name)s_message));
}

void %(name)s_decode(struct message * message, struct %(name)s_message * %(name)s) {
    memcpy((void *)%(name)s, (void *)message, sizeof(struct %(name)s_message));
}

void %(name)s_send(struct %(name)s_message * message) {
    (void)message;
}
"""

MESSAGE_INIT_TEMPLATE = """
import struct


def pack_message(message):
    header = MessageHeader()
    header.message_id = message.MESSAGE_ID
    header.message_size = message.MESSAGE_SIZE
    header_data = header.pack()
    message_data = message.pack()

    data = struct.pack('<cc3scc%ds' % message.MESSAGE_SIZE, b'A', b'E', header_data, b'E', b'A', message_data)
    return data


class Message(object):
    @classmethod
    def cls_for_message_id(cls, message_id):
        for subclass in cls.__subclasses__():
            if subclass.MESSAGE_ID == message_id:
                return subclass
        else:
            raise RuntimeError("No message class matching %s" % message_id)


class MessageHeader(Message):
    MESSAGE_ID = 0
    MESSAGE_SIZE = 3
    STRUCT_FORMAT = "<BH"

    def __init__(self, message_id=None, message_size=None):
        self.message_id = message_id
        self.message_size = message_size

    def __str__(self):
        return "<MessageHeader(%d, %d)>" % (self.message_id, self.message_size)

    def pack(self):
        return struct.pack(self.STRUCT_FORMAT, self.message_id, self.message_size)
"""

def cc2us(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def format_c_type(ctype, name):
    try:
        i = ctype.index("[")
        return "%s %s%s" % (ctype[:i], name, ctype[i:])
    except ValueError:
        return "%s %s" % (ctype, name)


def get_max_message_size(messages):
    max_size = 0
    for messagedef in messages:
        total_size = 0
        for param in messagedef['params']:
            if param['type'] in TYPES.keys():
                total_size = TYPES[param['type']][0]
            else:
                for t in TYPES.keys():
                    if param['type'].startswith("%s[" % t):
                        matches = re.search("%s\[([0-9]+)\]" % t, param['type'])
                        count = int(matches.group(1))
                        total_size = TYPES[t][0] * count
        if total_size > max_size:
            max_size = total_size
    return max_size


def process_message(code_format, messagedef, output_directory):
    total_size = 0
    struct_format = "<"
    params = []

    for param in messagedef['params']:
        if param['type'] in TYPES.keys():
            total_size += TYPES[param['type']][0]
            struct_format += TYPES[param['type']][1]
        else:
            for t in TYPES.keys():
                if param['type'].startswith("%s[" % t):
                    matches = re.search("%s\[([0-9]+)\]" % t, param['type'])
                    count = int(matches.group(1))
                    total_size += TYPES[t][0] * count
                    struct_format += "%d%s" % (count, TYPES[t][2])

    output = []

    if code_format == "python":
        output = []
        output.append("import struct")
        output.append("from .message import Message")
        output.append("")
        output.append("class %sMessage(Message):" % messagedef['name'])
        output.append("    MESSAGE_ID = %d" % messagedef['id'])
        output.append("    MESSAGE_SIZE = %d" % total_size)
        output.append("    STRUCT_FORMAT = \"%s\"" % struct_format)
        output.append("")
        output.append("    def __init__(self, %s):" % ", ".join(["%s=None" % name for name in [p['name'] for p in messagedef['params']]]))

        for p in messagedef['params']:
            output.append("        self.%s = %s" % (p['name'], p['name']))

        output.append("    ")
        output.append("    def pack(self):")
        output.append("        return struct.pack(self.STRUCT_FORMAT, %s)" % ", ".join(["self.%s" % name for name in [p['name'] for p in messagedef['params']]]))
        output.append("")
        output.append("")

        with open(os.path.join(output_directory, "%s.py" % cc2us(messagedef['name'])), "w") as fp:
            fp.write("\n".join(output))

    elif code_format == "c":
        header_fp = open(os.path.join(output_directory, "%s.h" % cc2us(messagedef['name'])), "w")
        source_fp = open(os.path.join(output_directory, "%s.c" % cc2us(messagedef['name'])), "w")

        header_output = []
        source_output = []

        header_output.append("#ifndef _%s_MESSAGE_H_" % cc2us(messagedef['name']).upper())
        header_output.append("#define _%s_MESSAGE_H_" % cc2us(messagedef['name']).upper())
        header_output.append("")

        struct_members = []
        for p in messagedef['params']:
            struct_members.append("  %s;" % format_c_type(p['type'], p['name']))
        struct_members = "\n".join(struct_members)

        header_output = HEADER_TEMPLATE % {
            "name": cc2us(messagedef['name']),
            "name_uc": cc2us(messagedef['name']).upper(),
            "struct_members": struct_members,
            "id": messagedef['id'],
            "size": total_size
            }

        source_output = SOURCE_TEMPLATE % {
            "name": cc2us(messagedef['name']),
            "name_uc": cc2us(messagedef['name']).upper(),
            "struct_members": struct_members,
            "id": messagedef['id'],
            "size": total_size
        }

        header_fp.write(header_output)
        header_fp.close()

        source_fp.write(source_output)
        source_fp.close()


def process_format_python(message_defs, output_directory):
    message_names = [message['name'] for message in message_defs]

    with open(os.path.join(output_directory, "__init__.py"), "w") as fp:
        fp.write("from .message import pack_message\n")
        fp.write("from .message import Message, MessageHeader\n")
        for name in message_names:
            fp.write("from .%s import %sMessage\n" % (cc2us(name).lower(), name))

    with open(os.path.join(output_directory, "message.py"), "w") as fp:
        fp.write(MESSAGE_INIT_TEMPLATE)

    for message in message_defs:
        process_message("python", message, output_directory)


def process_format_c(message_defs, output_directory):
    message_names = [message['name'] for message in message_defs]

    with open(os.path.join(output_directory, "message.h"), "w") as fp:
        for name in message_names:
            fp.write("#include \"%s.h\"\n" % cc2us(name))

        fp.write("\n")
        fp.write(MESSAGE_H_TEMPLATE % {
            "max_size_int": math.ceil(get_max_message_size(message_defs) / 4.0)
        })

    for message in message_defs:
        process_message("c", message, output_directory)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="JSON file containing message definitions")
    parser.add_argument("outdir", help="Output directory")
    parser.add_argument("--format", default="python", help="Output code format (python or c)")
    args = parser.parse_args()

    filename = args.filename
    output_directory = args.outdir

    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)
    else:
        shutil.rmtree(output_directory)
        os.mkdir(output_directory)

    with open(filename, 'r') as defp:
        message_defs = json.load(defp)

        if args.format == "c":
            process_format_c(message_defs, output_directory)
        elif args.format == "python":
            process_format_python(message_defs, output_directory)

    print("Finished")

if __name__ == "__main__":
    main()
