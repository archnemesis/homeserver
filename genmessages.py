import argparse
import re
import json
import sys
import io
import os
import shutil
import math


TYPES = {
    'uint32_t':     (4, 'I', 'I', "0"),
    'int32_t':      (4, 'i', 'i', "0"),
    'uint16_t':     (2, 'H', 'H', "0"),
    'int16_t':      (2, 'h', 'h', "0"),
    'float':        (4, 'f', 'f', "0"),
    'double':       (8, 'd', 'd', "0"),
    'char':         (1, 'c', 's', "bytes()"),
}

MESSAGE_H_TEMPLATE = """
#ifndef _MESSAGES_H_
#define _MESSAGES_H_

#include <stdint.h>
#include "FreeRTOS.h"

#if defined ( __GNUC__ ) && !defined (__CC_ARM) /* GNU Compiler */
  #ifndef __weak
    #define __weak   __attribute__((weak))
  #endif /* __weak */
#endif /* __GNUC__ */

%(enums)s

#define MESSAGE_HEADER_SIZE %(message_header_size)d
#define MESSAGE_MAX_DATA_SIZE %(max_size)d
#define MESSAGE_MAX_TOTAL_SIZE (MESSAGE_HEADER_SIZE + MESSAGE_MAX_DATA_SIZE)

struct message {
    uint8_t id;
    uint16_t size;
%(message_params)s
    uint32_t data[%(max_size_int)d];
} __packed;

typedef struct message message_t;

void message_send(message_t *message);

%(includes)s

__weak void message_send(message_t *message)
{
    vPortFree(message);
}

#endif
"""

HEADER_TEMPLATE = """
#ifndef _%(name_uc)s_MESSAGE_H_
#define _%(name_uc)s_MESSAGE_H_

#include "message.h"
#include <stdint.h>

#define MESSAGE_%(name_uc)s_ID %(id)d
#define MESSAGE_%(name_uc)s_LENGTH %(size)d

/**
 * %(description)s
 */
struct %(name)s_message {
%(struct_members)s
} __packed;

typedef struct %(name)s_message %(name)s_message_t;

/**
 * Encode a message to a buffer, making it ready to send.
 * @param message
 * @param %(name)s_message
 */
void %(name)s_encode(message_t *message, %(name)s_message_t *%(name)s);

/**
 * Decode a %(name)s_message stored in a message wrapper.
 * @param message
 * @param %(name)s_message
 */
void %(name)s_decode(message_t *message, %(name)s_message_t *%(name)s);

/**
 * Shortcut to send a message.
 * @param message
 */
void %(name)s_send(%(name)s_message_t *%(name)s);

#endif
"""

SOURCE_TEMPLATE = """
#include <string.h>
#include "FreeRTOS.h"
#include "%(name)s.h"

message_t *%(name)s_encode_alloc(%(name)s_message_t *%(name)s) {
    message_t *message = pvPortMalloc(MESSAGE_HEADER_SIZE + MESSAGE_%(name_uc)s_LENGTH);
    %(name)s_encode(message, %(name)s);
    return message;
}

void %(name)s_encode(message_t *message, %(name)s_message_t *%(name)s) {
    message->id = %(id)d;
    message->size = %(size)d;
    memcpy((void *)message->data, %(name)s, sizeof(%(name)s_message_t));
}

void %(name)s_decode(message_t *message, %(name)s_message_t *%(name)s) {
    memcpy((void *)%(name)s, (void *)message->data, sizeof(%(name)s_message_t));
}

void %(name)s_send(%(name)s_message_t *%(name)s) {
    message_t *message = %(name)s_encode_alloc(%(name)s);
    message_send(message);
}
"""

MESSAGE_PY_TEMPLATE = """
import struct
from .message import Message

class {name}Message(Message):
    MESSAGE_ID = {id}
    MESSAGE_SIZE = {total_size}
    STRUCT_FORMAT = "{struct_format}"

    {struct_classes}

    def __init__(self, {ctor_args}):
        {ctor_inits}

    @classmethod
    def unpack(cls, data):
        data = struct.unpack(cls.STRUCT_FORMAT, data)
        obj = cls()
        {unpack_inits}
        return obj

    def pack(self):
        struct_data = []
        {pack_inits}
        return struct.pack(self.STRUCT_FORMAT, *struct_data)
"""

