#!/usr/bin/env py
"""
Brainfuck Interpreter
=====================
 * Copyright 2025 yuran1811
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
"""

import os, re, pathlib
from argparse import ArgumentParser


class ArgParser:
    """
    Argument Parser for the Brainfuck Interpreter.

    Provides command-line options for:
      - Input file specification.
      - Tape output size control.
      - Dynamic I/O stream control.
      - Version info display.
    """

    def __init__(self, prog: str, desc: str) -> None:
        self.parser = ArgumentParser(prog=prog, description=desc)

    def with_input(self) -> None:
        self.parser.add_argument("-i", "--input", help="Input file", type=pathlib.Path)

    def with_tape_output(self) -> None:
        self.parser.add_argument(
            "-to", "--tape-output", help="Tape Output Size", type=int
        )

    def with_dynamic_iostream(self) -> None:
        self.parser.add_argument(
            "-d",
            "--dynamic-io",
            help="Dynamic I/O Stream with notation",
            action="store_const",
            const=1,
        )
        self.parser.add_argument(
            "-dc",
            "--dynamic-clean-io",
            help="Dynamic I/O Stream without notation",
            action="store_const",
            const=2,
        )

    def with_version(self) -> None:
        self.parser.add_argument(
            "-v", "--version", action="version", version="%(prog)s v1.0"
        )

    def parse_args(self):
        return self.parser.parse_args()


def brainfuck(code: str, use_dynamic_io=0, input_data="") -> tuple[str, list[int]]:
    """
    Brainfuck Interpreter Logic.

    Processes Brainfuck code and handles the operations on the tape.

    Parameters:
        code (str): The Brainfuck sanitized code to interpret.
        input_data (str): Input data for the Brainfuck program.

    Returns:
        tuple[str, list[int]]: Output string and the state of the memory tape.
    """
    CELL_SZ = 2**8 - 1
    TAPE_SZ = 30_000
    tape = [0] * TAPE_SZ
    loop_map: dict[int, int] = {}

    # Precompute loop positions
    loop_stk: list[int] = []
    for i, cmd in enumerate(code):
        if cmd == "[":
            loop_stk.append(i)
        elif cmd == "]":
            if not loop_stk:
                raise SyntaxError(f"Unmatched ']' at position {i}")
            start = loop_stk.pop()
            loop_map[start] = i
            loop_map[i] = start
    if loop_stk:
        raise SyntaxError(f"Unmatched '[' at position {loop_stk[-1]}")

    # Execute Brainfuck code
    p, i, inp_i = 0, 0, 0
    output = ""
    print(">>> Program is running...")
    while i < len(code):
        cmd = code[i]
        if cmd == ">":
            p = (p + 1) % TAPE_SZ
        elif cmd == "<":
            p = (p - 1) % TAPE_SZ
        elif cmd == "+":
            tape[p] = (tape[p] + 1) % CELL_SZ
        elif cmd == "-":
            tape[p] = (tape[p] - 1) % CELL_SZ
        elif cmd == ".":
            if use_dynamic_io:
                if use_dynamic_io == 1:
                    print(f"[o]: {chr(tape[p])}")
                else:
                    print(chr(tape[p]), end="")
            else:
                output += chr(tape[p])
        elif cmd == ",":
            if use_dynamic_io:
                __tmp_inp = input("[i]: " if use_dynamic_io == 1 else "").strip()
                tape[p] = ord(
                    bytes(__tmp_inp[0], "utf-8").decode("unicode_escape")
                    if __tmp_inp
                    else "\0"
                )
            else:
                tape[p] = ord(input_data[inp_i]) if inp_i < len(input_data) else 0
                inp_i += 1
        elif cmd == "[":
            if tape[p] == 0:
                i = loop_map[i]
        elif cmd == "]":
            if tape[p] != 0:
                i = loop_map[i]
        i += 1
    return output, tape


if __name__ == "__main__":
    parser = ArgParser(
        "Brainfuck Interpreter", "A simple Brainfuck interpreter written in Python"
    )
    parser.with_input()
    parser.with_dynamic_iostream()
    parser.with_tape_output()
    parser.with_version()

    args = parser.parse_args()

    if args.input:
        input_arg: pathlib.Path = args.input
        if not os.path.exists(input_arg):
            print(f"Error: File {input_arg} does not exist")
            exit()

        try:
            # Read and sanitize Brainfuck code
            with open(input_arg, "r") as f:
                code = re.sub(r"[^\>\<\+\-\.\,\[\]]*", "", f.read(), flags=re.MULTILINE)

            # Prepare for static input data
            use_dynamic_io, inp, inp_sz = (
                (args.dynamic_clean_io or 0) + (args.dynamic_io or 0),
                [],
                code.count(","),
            )
            if inp_sz and not use_dynamic_io:
                print(
                    f"Please fill {inp_sz} input entr{"ies" if inp_sz > 1  else "y"} (separate by ::):",
                    end=" ",
                )
                inp = input().strip().split("::")
                if len(inp) != inp_sz:
                    print("Error: Invalid input size")
                    exit()

                inp = [
                    ord(bytes(_[0], "utf-8").decode("unicode_escape") if _ else "\0")
                    for _ in inp
                ]

            # Run the Brainfuck interpreter
            outp, tape = brainfuck(code, use_dynamic_io, inp)

            # Display results
            if not use_dynamic_io:
                print(f">>> Output\n{outp}")
            if args.tape_output and args.tape_output > 0:
                print(f">>> Tape Snapshot: {tape[:2 ** args.tape_output]}")

        except KeyboardInterrupt:
            print("\nProcess interrupted by user.")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            exit()
