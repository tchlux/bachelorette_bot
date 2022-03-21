
import requests
url = "https://en.wikipedia.org/wiki/The_Bachelorette_(season_{number})"
first_season_number = 1
current_season_number = 17

# HTML element IDs for finding data tables on wiki pages.
season_table_ids = {
    1 : 'id="Elimination_Chart"',
    2 : 'id="Call-Out_Order"',
    None : 'id="Call-out_order"'
}

# Settings for processing legends out of HTML.
legend_color_start = '"background-color:'
legend_color_end = '; color:'
legend_entry_start = '</span>'
legend_entry_end = '</dd>'

# Settings for processing columns out of HTML.
col_start = "<td"
col_color_start = 'bgcolor="'
col_color_end = '"'
col_name_start = ">"
col_name_end = "<"
col_name_contains = set(['.', ' '] +
                        [chr(ord('a')+i) for i in range(26)] +
                        [chr(ord('A')+i) for i in range(26)] +
                        [chr(ord('0')+i) for i in range(10)]
)
col_name_split = "<br />"
col_end = "</td>"
col_citation_start = "<sup"


# Get legend entries and return them in a dictionary.
def parse_legend(legend_text):
    given_text = legend_text
    legend = []
    while (legend_color_start in legend_text):
        color_start = legend_text.index(legend_color_start) + len(legend_color_start)
        color_end = legend_text.index(legend_color_end)
        color, legend_text = (legend_text[color_start:color_end],
                              legend_text[color_end+len(legend_color_end):])
        entry_start = legend_text.index(legend_entry_start) + len(legend_entry_start)
        entry_end = legend_text.index(legend_entry_end)
        entry, legend_text = (legend_text[entry_start:entry_end],
                              legend_text[entry_end+len(legend_entry_end):])
        legend.append( (color.strip(), entry.strip().lower().replace(',','')) )
    legend = dict(legend)
    legend[None] = "none"
    return legend

# Make sure "Name" is free of any HTML.
def clean_name(name):
    # Initialize a list of possible names in this string based on content.
    if (col_name_start not in name):
        possible_names = [name.strip()]
    else:
        possible_names = [""]
    # Find all possible name substrings in this string.
    while (col_name_start in name):
        name = name[name.index(col_name_start)+len(col_name_start):]
        end = len(name)
        for end in range(len(name)+1):
            if (end == len(name)) or (name[end] not in col_name_contains):
                break
        possible_names.append( name[:end].strip() )
        name = name[end:]
    # Sort the possible names by length.
    possible_names.sort(key=lambda name: len(name))
    # Return the longest candidate name.
    return possible_names[-1]

# Given the text of a table, add data rows
def parse_table(table_text, legend):
    # Holder for output data.
    data = []

    # Get the table rows.
    rows = []
    while ("<tr>" in table_text):
        row_start = table_text.index("<tr>")
        row_end = table_text.index("</tr>")
        row, table_text = table_text[row_start+4:row_end], table_text[row_end+5:]
        rows.append( row.strip() )

    # Extract information about each contestant on each week from the table rows.
    for r,row_text in enumerate(rows):
        # Remove any spurious "center" blocks that might exist around the row contents.
        row_text = row_text.replace("<center>","")
        row_text = row_text.replace("</center>","")
        # Set up some key strings for parsing columns.
        col_number = -1
        # Get all of the columns out of the table row.
        while (col_start in row_text):
            col_number += 1
            start = row_text.index(col_start)+len(col_start)
            end = row_text.index(col_end)
            col, row_text = row_text[start:end], row_text[end+len(col_end):]
            # Get the color of this column, if it exists.
            if (col_color_start in col):
                start = col.index(col_color_start)+len(col_color_start)
                col = col[start:]
                end = col.index(col_color_end)
                color, col = col[:end], col[end+len(col_color_end):]
            else:
                color = None
            # Get the name(s) from this column.
            names = []
            if (col_name_split in col):
                for name in col.split(col_name_split):
                    names.append( clean_name(name) )
            else:
                names.append( clean_name(col) )
            # Store the information if there is a name (after cleaning).
            for name in names:
                if (len(name) > 0):
                    if (color not in legend):
                        print(f"WARNING: Could not find legend entry for color '{color}'\n"+
                              f"         Season {season_number}, column: {[col]}\n"+
                              f"         Legend: {legend}")
                    data.append( [name, col_number, legend.get(color,f"Unknown status ({color})")] )
    # Return all table data.
    return data


# If this file is executed directly (and *not* imported by other code).
if __name__ == "__main__":
    data = []
    # Iterate up to the current season.
    for season_number in range(first_season_number, current_season_number+1):

        # Get the HTML response from Wikipedia.
        response = requests.get(url.format(number=season_number))

        # Get the appropriate element ID based on the season.
        if (season_number in season_table_ids):
            check_id = season_table_ids[season_number]
        else:
            check_id = season_table_ids[None]

        # Print a status update.
        print()
        print("Season", season_number)
        print("", url.format(number=season_number))
        print("", check_id)

        # Sanity-check some assumptions about the raw HTML.
        count = response.text.count(check_id)
        if (count == 0):
            print(f"Did not find ID '{check_id}' for season {i}.")
            print()
            print(response.text)
            exit()
        elif (count > 1):
            print(f"Found {count} copies of ID '{check_id}' for season {i}.")
            print()
            print(response.text)
            exit()

        # Get the contents of the table that shows call-out-order.
        text = response.text # <- plain text response
        text = text.split(check_id)[1] # <- remove everything before "ID"
        print("text.count('<tbody>'): ",text.count("<tbody>"))
        if (season_number != 16):
            text = text.split("<tbody>")[1] # <- grab contents after next "<tbody>"
            text = text.split("</tbody>") # <- grab contents around next "</tbody>"
            table_text, legend_text = text[0], text[1] # <- table text is before, legend is after
        else:
            text1, text2 = text.split("<tbody>")[1:3]
            text1 = text1.split("</tbody>")[0]
            text2, legend_text = text2.split("</tbody>")[:2]
            table_text = text1

        # Get the legend information.
        legend = parse_legend(legend_text)


        # Add all of the table rows do the "data" list.
        table_data = parse_table(table_text, legend)
        for row in table_data:
            data.append( [season_number] + row )

        # Special case for season 16.
        if (season_number == 16):
            table_text = text2
            table_data = parse_table(table_text, legend)
            for row in table_data:
                data.append( [season_number + .5] + row )

    # Write the data to file.
    with open("bachelorette.csv", "w") as f:
        first_row = ["Season", "Name", "Column", "Label"]
        for row in [first_row] + data:
            row = ",".join(map(str, row))
            print(row, file=f)

