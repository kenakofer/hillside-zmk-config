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

        layer_amps = layer_content.strip().split("&")
        pop = layer_amps.pop(0)
        # if pop != "":
        #     print("Pop is", pop)
        #     print("Layer is", layer_amps)
        #     assert pop == ""
        assert len(layer_amps) == 52

        cells = [["" for i in range(16)] for j in range(4)]

        skip_before = [6, 6, 18, 18, 31]
        break_before = [12, 24, 37]

        (x, y) = (0, 0)
        for i, c in enumerate(layer_amps):
            c = " ".join(c.split())
            while skip_before and i == skip_before[0]:
                skip_before.pop(0)
                x += 2
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

        # Replace original with formatted content
        start, end = match.span(1)
        new_content = (
            new_content[:start]
            + "\n"
            + "\n".join(formatted_lines)
            + "\n    "
            + new_content[end:]
        )

        print("Reformatted a layer")

    with open(input_file, "w") as f:
        f.write(new_content)
    print(f"Formatted '{input_file}'")


if __name__ == "__main__":
    main()
