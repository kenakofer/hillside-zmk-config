#!/usr/bin/env python3
import re


def parse_row(line):
    return ["&" + part.strip() for part in line.split("&") if part.strip()]


def get_widths(rows):
    widths = [0] * max(len(r) for r in rows)
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    return widths


def format_layer(layer_lines):
    # Extract pure key binding lines
    key_lines = [line.strip() for line in layer_lines if "&" in line]

    # Skip if it's not a standard 4-row layer
    if len(key_lines) != 4:
        return layer_lines

    rows = [parse_row(line) for line in key_lines]

    # Split alpha rows for separate formatting
    left_rows = [rows[i][:6] for i in range(3)]
    right_rows = [rows[i][6:] for i in range(3)]
    thumb_row = rows[3]

    left_widths = get_widths(left_rows)
    right_widths = get_widths(right_rows)
    thumb_widths = get_widths([thumb_row])

    formatted_lines = []
    for i in range(3):
        left = " ".join(
            left_rows[i][j].ljust(left_widths[j]) for j in range(len(left_rows[i]))
        )
        right = " ".join(
            right_rows[i][j].ljust(right_widths[j]) for j in range(len(right_rows[i]))
        )
        formatted_lines.append(f"        {left}    {right}")

    formatted_lines.append(
        "        "
        + " ".join(thumb_row[i].ljust(thumb_widths[i]) for i in range(len(thumb_row)))
    )

    # Re-integrate with comments and blank lines
    final_block = []
    key_line_idx = 0
    for line in layer_lines:
        if "&" in line:
            if key_line_idx < len(formatted_lines):
                final_block.append(formatted_lines[key_line_idx])
                key_line_idx += 1
        else:
            final_block.append(line)
    return final_block


def main():
    input_file = "config/hillside52.keymap"
    with open(input_file, "r") as f:
        content = f.read()

    # Find all layer bindings
    layer_regex = r"bindings = <([^>]+)>;\n\s*sensor-bindings"
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

        cells = ["" for i in range(14)] for j in
        range(4)]

        skip_before = [6, 6, 18, 18, 30]
        break_before = [12, 24, 37]

        (x,y) = (0,0)
        for (c, i) in enumerate(layer_amps):
            c = " ".join(c.split())
            while i == skip_before[0]:
                skip_before.pop(0)
                x += 1
            while i == break_before[0]:
                break_before.pop(0)
                y += 1
                x = 0
            cells[y][x] = c
            x += 1


        # layer_lines = layer_content.strip().split('\n')
        #
        # formatted_lines = format_layer(layer_lines)
        #
        # # Replace original with formatted content
        # start, end = match.span(1)
        # new_content = new_content[:start] + "\n" + "\n".join(formatted_lines) + "\n    " + new_content[end:]

    with open(input_file, "w") as f:
        f.write(new_content)
    print(f"Formatted '{input_file}'")


if __name__ == "__main__":
    main()
