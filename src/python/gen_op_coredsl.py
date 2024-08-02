import pandas as pd
import os
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


def find_single_exec_operations(df):
    # Find operations with exactly one EXEC_OPERATION in trigger_semantics
    single_exec_operations = []
    for index, row in df.iterrows():
        if pd.notna(row["trigger_semantics"]):
            trigger_lines = row["trigger_semantics"].strip().splitlines()
            exec_operations = [
                line.strip()
                for line in trigger_lines
                if line.strip().startswith("EXEC_OPERATION")
            ]
            if len(exec_operations) == 1:
                single_exec_operations.append(row["name"])

    print("Single EXEC_OPERATION operations found:")
    print(single_exec_operations)  # Print the list of single EXEC_OPERATION operations found

    return single_exec_operations


def generate_instruction_set(
    input_filepath, output_directory, generate_single_exec_operations=False
):
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

        single_exec_operations = find_single_exec_operations(df)

        # Initialize func7_counter to generate unique func7 values
        func7_counter = 0

        for index, row in df.iterrows():
            operation_name = row["name"]

            # Check if generate_single_exec_operations is True and operation_name is NOT in single_exec_operations
            if generate_single_exec_operations and operation_name not in single_exec_operations:
                print(f"Skipping operation {operation_name} as it is not in single_exec_operations list")
                continue

            print(f"Generating code for operation {operation_name}")

            description = row["description"]

            # Write description as comment at the beginning of each operation
            if pd.notna(description):
                # Split description into lines and write each line as a comment
                description_lines = description.splitlines()
                for line in description_lines:
                    f.write(f"        // {line}\n")

            # Determine number of rd and rs based on inputs and outputs columns
            inputs = int(row["inputs"]) if pd.notna(row["inputs"]) else 0
            outputs = int(row["outputs"]) if pd.notna(row["outputs"]) else 0

            # Write operands section
            f.write(f"        OpenASIP_{filename}_{operation_name} " + "{\n")

            # Write encoding section
            f.write("            encoding: ")

            # Generate func7 for this operation
            func7 = f"7'b{func7_counter:07b}"
            func7_counter += 1

            # Example: 7'b0000000 :: rs2[4:0] :: rs1[4:0] :: 3'b000 :: rd[4:0] :: 7'b0001011
            encoding = f"{func7} :: {{name(rs2)}}[4:0] :: {{name(rs1)}}[4:0] :: 3'b000 :: {{name(rd)}}[4:0] :: 7'b0001011"
            f.write(f"{encoding};\n")

            # Write assembly section
            f.write("            assembly: \"")

            operands_list = []
            for i in range(outputs):
                operands_list.append(f"{{name(rd{i+1})}}")
            for i in range(inputs):
                operands_list.append(f"{{name(rs{i+1})}}")

            operands_str = ", ".join(operands_list)
            f.write(f"{operands_str}\";\n")  # Complete assembly format

            f.write("            behavior: {};\n")  # Empty behavior
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
    parser.add_argument(
        "--single_exec_operations",
        action="store_true",
        help="Generate only operations with single EXEC_OPERATION in trigger_semantics",
    )
    args = parser.parse_args()
    filename = args.filename
    input_filepath = f"Operations/{filename}.xlsx"
    output_directory = "Operations"

    generate_instruction_set(
        input_filepath, output_directory, args.single_exec_operations
    )
