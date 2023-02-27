import random
import util
from math import log

class Line:

    """Class representing a line within a processor's main cache."""

    def __init__(self, size):
        self.use = 0
        self.modified = 0
        self.valid = 0
        self.tag = 0
        self.data = [0] * size

class Cache:

    """Class representing a processor's main cache."""

    def __init__(self, size, mem_size, line_size, way_number):
        self._lines = [Line(line_size) for i in range(size // line_size)]

        self._way_number = way_number  # Mapping policy

        self._size = size  # Cache size
        self._mem_size = mem_size  # Memory size
        self._line_size = line_size  # Block size

        # Bit offset of cache line tag
        self._tag_shift = int(log(self._size // self._way_number, 2))
        # Bit offset of cache line set
        self._set_shift = int(log(self._line_size, 2))

    def read(self, address):
        """Read a block of memory from the cache.

        :param int address: memory address for data to read from cache
        :return: block of memory read from the cache (None if cache miss)
        """
        tag = self._get_tag(address)  # Tag of cache line
        set = self._get_set(address)  # Set of cache lines
        line = None

        # Search for cache line within set
        for candidate in set:
            if candidate.tag == tag and candidate.valid:
                line = candidate
                break

        # Update use bits of cache line
        if line:
            self._update_use(line, set)

        return line.data if line else line

    def write(self, address, data):
        """Load a block of memory into the cache.

        :param int address: memory address for data to load to cache
        :param list data: block of memory to load into cache
        :return: tuple containing victim address and data (None if no victim)
        """
        tag = self._get_tag(address)  # Tag of cache line
        set = self._get_set(address)  # Set of cache lines
        victim = None

        # Select the victim
        victim = set[0]

        for index in range(len(set)):
            if set[index].use < victim.use:
                victim = set[index]

        victim.use = 0
        self._update_use(victim, set)

        # Replace victim
        victim.modified = 0
        victim.valid = 1
        victim.tag = tag
        victim.data = data

    def print_section(self, start, amount):
        """Print a section of the cache.

        :param int start: start address to print from
        :param int amount: amount of lines to print
        """
        line_len = len(str(self._size // self._line_size - 1))
        use_len = max([len(str(i.use)) for i in self._lines])
        tag_len = int(log(self._way_number * self._mem_size // self._size, 2))
        address_len = int(log(self._mem_size, 2))

        if start < 0 or (start + amount) > (self._size // self._line_size):
            raise IndexError

        print("\n" + " " * line_len + " " * use_len + " U M V T" +
              " " * tag_len + "<DATA @ ADDRESS>")

        for i in range(start, start + amount):
            print(util.dec_str(i, line_len) + ": " +
                  util.dec_str(self._lines[i].use, use_len) + " " +
                  util.bin_str(self._lines[i].modified, 1) + " " +
                  util.bin_str(self._lines[i].valid, 1) + " " +
                  util.bin_str(self._lines[i].tag, tag_len) + " <" +
                  " ".join([util.hex_str(i, 2) for i in self._lines[i].data]) + " @ " +
                  util.bin_str(self.get_physical_address(i), address_len) + ">")
        print()

    def get_physical_address(self, index):
        """Get the physical address of the cache line at index.

        :param int index: index of cache line to get physical address of
        :return: physical address of cache line
        """
        set_num = index // self._way_number

        return ((self._lines[index].tag << self._tag_shift) +
                (set_num << self._set_shift))

    def get_offset(self, address):
        """Get the offset from within a set from a physical address.

        :param int address: memory address to get offset from
        """
        return address & (self._line_size - 1)

    def _get_tag(self, address):
        """Get the cache line tag from a physical address.

        :param int address: memory address to get tag from
        """
        return address >> self._tag_shift

    def _get_set(self, address):
        """Get a set of cache lines from a physical address.

        :param int address: memory address to get set from
        """
        set_mask = (self._size // (self._line_size * self._way_number)) - 1
        set_num = (address >> self._set_shift) & set_mask
        index = set_num * self._way_number
        return self._lines[index:index + self._way_number]

    def _update_use(self, line, set):
        """Update the use bits of a cache line.

        :param line line: cache line to update use bits of
        """
        use = line.use

        if line.use < self._way_number:
            line.use = self._way_number
            for other in set:
                if other is not line and other.use > use:
                    other.use -= 1
