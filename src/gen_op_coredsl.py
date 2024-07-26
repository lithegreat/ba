import pandas as pd
import os
import math
import argparse


def log_width(width):
    # Calculate log base 2 of width
    return int(math.log2(width))


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
                f.write(f"        // {description}\n")

            # Calculate rd_width and rs1_width, handling NaN values
            if pd.notna(row["oo_1_element_width"]):
                oo_1_element_width = int(row["oo_1_element_width"])
                rd_width = int(log_width(oo_1_element_width))
            else:
                rd_width = 0  # Default value when oo_1_element_width is NaN or missing

            if pd.notna(row["io_1_element_width"]):
                io_1_element_width = int(row["io_1_element_width"])
                rs1_width = int(log_width(io_1_element_width))
            else:
                rs1_width = 0  # Default value when io_1_element_width is NaN or missing

            # Calculate rs2_width, handling NaN values and non-existence of io_2_element_width
            if "io_2_element_width" in row and pd.notna(row["io_2_element_width"]):
                io_2_element_width = int(row["io_2_element_width"])
                rs2_width = log_width(io_2_element_width)
            else:
                rs2_width = (
                    -1
                )  # Default value when io_2_element_width does not exist or is NaN

            f.write(f"        {operation_name} " + "{\n")
            f.write("            operands: {\n")
            f.write(
                f"                unsigned<{rd_width}> rd [[reg_type=u{oo_1_element_width}]] [[out]];\n"
            )
            f.write(
                f"                unsigned<{rs1_width}> rs1 [[reg_type=u{io_1_element_width}]] [[in]];\n"
            )
            if rs2_width != -1:
                f.write(
                    f"                unsigned<{rs2_width}> rs2 [[reg_type=u{io_2_element_width}]] [[in]];\n"
                )
            else:
                f.write("                // rs2 operand not specified in input\n")
            f.write("            }\n")
            f.write("            encoding: auto;\n")
            f.write(
                f'            assembly: {{"OpenASIP_{filename}.{operation_name}", "{{name(rd)}}, {{name(rs1)}}, {{name(rs2)}}"}};\n'
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
    input_filepath = f"Operations/OpenASIP_{filename}.xlsx"  # Replace with your input Excel file path
    output_directory = "Operations"  # Replace with desired output directory

    generate_instruction_set(input_filepath, output_directory)
