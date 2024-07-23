import os
import xml.etree.ElementTree as ET
import pandas as pd
import argparse

class OperationParser:
    def __init__(self, directory='openasip/openasip/opset/base'):
        self.directory = directory
        self.operations = []

    def oppToTable(self, filepath):
        # Parse the XML file
        tree = ET.parse(filepath)
        root = tree.getroot()

        # Loop through each operation node
        for operation in root.findall('operation'):
            name = operation.find('name').text if operation.find('name') is not None else ''
            description = operation.find('description').text if operation.find('description') is not None else ''
            inputs = operation.find('inputs').text if operation.find('inputs') is not None else ''
            outputs = operation.find('outputs').text if operation.find('outputs') is not None else ''
            reads_memory = True if operation.find('reads-memory') is not None else False
            writes_memory = True if operation.find('writes-memory') is not None else False
            has_side_effects = True if operation.find('side-effects') is not None else False
            is_branch = True if operation.find('is-branch') is not None else False
            control_flow = True if operation.find('control-flow') is not None else False
            is_call = True if operation.find('is-call') is not None else False

            # Get input operands information
            input_operands = []
            for i, operand in enumerate(operation.findall('in'), start=1):
                mem_address = 'yes' if operand.find('mem-address') is not None else 'no'
                mem_data = 'yes' if operand.find('mem-data') is not None else 'no'
                can_swap = operand.find('can-swap/in').attrib.get('id') if operand.find('can-swap/in') is not None else ''
                input_operands.append({
                    f'input_operand_{i}_id': operand.attrib.get('id', ''),
                    f'io_{i}_element_count': operand.attrib.get('element-count', ''),
                    f'io_{i}_element_width': operand.attrib.get('element-width', ''),
                    f'io_{i}_type': operand.attrib.get('type', ''),
                    f'io_{i}_mem_address': mem_address,
                    f'io_{i}_mem_data': mem_data,
                    f'io_{i}_can_swap': can_swap
                })

            # Get output operands information
            output_operands = []
            for i, operand in enumerate(operation.findall('out'), start=1):
                mem_data = 'yes' if operand.find('mem-data') is not None else 'no'
                output_operands.append({
                    f'output_operand_{i}_id': operand.attrib.get('id', ''),
                    f'oo_{i}_element_count': operand.attrib.get('element-count', ''),
                    f'oo_{i}_element_width': operand.attrib.get('element-width', ''),
                    f'oo_{i}_type': operand.attrib.get('type', ''),
                    f'oo_{i}_memory_data': operand.attrib.get('memory_data', ''),
                    f'oo_{i}_mem_data': mem_data
                })

            # Flatten the input and output operands into single dictionaries
            input_operands_flat = {k: v for d in input_operands for k, v in d.items()}
            output_operands_flat = {k: v for d in output_operands for k, v in d.items()}

            # Combine all data
            operation_data = {
                'name': name,
                'description': description,
                'inputs': inputs,
                'outputs': outputs,
                'reads_memory': reads_memory,
                'writes_memory': writes_memory,
                'has_side_effects': has_side_effects,
                'is_branch': is_branch,
                'control_flow': control_flow,
                'is_call': is_call
            }
            operation_data.update(input_operands_flat)
            operation_data.update(output_operands_flat)

            self.operations.append(operation_data)

    def load_operations(self):
        self.operations = []

        # Loop through all .opp files in the directory
        for filename in os.listdir(self.directory):
            if filename.endswith('.opp'):
                filepath = os.path.join(self.directory, filename)
                self.oppToTable(filepath)

    def filter_operations(self, min_inputs=0, max_inputs=3, min_outputs=0, max_outputs=1,
                          min_element_width=0, max_element_width=32,
                          is_control_flow=False, is_call=False, is_branch=False,
                          is_element_count_1=False, no_side_effects=False,
                          no_memory_reads=False, no_memory_writes=False):
        df_operations = pd.DataFrame(self.operations)

        # Filter operations based on arguments
        mask = (
            (df_operations['inputs'] >= min_inputs) &
            (df_operations['inputs'] <= max_inputs) &
            (df_operations['outputs'] >= min_outputs) &
            (df_operations['outputs'] <= max_outputs) &
            (df_operations['io_1_element_width'].astype(int) >= min_element_width) &
            (df_operations['io_1_element_width'].astype(int) <= max_element_width)
        )

        if is_control_flow:
            mask &= df_operations['control_flow']

        if is_call:
            mask &= df_operations['is_call']

        if is_branch:
            mask &= df_operations['is_branch']

        if is_element_count_1:
            mask &= (df_operations['io_1_element_count'].astype(int) == 1)

        if no_side_effects:
            mask &= ~df_operations['has_side_effects']

        if no_memory_reads:
            mask &= ~df_operations['reads_memory']

        if no_memory_writes:
            mask &= ~df_operations['writes_memory']

        filtered_operations = df_operations[mask]

        return filtered_operations

    def save_to_excel(self, filepath):
        df_operations = pd.DataFrame(self.operations)
        df_operations.to_excel(filepath, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse and filter XML operation files.')
    parser.add_argument('--directory', type=str, default='openasip/openasip/opset/base', help='Directory containing .opp files')
    parser.add_argument('--min-inputs', type=int, default=0, help='Minimum number of inputs')
    parser.add_argument('--max-inputs', type=int, default=3, help='Maximum number of inputs')
    parser.add_argument('--min-outputs', type=int, default=0, help='Minimum number of outputs')
    parser.add_argument('--max-outputs', type=int, default=1, help='Maximum number of outputs')
    parser.add_argument('--min-element-width', type=int, default=0, help='Minimum element width')
    parser.add_argument('--max-element-width', type=int, default=32, help='Maximum element width')
    parser.add_argument('--is-control-flow', action='store_true', help='Only include control flow operations')
    parser.add_argument('--is-call', action='store_true', help='Only include call operations')
    parser.add_argument('--is-branch', action='store_true', help='Only include branch operations')
    parser.add_argument('--is-element-count-1', action='store_true', help='Only include operations with element count 1')
    parser.add_argument('--no-side-effects', action='store_true', help='Exclude operations with side effects')
    parser.add_argument('--no-memory-reads', action='store_true', help='Exclude operations that read memory')
    parser.add_argument('--no-memory-writes', action='store_true', help='Exclude operations that write memory')
    parser.add_argument('--skip-filters', action='store_true', help='Skip all filters and output all operations')

    args = parser.parse_args()

    operation_parser = OperationParser(directory=args.directory)
    operation_parser.load_operations()

    if args.skip_filters:
        filtered_operations = pd.DataFrame(operation_parser.operations)
    else:
        filtered_operations = operation_parser.filter_operations(
            min_inputs=args.min_inputs,
            max_inputs=args.max_inputs,
            min_outputs=args.min_outputs,
            max_outputs=args.max_outputs,
            min_element_width=args.min_element_width,
            max_element_width=args.max_element_width,
            is_control_flow=args.is_control_flow,
            is_call=args.is_call,
            is_branch=args.is_branch,
            is_element_count_1=args.is_element_count_1,
            no_side_effects=args.no_side_effects,
            no_memory_reads=args.no_memory_reads,
            no_memory_writes=args.no_memory_writes
        )

    print("Filtered Operations:")
    print(filtered_operations)

    # Save filtered operations to Excel file
    output_filepath = os.path.join('/home/lithegreat/project/ba/output', 'filtered_operations.xlsx')
    filtered_operations.to_excel(output_filepath, index=False)
    print(f"Saved filtered operations to {output_filepath}")