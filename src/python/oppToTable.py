import os
import xml.etree.ElementTree as ET
import pandas as pd
import argparse


class OperationParser:
    def __init__(self, directory="openasip/openasip/opset/base"):
        self.directory = directory
        self.operations = {}  # Dictionary to store operations from different .opp files

    def oppToTable(self, filepath):
        # Parse the XML file
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()

            operations = []

            # Loop through each operation node
            for operation in root.findall("operation"):
                # Extract basic operation information
                name = (
                    operation.find("name").text
                    if operation.find("name") is not None
                    else ""
                )
                description = (
                    operation.find("description").text
                    if operation.find("description") is not None
                    else ""
                )
                trigger_semantics = (
                    operation.find("trigger-semantics").text
                    if operation.find("trigger-semantics") is not None
                    else ""
                )
                inputs = (
                    operation.find("inputs").text
                    if operation.find("inputs") is not None
                    else ""
                )
                outputs = (
                    operation.find("outputs").text
                    if operation.find("outputs") is not None
                    else ""
                )
                reads_memory = (
                    True if operation.find("reads-memory") is not None else False
                )
                writes_memory = (
                    True if operation.find("writes-memory") is not None else False
                )
                has_side_effects = (
                    True if operation.find("side-effects") is not None else False
                )
                is_branch = True if operation.find("is-branch") is not None else False
                control_flow = (
                    True if operation.find("control-flow") is not None else False
                )
                is_call = True if operation.find("is-call") is not None else False

                # Get input operands information
                input_operands = []
                for i, operand in enumerate(operation.findall("in"), start=1):
                    mem_address = (
                        "yes" if operand.find("mem-address") is not None else "no"
                    )
                    mem_data = "yes" if operand.find("mem-data") is not None else "no"
                    can_swap = (
                        operand.find("can-swap/in").attrib.get("id")
                        if operand.find("can-swap/in") is not None
                        else ""
                    )
                    input_operands.append(
                        {
                            f"input_operand_{i}_id": operand.attrib.get("id", ""),
                            f"io_{i}_element_count": operand.attrib.get(
                                "element-count", ""
                            ),
                            f"io_{i}_element_width": operand.attrib.get(
                                "element-width", ""
                            ),
                            f"io_{i}_type": operand.attrib.get("type", ""),
                            f"io_{i}_mem_address": mem_address,
                            f"io_{i}_mem_data": mem_data,
                            f"io_{i}_can_swap": can_swap,
                        }
                    )

                # Get output operands information
                output_operands = []
                for i, operand in enumerate(operation.findall("out"), start=1):
                    mem_data = "yes" if operand.find("mem-data") is not None else "no"
                    output_operands.append(
                        {
                            f"output_operand_{i}_id": operand.attrib.get("id", ""),
                            f"oo_{i}_element_count": operand.attrib.get(
                                "element-count", ""
                            ),
                            f"oo_{i}_element_width": operand.attrib.get(
                                "element-width", ""
                            ),
                            f"oo_{i}_type": operand.attrib.get("type", ""),
                            f"oo_{i}_memory_data": operand.attrib.get(
                                "memory_data", ""
                            ),
                            f"oo_{i}_mem_data": mem_data,
                        }
                    )

                # Flatten the input and output operands into single dictionaries
                input_operands_flat = {
                    k: v for d in input_operands for k, v in d.items()
                }
                output_operands_flat = {
                    k: v for d in output_operands for k, v in d.items()
                }

                # Combine all data into a single operation dictionary
                operation_data = {
                    "name": name,
                    "description": description,
                    "trigger_semantics": trigger_semantics,
                    "inputs": inputs,
                    "outputs": outputs,
                    "reads_memory": reads_memory,
                    "writes_memory": writes_memory,
                    "has_side_effects": has_side_effects,
                    "is_branch": is_branch,
                    "control_flow": control_flow,
                    "is_call": is_call,
                }
                operation_data.update(input_operands_flat)
                operation_data.update(output_operands_flat)

                operations.append(operation_data)

            # Extract the filename (without extension)
            filename = os.path.splitext(os.path.basename(filepath))[0]
            self.operations[filename] = pd.DataFrame(
                operations
            )  # Store operations as a DataFrame

        except (FileNotFoundError, ET.ParseError) as e:
            print(f"Error parsing {filepath}: {e}")

    def load_operations(self):
        self.operations = {}  # Clear the operations data

        # Loop through all .opp files in the directory
        for filename in os.listdir(self.directory):
            if filename.endswith(".opp"):
                filepath = os.path.join(self.directory, filename)
                self.oppToTable(filepath)

    def filter_operations(
        self,
        min_inputs=0,
        max_inputs=3,
        min_outputs=0,
        max_outputs=1,
        element_widths=[1, 5, 8, 16, 32],
        no_control_flow=False,
        no_call=False,
        no_branch=False,
        is_element_count_1=False,
        no_side_effects=False,
        no_memory_reads=False,
        no_memory_writes=False,
        no_HalfFloatWord=False,
        no_FloatWord=False,
        no_RawData=False,
    ):
        filtered_operations = {}

        for filename, df_operations in self.operations.items():
            # Initialize mask to select all rows
            mask = pd.Series([True] * len(df_operations))

            # Filter based on inputs
            for i in range(1, max_inputs):
                col_name = f"io_{i}_type"
                if col_name in df_operations.columns:
                    if no_HalfFloatWord:
                        mask &= df_operations[col_name] != "HalfFloatWord"
                    if no_FloatWord:
                        mask &= df_operations[col_name] != "FloatWord"
                    if no_RawData:
                        mask &= df_operations[col_name] != "RawData"
                col_name_width = f"io_{i}_element_width"
                if col_name_width in df_operations.columns:
                    df_operations[col_name_width] = pd.to_numeric(df_operations[col_name_width], errors='coerce').fillna(-1).astype(int)
                    mask &= df_operations[col_name_width].isin(element_widths)

            # Filter based on outputs
            for i in range(1, max_outputs):
                col_name = f"oo_{i}_type"
                if col_name in df_operations.columns:
                    if no_HalfFloatWord:
                        mask &= df_operations[col_name] != "HalfFloatWord"
                    if no_FloatWord:
                        mask &= df_operations[col_name] != "FloatWord"
                    if no_RawData:
                        mask &= df_operations[col_name] != "RawData"

                col_name_width = f"oo_{i}_element_width"
                if col_name_width in df_operations.columns:
                    df_operations[col_name_width] = pd.to_numeric(df_operations[col_name_width], errors='coerce').fillna(-1).astype(int)
                    mask &= df_operations[col_name_width].isin(element_widths)

            # Additional filters
            mask &= df_operations["inputs"].fillna(0).astype(int) >= min_inputs
            mask &= df_operations["inputs"].fillna(0).astype(int) <= max_inputs
            mask &= df_operations["outputs"].fillna(0).astype(int) >= min_outputs
            mask &= df_operations["outputs"].fillna(0).astype(int) <= max_outputs

            if no_control_flow:
                mask &= ~df_operations["control_flow"]

            if no_call:
                mask &= ~df_operations["is_call"]

            if no_branch:
                mask &= ~df_operations["is_branch"]

            if is_element_count_1:
                for i in range(1, max_inputs):
                    col_name_count = f"io_{i}_element_count"
                    if col_name_count in df_operations.columns:
                        df_operations[col_name_count] = pd.to_numeric(df_operations[col_name_count], errors='coerce').fillna(0).astype(int)
                        mask &= df_operations[col_name_count] == 1

            if no_side_effects:
                mask &= ~df_operations["has_side_effects"]

            if no_memory_reads:
                mask &= ~df_operations["reads_memory"]

            if no_memory_writes:
                mask &= ~df_operations["writes_memory"]

            filtered_operations[filename] = df_operations[mask]

        return filtered_operations

    def save_to_excel(self, directory):
        for filename, df_operations in self.operations.items():
            output_filepath = os.path.join(directory, f"{filename}.xlsx")
            df_operations.to_excel(output_filepath, index=False)
            print(f"Saved {filename}.xlsx to {output_filepath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse and filter XML operation files."
    )
    parser.add_argument(
        "--directory",
        type=str,
        default="openasip/openasip/opset/base",
        help="Directory containing .opp files",
    )
    parser.add_argument(
        "--min-inputs", type=int, default=0, help="Minimum number of inputs"
    )
    parser.add_argument(
        "--max-inputs", type=int, default=3, help="Maximum number of inputs"
    )
    parser.add_argument(
        "--min-outputs", type=int, default=0, help="Minimum number of outputs"
    )
    parser.add_argument(
        "--max-outputs", type=int, default=1, help="Maximum number of outputs"
    )
    parser.add_argument(
        "--element-widths",
        type=int,
        nargs="+",
        default=[1, 5, 8, 16, 32],
        help="Allowed element widths",
    )
    parser.add_argument(
        "--no-control-flow",
        action="store_true",
        help="Exclude control flow operations",
    )
    parser.add_argument(
        "--no-call", action="store_true", help="Exclude call operations"
    )
    parser.add_argument(
        "--no-branch", action="store_true", help="Exclude branch operations"
    )
    parser.add_argument(
        "--is-element-count-1",
        action="store_true",
        help="Only include operations with element count 1",
    )
    parser.add_argument(
        "--no-side-effects",
        action="store_true",
        help="Exclude operations with side effects",
    )
    parser.add_argument(
        "--no-memory-reads",
        action="store_true",
        help="Exclude operations that read memory",
    )
    parser.add_argument(
        "--no-memory-writes",
        action="store_true",
        help="Exclude operations that write memory",
    )
    parser.add_argument(
        "--no-HalfFloatWord",
        action="store_true",
        help="Exclude operations with type HalfFloatWord",
    )
    parser.add_argument(
        "--no-FloatWord",
        action="store_true",
        help="Exclude operations with type FloatWord",
    )
    parser.add_argument(
        "--no-RawData",
        action="store_true",
        help="Exclude operations with type RawData",
    )
    parser.add_argument(
        "--skip-filters",
        action="store_true",
        help="Skip all filters and output all operations",
    )
    parser.add_argument(
        "--output-directory",
        type=str,
        default="./Operations",
        help="Directory to save filtered results",
    )

    args = parser.parse_args()

    operation_parser = OperationParser(directory=args.directory)
    operation_parser.load_operations()

    if args.skip_filters:
        filtered_operations = operation_parser.operations
    else:
        filtered_operations = operation_parser.filter_operations(
            min_inputs=args.min_inputs,
            max_inputs=args.max_inputs,
            min_outputs=args.min_outputs,
            max_outputs=args.max_outputs,
            element_widths=args.element_widths,
            no_control_flow=args.no_control_flow,
            no_call=args.no_call,
            no_branch=args.no_branch,
            is_element_count_1=args.is_element_count_1,
            no_side_effects=args.no_side_effects,
            no_memory_reads=args.no_memory_reads,
            no_memory_writes=args.no_memory_writes,
            no_HalfFloatWord=args.no_HalfFloatWord,
            no_FloatWord=args.no_FloatWord,
            no_RawData=args.no_RawData,
        )

    for filename, df_operations in filtered_operations.items():
        output_directory = args.output_directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        output_filepath = os.path.join(output_directory, f"{filename}.xlsx")
        df_operations.to_excel(output_filepath, index=False)
        print(f"Saved {filename}.xlsx to {output_filepath}")
