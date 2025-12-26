from dataclasses import dataclass
from typing import Literal

from clang import cindex
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import Section


@dataclass(frozen=True)
class Target:
    name: str
    provides: list[str]
    depends: list[str]


def init_targets(header_path: str, kernel_path: str) -> list[Target]:
    def struct_from_header(header_path: str, struct_name: str, clang_args=None):
        clang_args = clang_args or []
        cidx = cindex.Index.create()
        tu = cidx.parse(
            header_path,
            args=["-x", "c", "-std=gnu23", *clang_args],
            options=0,
        )

        if tu.cursor is None:
            return None

        struct = None
        for cur in tu.cursor.walk_preorder():
            if cur.kind == cindex.CursorKind.STRUCT_DECL and cur.is_definition():
                if cur.spelling != struct_name:
                    continue

                struct = cur

        if struct is None:
            return None

        fields = {}
        for child in struct.get_children():
            if child.kind == cindex.CursorKind.FIELD_DECL:
                fields[child.spelling] = {
                    "type": child.type.spelling,
                    "offset": child.get_field_offsetof(),
                    "size": child.type.get_size(),
                }

        return fields

    def vaddr_to_offset(elf: ELFFile, vaddr: int) -> int:
        for seg in elf.iter_segments():
            if seg.header.p_type != "PT_LOAD":
                continue

            p_vaddr = int(seg.header.p_vaddr)
            p_offset = int(seg.header.p_offset)
            p_filesz = int(seg.header.p_filesz)
            p_memsz = int(seg.header.p_memsz)

            if not (p_vaddr <= vaddr < p_vaddr + p_memsz):
                continue

            off = p_offset + (vaddr - p_vaddr)

            if off < p_offset or off >= p_offset + p_filesz:
                raise ValueError(f"vaddr 0x{vaddr:x} maps into zero-filled region (memsz>filesz) of a PT_LOAD segment")

            return off

        raise ValueError(f"vaddr 0x{vaddr:x} not covered by any PT_LOAD segment")

    def read_cstring_from_vaddr(elf: ELFFile, vaddr: int, encoding: str = "utf-8", errors: str = "strict", max_len: int = 1 << 20) -> str:
        off = vaddr_to_offset(elf, vaddr)
        elf.stream.seek(off)

        out = bytearray()
        while len(out) < max_len:
            b = elf.stream.read(1)
            if b == b"":
                raise EOFError(f"EOF while reading C-string at vaddr 0x{vaddr:x}")
            if b == b"\x00":
                return out.decode(encoding, errors=errors)
            out += b

        raise ValueError(f"C-string exceeds max_len={max_len} at vaddr 0x{vaddr:x}")

    def read_int_from_vaddr(elf: ELFFile, vaddr: int, size: int, signed: bool = False, byteorder: Literal["little", "big"] = "little"):
        off = vaddr_to_offset(elf, vaddr)
        elf.stream.seek(off)

        data = elf.stream.read(size)
        if len(data) != size:
            raise EOFError("unexpected EOF")

        return int.from_bytes(data, byteorder=byteorder, signed=signed)

    targets = []

    with open(kernel_path, "rb") as f:
        elf = ELFFile(f)

        init_targets_section = elf.get_section_by_name(".init_targets")
        if init_targets_section is None or not isinstance(init_targets_section, Section):
            raise Exception("Elf does not contain an `.init_targets` section")

        data = init_targets_section.data()

        fields = struct_from_header(header_path, "init_target", ["-std=gnu23"])
        if fields is None:
            raise Exception("Failed to parse `init_target` struct out of the init header")

        struct_size = 0
        for v in fields.values():
            struct_size += v["size"]

        for field in fields.items():
            if field[1]["offset"] % 8 != 0:
                raise Exception(f"Struct `init_target` contains a field `{field[0]}` with an invalid offset `{field[0]['offset']}")

        def get_field(fields, name):
            if name not in fields:
                raise Exception("Struct `init_target` does not contain the field `name`")

            return {
                "offset": fields[name]["offset"] // 8,
                "size": fields[name]["size"],
            }

        name_field = get_field(fields, "name")
        provides_field = get_field(fields, "provides")
        provides_count_field = get_field(fields, "provides_count")
        deps_field = get_field(fields, "dependencies")
        deps_count_field = get_field(fields, "dependency_count")

        ptr_size = name_field["size"]

        for i in range(0, len(data), struct_size):

            def read_field(field):
                return int.from_bytes(data[i + field["offset"] : i + field["offset"] + field["size"]], "little")

            name = read_cstring_from_vaddr(elf, read_field(name_field))

            provides_count = read_field(provides_count_field)
            provides = []
            for j in range(0, provides_count):
                provides.append(read_cstring_from_vaddr(elf, read_int_from_vaddr(elf, read_field(provides_field) + j * ptr_size, ptr_size)))

            deps_count = read_field(deps_count_field)
            deps = []
            for j in range(0, deps_count):
                deps.append(read_cstring_from_vaddr(elf, read_int_from_vaddr(elf, read_field(deps_field) + j * ptr_size, ptr_size)))

            targets.append(Target(name=name, provides=provides, depends=deps))

    return targets