MESSAGE_INIT_TEMPLATE = """
import struct


MESSAGE_HEADER_SIZE = {header_size}
MESSAGE_MAX_DATA_SIZE = {max_size}
MESSAGE_MAX_TOTAL_SIZE = MESSAGE_HEADER_SIZE + MESSAGE_MAX_DATA_SIZE


def pack_message(message):
    header = MessageHeader()
    header.message_id = message.MESSAGE_ID
    header.message_size = message.MESSAGE_SIZE
    header_data = header.pack()
    message_data = message.pack()

    data = struct.pack('<cc%ds%ds' % (header.MESSAGE_SIZE, message.MESSAGE_SIZE), b'A', b'E', header_data, message_data)
    return data


{enums}


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
    MESSAGE_SIZE = {header_size}
    STRUCT_FORMAT = "<BH{header_struct_format}"

    def __init__(self, message_id=None, message_size=None{header_args}):
        self.message_id = message_id
        self.message_size = message_size
{header_inits}

    def __str__(self):
        return "<MessageHeader(%d, %d)>" % (self.message_id, self.message_size)

    @classmethod
    def unpack(cls, data):
        msg_data = struct.unpack(cls.STRUCT_FORMAT, data)
        obj = cls()
        obj.message_id = msg_data[0]
        obj.message_size = msg_data[1]
{header_unpacks}
        return obj

    def pack(self):
        return struct.pack(self.STRUCT_FORMAT, self.message_id, self.message_size{header_packs})
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


def get_param_total_size(params):
    total_size = 0
    for param in params:
        if param['type'] in TYPES.keys():
            total_size += TYPES[param['type']][0]
        else:
            if param['type'].startswith('struct'):
                struct_size = get_param_total_size(param['params'])
                if param['type'].startswith("struct["):
                    matches = re.search("struct\[([0-9]+)\]", param['type'])
                    count = int(matches.group(1))
                    struct_size = struct_size * count
                total_size += struct_size
            else:
                for t in TYPES.keys():
                    if param['type'].startswith("%s[" % t):
                        matches = re.search("%s\[([0-9]+)\]" % t, param['type'])
                        count = int(matches.group(1))
                        total_size += TYPES[t][0] * count
    return total_size


def get_max_message_size(messages):
    max_size = 0
    for messagedef in messages:
        total_size = get_param_total_size(messagedef['params'])
        if total_size > max_size:
            max_size = total_size
    return max_size


def get_message_struct_format(params):
    struct_format = "<"

    for param in params:
        if param['type'] in TYPES.keys():
            struct_format += TYPES[param['type']][1]
        else:
            if param['type'].startswith('struct'):
                mult = 1
                if param['type'].index('[') > 0:
                    matches = re.search("struct\[([0-9]+)\]", param['type'])
                    mult = int(matches.group(1))
                for i in range(mult):
                    struct_format += "%ds" % get_param_total_size(param['params'])
            else:
                for t in TYPES.keys():
                    if param['type'].startswith("%s[" % t):
                        matches = re.search("%s\[([0-9]+)\]" % t, param['type'])
                        count = int(matches.group(1))
                        struct_format += "%d%s" % (count, TYPES[t][2])
    return struct_format


def process_struct_params(params, padding=2):
    struct_members = []
    for p in params:
        if p['type'].startswith('struct'):
            count = ""
            if p['type'].index('[') > 0:
                matches = re.search("struct\[([0-9]+)\]", p['type'])
                count = "[%d]" % int(matches.group(1))
            substruct = []
            substruct.append("  struct {")
            for sp in p['params']:
                substruct.append("%s%s;" % (" " * (padding + 2), format_c_type(sp['type'], sp['name'])))
            substruct.append("  } __packed %s%s;" % (p['name'], count))
            struct_members.append("\n".join(substruct))
        else:
            struct_members.append("%s%s;" % (" " * padding, format_c_type(p['type'], p['name'])))
    struct_members = "\n".join(struct_members)
    return struct_members


def process_message(code_format, messagedef, output_directory):
    total_size = get_param_total_size(messagedef['params'])
    struct_format = get_message_struct_format(messagedef['params'])

    output = []

    if code_format == "python":
        param_names = [p['name'] for p in messagedef['params']]
        ctor_args = ", ".join(["%s=0" % name for name in param_names])
        ctor_inits = "\n        ".join(["self.%s = %s" % (name, name) for name in param_names])

        unpack_inits = []
        pack_inits = []
        struct_classes = []
        param_index = 0
        for param in messagedef['params']:
            if param['type'].startswith('struct'):
                p_names = [p['name'] for p in param['params']]
                struct_name = "%sMessage%sParam" % (messagedef['name'], param['name'].title())

                struct_size = get_param_total_size(param['params'])
                struct_ctor_params = ", ".join(["%s=0" % pn for pn in p_names])
                struct_classes.append("class %sMessage%sParam(object):" % (messagedef['name'], param['name'].title()))
                struct_classes.append("    STRUCT_FORMAT = \"%s\"" % get_message_struct_format(param['params']))
                struct_classes.append("    STRUCT_SIZE = %d" % struct_size)
                struct_classes.append("    ")
                struct_classes.append("    def __init__(self, %s):" % struct_ctor_params)
                for pn in p_names:
                    struct_classes.append("        self.%s = %s" % (pn, pn))
                struct_classes.append("    ")
                struct_classes.append("    @classmethod")
                struct_classes.append("    def unpack(cls, data):")
                struct_classes.append("        data = struct.unpack(cls.STRUCT_FORMAT, data)")
                struct_classes.append("        obj = cls()")

                i = 0
                for p in param['params']:
                    struct_classes.append("        obj.%s = data[%d]" % (p['name'], i))
                    i += 1

                struct_classes.append("        ")
                struct_classes.append("    def pack(self):")
                struct_classes.append("        return struct.pack(self.STRUCT_FORMAT, %s)" % ", ".join(["self.%s" % pn for pn in p_names]))
                struct_classes.append("")

                if param['type'].index('[') > 0:
                    matches = re.search("struct\[([0-9]+)\]", param['type'])
                    count = int(matches.group(1))

                    unpack_inits.append("obj.%s = []" % param['name'])
                    unpack_inits.append("for i in range(%d):" % count)
                    unpack_inits.append("    obj.%s.append(cls.%s.unpack(data[%d + i]))" % (param['name'], struct_name, param_index))

                    pack_inits.append("for i in range(%d):" % count)
                    pack_inits.append("    try:")
                    pack_inits.append("        struct_data.append(self.%s[i].pack())" % param['name'])
                    pack_inits.append("    except IndexError:")
                    pack_inits.append("        struct_data.append(b'0' * self.%s.STRUCT_SIZE)" % struct_name)

                    param_index += count
                else:
                    unpack_inits.append("obj.%s = cls.%s.unpack(data[%d])" % (param['name'], struct_name, param_index))
                    pack_inits.append("struct_data.append(self.%s.pack())" % param['name'])
                    param_index += 1
            else:
                unpack_inits.append("obj.%s = data[%d]" % (param['name'], param_index))
                pack_inits.append("struct_data.append(self.%s)" % param['name'])
                param_index += 1

        unpack_inits = "\n        ".join(unpack_inits)
        pack_inits = "\n        ".join(pack_inits)
        struct_classes = "\n    ".join(struct_classes)

        MESSAGE_PY = MESSAGE_PY_TEMPLATE.format(**{
            "id": messagedef['id'],
            "name": messagedef['name'],
            "ctor_args": ctor_args,
            "ctor_inits": ctor_inits,
            "pack_inits": pack_inits,
            "unpack_inits": unpack_inits,
            "struct_classes": struct_classes,
            "total_size": total_size,
            "struct_format": struct_format
        })

        print("Generating %s..." % os.path.join(output_directory, "%s.py" % cc2us(messagedef['name'])))
        with open(os.path.join(output_directory, "%s.py" % cc2us(messagedef['name'])), "w") as fp:
            fp.write(MESSAGE_PY)

    elif code_format == "c":
        header_output = []
        source_output = []
        struct_members = process_struct_params(messagedef['params'], padding=2)

        header_output = HEADER_TEMPLATE % {
            "name": cc2us(messagedef['name']),
            "name_uc": cc2us(messagedef['name']).upper(),
            "struct_members": struct_members,
            "id": messagedef['id'],
            "size": total_size,
            "description": messagedef['description'],
            }

        source_output = SOURCE_TEMPLATE % {
            "name": cc2us(messagedef['name']),
            "name_uc": cc2us(messagedef['name']).upper(),
            "struct_members": struct_members,
            "id": messagedef['id'],
            "size": total_size,
            "description": messagedef['description'],
        }

        print("Generating %s..." % os.path.join(output_directory, "%s.h" % cc2us(messagedef['name'])))
        with open(os.path.join(output_directory, "%s.h" % cc2us(messagedef['name'])), "w") as header_fp:
            header_fp.write(header_output)
            header_fp.close()

        print("Generating %s..." % os.path.join(output_directory, "%s.c" % cc2us(messagedef['name'])))
        with open(os.path.join(output_directory, "%s.c" % cc2us(messagedef['name'])), "w") as source_fp:
            source_fp.write(source_output)
            source_fp.close()


def process_format_python(message_defs, output_directory):
    message_names = [message['name'] for message in message_defs['messages']]
    enum_names = [enum['name'] for enum in message_defs['enums']]

    print("Generating %s..." % os.path.join(output_directory, "__init__.py"))
    with open(os.path.join(output_directory, "__init__.py"), "w") as fp:
        fp.write("from .message import pack_message\n")
        fp.write("from .message import Message, MessageHeader\n")
        for name in message_names:
            fp.write("from .%s import %sMessage\n" % (cc2us(name).lower(), name))
        for name in enum_names:
            fp.write("from .message import %s\n" % name)
        fp.write("\n")

    header_size = 0
    header_inits = ""
    header_unpacks = ""
    header_packs = ""
    header_args = ""
    param_index = 2
    if 'header' in message_defs:
        if 'params' in message_defs['header']:
            header_inits = []
            header_unpacks = []
            header_packs = []
            header_args = []
            param_index = 2

            for param in message_defs['header']['params']:
                plain_type = param['type']
                try:
                    if plain_type.index('[') > 0:
                        plain_type = plain_type[0:plain_type.index('[')]
                except ValueError:
                    pass

                header_inits.append("        self.%s = %s" % (param['name'], param['name']))
                header_unpacks.append("        obj.%s = msg_data[%d]" % (param['name'], param_index))
                header_args.append("%s=%s" % (param['name'], TYPES[plain_type][3]))
                header_packs.append("self.%s" % param['name'])
                param_index += 1
            header_inits = "\n".join(header_inits)
            header_unpacks = "\n".join(header_unpacks)
            header_packs = ", " + ", ".join(header_packs)
            header_args = ", " + ", ".join(header_args)
            header_size  = 3 + get_param_total_size(message_defs['header']['params'])
            header_format = get_message_struct_format(message_defs['header']['params'])[1:]

    print("Generating %s..." % os.path.join(output_directory, "message.py"))
    with open(os.path.join(output_directory, "message.py"), "w") as fp:
        enum_output = []
        for enum in message_defs['enums']:
            enum_output.append("class %s(object):" % enum['name'])

            for (name, value) in enum['values']:
                enum_output.append("    %s = %d" % (name, value))
        fp.write(MESSAGE_INIT_TEMPLATE.format(
            enums="\n".join(enum_output),
            max_size_int=math.ceil(get_max_message_size(message_defs['messages']) / 4.0),
            max_size=get_max_message_size(message_defs['messages']),
            header_size=header_size,
            header_inits=header_inits,
            header_packs=header_packs,
            header_unpacks=header_unpacks,
            header_args=header_args,
            header_struct_format=header_format))

    for message in message_defs['messages']:
        process_message("python", message, output_directory)


def process_format_c(message_defs, output_directory):
    message_names = [message['name'] for message in message_defs['messages']]

    print("Generating %s..." % os.path.join(output_directory, "message.h"))
    with open(os.path.join(output_directory, "message.h"), "w") as fp:
        includes = []
        for name in message_names:
            includes.append("#include \"%s.h\"" % cc2us(name))
        includes.append("")

        enums = []
        for enum in message_defs['enums']:
            enums.append("enum %s {" % enum['name'])
            enum_options = []
            for (name, value) in enum['values']:
                enum_options.append("  %s = %d" % (name, value))
            enums.append(",\n".join(enum_options))
            enums.append("} __attribute__ ((packed));")
            enums.append("")

        params = ""
        params_size = 0
        if 'header' in message_defs:
            if 'params' in message_defs['header']:
                params = process_struct_params(message_defs['header']['params'], padding=4)
                params_size = get_param_total_size(message_defs['header']['params'])

        fp.write("\n")
        fp.write(MESSAGE_H_TEMPLATE % {
            "includes": "\n".join(includes),
            "max_size_int": math.ceil(get_max_message_size(message_defs['messages']) / 4.0),
            "max_size": get_max_message_size(message_defs['messages']),
            "enums": "\n".join(enums),
            "message_params": params,
            "message_header_size": 3 + params_size
        })

    for message in message_defs['messages']:
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
        for f in os.listdir(output_directory):
            if os.path.isfile(os.path.join(output_directory, f)):
                os.unlink(os.path.join(output_directory, f))

    with open(filename, 'r') as defp:
        message_defs = json.load(defp)

        if args.format == "c":
            process_format_c(message_defs, output_directory)
        elif args.format == "python":
            process_format_python(message_defs, output_directory)

    print("Finished")

if __name__ == "__main__":
    main()
