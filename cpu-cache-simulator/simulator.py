import argparse
import random
import util
from cache import Cache
from memory import Memory

replacement_policies = ["LRU", "LFU", "FIFO", "RAND"]
write_policies = ["WB", "WT"]

parser = argparse.ArgumentParser(description="Simulate the cache of a CPU.")

parser.add_argument("MEMORY", metavar="MEMORY", type=int,
                    help="Size of main memory in 2^N bytes")
parser.add_argument("CACHE", metavar="CACHE", type=int,
                    help="Size of the cache in 2^N bytes")
parser.add_argument("LINE", metavar="LINE", type=int,
                    help="Size of a line of memory in 2^N bytes")
parser.add_argument("MAPPING", metavar="MAPPING", type=int,
                    help="Mapping policy for cache in 2^N ways")
parser.add_argument("REPLACE", metavar="REPLACE", choices=replacement_policies,
                    help="Replacement policy for cache {"+", ".join(replacement_policies)+"}")
parser.add_argument("WRITE", metavar="WRITE", choices=write_policies,
                    help="Write policy for cache {"+", ".join(write_policies)+"}")

args = parser.parse_args()

mem_size = 2 ** args.MEMORY
cache_size = 2 ** args.CACHE
line_size = 2 ** args.LINE
mapping = 2 ** args.MAPPING

hits = 0
misses = 0

memory = Memory(mem_size, line_size)
cache = Cache(cache_size, mem_size, line_size,
              mapping)

mapping_str = "2^{0}-way associative".format(args.MAPPING)
print("\nMemory size: " + str(mem_size) +
      " bytes (" + str(mem_size // line_size) + " lines)")
print("Cache size: " + str(cache_size) +
      " bytes (" + str(cache_size // line_size) + " lines)")
print("Line size: " + str(line_size) + " bytes")
print("Mapping policy: " + ("direct" if mapping == 1 else mapping_str) + "\n")


def read(address, cache):
    """Read a byte from cache."""
    cache_line = cache.read(address)

    if cache_line:
        global hits
        hits += 1
    else:
        global misses
        misses += 1

    return cache_line[cache.get_offset(address)]

def write(address, data, cache):
    """Load a byte to cache."""
    line = [int(byte) for byte in reversed(data.to_bytes(line_size, 'big'))]
    cache.write(address, line)

command = None

while (command != "quit"):
    operation = input("> ")
    operation = operation.split()

    try:
        command = operation[0]
        params = operation[1:]

        if command == "read" and len(params) == 1:
            address = int(params[0])
            byte = read(address, cache)

            print("\nByte 0x" + util.hex_str(byte, 2) + " read from " +
                  util.bin_str(address, args.MEMORY) + "\n")

        elif command == "write" and len(params) == 2:
            address = int(params[0])
            data = int(params[1])

            write(address, data, cache)

            print("\nData 0x" + util.hex_str(data, 2) + " written to " +
                  util.bin_str(address, args.MEMORY) + "\n")

        elif command == "randread" and len(params) == 1:
            amount = int(params[0])

            for i in range(amount):
                address = random.randint(0, mem_size - 1)
                read(address, cache)

            print("\n" + str(amount) + " bytes read from memory\n")

        elif command == "randwrite" and len(params) == 1:
            amount = int(params[0])

            for i in range(amount):
                address = random.randint(0, mem_size - 1)
                byte = util.rand_byte()
                write(address, byte, cache)

            print("\n" + str(amount) + " bytes written to memory\n")

        elif command == "print" and len(params) == 2:
            start = int(params[0])
            amount = int(params[1])

            cache.print_section(start, amount)

        elif command == "print" and len(params) == 0:
            cache.print_section(0, len(cache._lines))

        elif command == "stats" and len(params) == 0:
            ratio = (hits / ((hits + misses) if misses else 1)) * 100

            print("\nHits: {0} | Misses: {1}".format(hits, misses))
            print("Hit/Miss Ratio: {0:.2f}%".format(ratio) + "\n")

        elif command != "quit":
            print("\nERROR: invalid command\n")

    except IndexError:
        print("\nERROR: out of bounds\n")