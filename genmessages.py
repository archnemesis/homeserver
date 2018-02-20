import argparse
import re
import json
import sys
import io


TYPES = {
    'uint32_t':     (4, 'I', 'I'),
    'int32_t':      (4, 'i', 'i'),
    'uint16_t':     (2, 'H', 'H'),
    'int16_t':      (2, 'h', 'h'),
    'float':        (4, 'f', 'f'),
    'double':       (8, 'd', 'd'),
    'char':         (1, 'c', 's'),
}


def process_message(messagedef, device):
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
    output.append("        return struct.pack(self.STRUCT_FORMAT, %s)" % ", ".join(["%s" % name for name in [p['name'] for p in messagedef['params']]]))
    output.append("")
    output.append("")

    device.write("\n".join(output))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="JSON file containing message definitions")
    parser.add_argument("--python", action="store_true", help="Generate Python message definitions")
    parser.add_argument("--c", action="store_true", help="Generate C message definitions")
    parser.add_argument("--output", default=None, help="Output (output to stdout if none given)")
    args = parser.parse_args()

    filename = args.filename
    outfile = io.StringIO()

    with open(filename, 'r') as defp:
        message_defs = json.load(defp)

        for message in message_defs:
            process_message(message, outfile)

    if args.output is not None:
        with open(args.output, 'w') as fp:
            fp.write(outfile.getvalue())
    else:
        print(outfile.getvalue())

    print("Finished")

if __name__ == "__main__":
    main()
