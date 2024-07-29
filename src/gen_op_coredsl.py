import pandas as pd
import os
import math
import argparse


def determine_reg_type(element_type):
    # Determine register type based on element type
    if isinstance(element_type, str):
        if "SIntWord" in element_type:
            return "s"
        elif "UIntWord" in element_type:
            return "u"
        else:
            return "u"  # Default to unsigned if type is not specified
    else:
        return "u"  # Default to unsigned if element_type is not a string or NaN


def generate_instruction_set(input_filepath, output_directory):
    # Extract file name without extension
    filename = os.path.splitext(os.path.basename(input_filepath))[0]

    # Load Excel file
    df = pd.read_excel(input_filepath)

    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    output_filepath = os.path.join(output_directory, f"{filename}.core_desc")

    with open(output_filepath, "w") as f:
        f.write("InstructionSet OpenASIP_{} extends RV32I {{\n".format(filename))
        f.write("    instructions {\n")

        for index, row in df.iterrows():
            operation_name = row["name"]
            description = row["description"]

            # Write description as comment at the beginning of each operation
            if pd.notna(description):
                # Split description into lines and write each line as a comment
                description_lines = description.splitlines()
                for line in description_lines:
                    f.write(f"        // {line}\n")

            # Calculate rd_width, rs1_width, rs2_width, rs3_width and handle NaN values
            oo_1_element_width = -1
            io_1_element_width = -1
            io_2_element_width = -1
            io_3_element_width = -1

            if pd.notna(row["oo_1_element_width"]):
                oo_1_element_width = int(row["oo_1_element_width"])

            if pd.notna(row["io_1_element_width"]):
                io_1_element_width = int(row["io_1_element_width"])

            if "io_2_element_width" in row and pd.notna(row["io_2_element_width"]):
                io_2_element_width = int(row["io_2_element_width"])

            if "io_3_element_width" in row and pd.notna(row["io_3_element_width"]):
                io_3_element_width = int(row["io_3_element_width"])

            f.write(f"        {operation_name} " + "{\n")
            f.write("            operands: {\n")

            if oo_1_element_width != -1:
                f.write(
                    f"                unsigned<5> rd [[reg_type={determine_reg_type(row['oo_1_type'])}{oo_1_element_width}]] [[out]];\n"
                )

            if io_1_element_width != -1:
                f.write(
                    f"                unsigned<5> rs1 [[reg_type={determine_reg_type(row['io_1_type'])}{io_1_element_width}]] [[in]];\n"
                )

            if io_2_element_width != -1:
                f.write(
                    f"                unsigned<5> rs2 [[reg_type={determine_reg_type(row['io_2_type'])}{io_2_element_width}]] [[in]];\n"
                )

            if io_3_element_width != -1:
                f.write(
                    f"                unsigned<5> rs3 [[reg_type={determine_reg_type(row['io_3_type'])}{io_3_element_width}]] [[in]];\n"
                )

            f.write("            }\n")
            f.write("            encoding: auto;\n")

            # Generate assembly line only if rd, rs1, rs2, or rs3 exist
            operands_list = []
            if oo_1_element_width != -1:
                operands_list.append("{name(rd)}")
            if io_1_element_width != -1:
                operands_list.append("{name(rs1)}")
            if io_2_element_width != -1:
                operands_list.append("{name(rs2)}")
            if io_3_element_width != -1:
                operands_list.append("{name(rs3)}")

            operands_str = ", ".join(operands_list)
            f.write(
                f'            assembly: {{"OpenASIP_{filename}.{operation_name}", "{operands_str}"}};\n'
            )

            f.write("            behavior: {};\n")
            f.write("        }\n")

        f.write("    }\n")
        f.write("}\n")

    print(f"Generated instruction set saved to {output_filepath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate instruction set from Excel file"
    )
    parser.add_argument(
        "--filename",
        type=str,
        default="base",
        help="Filename for the instruction set",
    )
    args = parser.parse_args()
    filename = args.filename
    input_filepath = (
        f"Operations/{filename}.xlsx"  # Replace with your input Excel file path
    )
    output_directory = "Operations"  # Replace with desired output directory

    generate_instruction_set(input_filepath, output_directory)
