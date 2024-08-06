from turtle import up
import pandas as pd
import os
import argparse
import re


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

    return single_exec_operations


def extract_trigger_code(filepath, operations):
    operation_codes = {}

    with open(filepath, "r") as file:
        content = file.read()

        for operation in operations:
            pattern = rf"OPERATION\({operation}\)(.*?)END_OPERATION\({operation}\)"
            match = re.search(pattern, content, re.DOTALL)

            if match:
                operation_code = match.group(1).strip()
                operation_codes[operation] = operation_code

    return operation_codes


def transform_trigger_code(trigger_code):
    transformed_code = ""

    # Replace UINT and ULONG with appropriate formats
    trigger_code = re.sub(r"UINT\((\d+)\)", r"X[rs\1 % RFS]", trigger_code)
    trigger_code = re.sub(r"ULONG\((\d+)\)", r"X[\1 % RFS]", trigger_code)

    # Replace SIntWord and UIntWord with signed<32> and unsigned<32> respectively
    trigger_code = re.sub(r"SIntWord", r"signed<32>", trigger_code)
    trigger_code = re.sub(r"UIntWord", r"unsigned<32>", trigger_code)

    # Replace MIN and OSAL_WORD_WIDTH with appropriate formats
    trigger_code = re.sub(r"MIN\(([^)]+)\)", r"min(\1)", trigger_code)
    trigger_code = re.sub(r"OSAL_WORD_WIDTH", r"32", trigger_code)

    # Replace other specific patterns
    trigger_code = re.sub(r"\(1\)", r"(rd % RFS)", trigger_code)
    trigger_code = re.sub(r"\(2\)", r"(X[rs1 % RFS] == X[rs2 % RFS])", trigger_code)
    trigger_code = re.sub(r"remainder\(([^)]+)\)", r"remainder(\1)", trigger_code)
    trigger_code = re.sub(r"static_cast<([^>]+)>\(([^)]+)\)", r"\1(\2)", trigger_code)
    trigger_code = re.sub(r"raise\(([^,]+), ([^)]+)\)", r"raise(\1, \2)", trigger_code)

    # Remove TRIGGER and END_TRIGGER; lines
    trigger_code = re.sub(r"END_TRIGGER;", r"", trigger_code)
    trigger_code = re.sub(r"TRIGGER", r"", trigger_code)

    # Replace IO(3) with X[rd % RFS]
    trigger_code = re.sub(r"IO\(3\)", r"X[rd % RFS]", trigger_code)

    # Change specific condition if (X[rs2 % RFS] == 0) to if (X[rs2 % RFS] != 0) and remove RUNTIME_ERROR
    trigger_code = re.sub(
        r'if\s*\(X\[rs2\s*%\s*RFS\]\s*==\s*0\)\s*RUNTIME_ERROR\("Divide by zero."\)',
        r"if (X[rs2 % RFS] != 0)",
        trigger_code,
    )

    # Add necessary indentation and formatting with 12 spaces
    lines = trigger_code.strip().splitlines()
    inside_if_block = False
    for line in lines:
        # Check for if statement and ensure it has correct indentation
        if line.startswith("if (X[rs2 % RFS] != 0)"):
            transformed_code += f"{' ' * 12}{line}\n"
            inside_if_block = True
        elif inside_if_block and (line.startswith("}") or line.startswith("else")):
            # Closing or else part of if block, reset indentation
            transformed_code += f"{' ' * 12}{line}\n"
            inside_if_block = False
        elif inside_if_block:
            # Inside if block, ensure indentation
            transformed_code += f"{' ' * 16}{line}\n"
        else:
            # Standard indentation for other lines
            transformed_code += f"{' ' * 12}{line}\n"

    return transformed_code


def find_based_operation(row, df):
    semantics = row["trigger_semantics"]
    if pd.notna(semantics):
        match = re.search(r"EXEC_OPERATION\((\w+), (.*?), (.*?), (.*?)\);", semantics)
        # print(f"Match: {match}")
        if match:
            based_operation = match.group(1)
            print(f"base_operation of {row['name']}: {based_operation.upper()}")
            return based_operation.upper()


def generate_behavior_code(operation_name, input_filepath, filename, row, df):
    operations = find_single_exec_operations(pd.read_excel(input_filepath))
    trigger_filepath = f"openasip/openasip/opset/base/{filename}.cc"
    trigger_code = extract_trigger_code(trigger_filepath, operations)
    behavior_code = transform_trigger_code(trigger_code.get(operation_name, ""))
    if not behavior_code:
        print(f"Trigger code not found for operation {operation_name}")
        based_operation = find_based_operation(row, df)
        behavior_code = transform_trigger_code(trigger_code.get(based_operation, ""))
        # swap rs1 and rs2
        temp_rs1 = "TEMP_RS1"
        behavior_code = behavior_code.replace("rs1", temp_rs1)
        behavior_code = behavior_code.replace("rs2", "rs1")
        behavior_code = behavior_code.replace(temp_rs1, "rs2")
    return behavior_code


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
            if (
                generate_single_exec_operations
                and operation_name not in single_exec_operations
            ):
                print(
                    f"Skipping operation {operation_name} as it is not in single_exec_operations list"
                )
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
            encoding = (
                f"{func7} :: rs2[4:0] :: rs1[4:0] :: 3'b000 :: rd[4:0] :: 7'b0001011"
            )
            f.write(f"{encoding};\n")

            # Write assembly section
            f.write('            assembly: "')

            operands_list = []
            for i in range(outputs):
                operands_list.append(f"{{name(rd{i+1})}}")
            for i in range(inputs):
                operands_list.append(f"{{name(rs{i+1})}}")

            operands_str = ", ".join(operands_list)
            f.write(f'{operands_str}";\n')  # Complete assembly format

            f.write("            behavior: {\n")

            # Extract trigger code for single EXEC_OPERATION operations
            if generate_single_exec_operations:
                behavior_code = generate_behavior_code(
                    operation_name, input_filepath, filename, row, df
                )
                f.write(f"    {behavior_code}")

            f.write("            }\n")
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
    output_directory = "src/CoreDSL"

    generate_instruction_set(
        input_filepath, output_directory, args.single_exec_operations
    )
