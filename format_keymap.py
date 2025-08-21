#!/usr/bin/env python3
import re


def main():
    input_file = "config/hillside52.keymap"
    with open(input_file, "r") as f:
        content = f.read()

    # Find all layer bindings
    layer_regex = r"bindings = <([^>]+)>;\n\s*sensor-bindings"
    matches = re.finditer(layer_regex, content, re.DOTALL)

    # First Pass: Collect all cells to determine max width
    column_width = 0
    longest = []
    for match in matches:
        layer_content = match.group(1)
        layer_content = re.sub(r"^\s*//.*$", "", layer_content, flags=re.MULTILINE)

        layer_amps = layer_content.strip().split("&")
        pop = layer_amps.pop(0)
        assert len(layer_amps) == 52

        for amp in layer_amps:
            amp = " ".join(amp.split())
            if column_width < len(amp):
                column_width = len(amp)
                longest = [amp]
            elif column_width == len(amp):
                longest.append(amp)
    print("Longest entries:", longest)

    # Second Pass: Reformat layers
    matches = re.finditer(layer_regex, content, re.DOTALL)
    new_content = content
    for match in reversed(list(matches)):
        layer_content = match.group(1)
        layer_content = re.sub(r"^\s*//.*$", "", layer_content, flags=re.MULTILINE)

        layer_amps = layer_content.strip().split("&")
        pop = layer_amps.pop(0)
        # if pop != "":
        #     print("Pop is", pop)
        #     print("Layer is", layer_amps)
        #     assert pop == ""
        assert len(layer_amps) == 52

        cells = [["" for i in range(16)] for j in range(4)]

        skip_before = [6, 6, 6, 6, 18, 18, 18, 18, 31, 31, 41, 49]
        break_before = [12, 24, 38]

        (x, y) = (0, 0)
        for i, c in enumerate(layer_amps):
            c = " ".join(c.split())
            while skip_before and i == skip_before[0]:
                skip_before.pop(0)
                x += 1
            while break_before and i == break_before[0]:
                break_before.pop(0)
                y += 1
                x = 0
            cells[y][x] = c
            x += 1

        formatted_lines = []
        for y in range(4):
            line = ""
            for x in range(16):
                if cells[y][x] != "":
                    line += "&" + cells[y][x].ljust(column_width)
                else:
                    line += " " * (column_width + 1)
            formatted_lines.append(line.rstrip())

        # Add // comment lines with box drawing characters, including T characters
        comment_lines = ["//" + "─" * (column_width - 1) for _y in range(5)]
        comment_lines[0] += ""
        for x in range(5):
            comment_lines[0] += "┬" + "─" * (column_width)
        comment_lines[0] += "┐"
        comment_lines[0] += " " * (column_width * 4 + 3)
        # Second grouping, opposite of "┐"
        comment_lines[0] += "┌" + "─" * (column_width)
        for x in range(5):
            comment_lines[0] += "┬" + "─" * (column_width)
        comment_lines[0] += "┐"

        comment_lines[1] = (
            comment_lines[0].replace("┬", "┼").replace("┐", "┤").replace("┌", "├")
        )

        # Third comment line needs to accommodate the 6 above and 7 below
        comment_lines[2] = comment_lines[1]
        # comment_lines[4] = (
        #     comment_lines[0].replace("┬", "┴").replace("┐", "┘").replace("┌", "└")
        # )
        for x in range(15):
            comment_lines[4] += "┴" + "─" * (column_width)
        comment_lines[4] += "┘"

        comment_lines[3] = (
            comment_lines[4].replace("┴", "┼").replace("┘", "┤").replace("└", "├")
        )

        # Interleave the 5 comment lines with the 4 formatted lines
        interleaved_lines = []
        for y in range(4):
            interleaved_lines.append(comment_lines[y])
            interleaved_lines.append(formatted_lines[y])
        interleaved_lines.append(comment_lines[4])

        # Replace original with formatted content
        start, end = match.span(1)
        new_content = (
            new_content[:start]
            + "\n"
            + "\n".join(interleaved_lines)
            + "\n    "
            + new_content[end:]
        )

        print("Reformatted a layer")

    with open(input_file, "w") as f:
        f.write(new_content)
    print(f"Formatted '{input_file}'")


if __name__ == "__main__":
    main()
