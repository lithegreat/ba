import os
import xml.etree.ElementTree as ET
import pandas as pd

# Define the directory containing the .oop files
directory = 'openasip/openasip/opset/base'

# Loop through all files in the directory
for filename in os.listdir(directory):
    if filename.endswith('.opp'):
        filepath = os.path.join(directory, filename)

        # Parse the XML file
        tree = ET.parse(filepath)
        root = tree.getroot()

        operations = []

        # Loop through each operation node
        for operation in root.findall('operation'):
            name = operation.find('name').text if operation.find('name') is not None else ''
            description = operation.find('description').text if operation.find('description') is not None else ''
            inputs = operation.find('inputs').text if operation.find('inputs') is not None else ''
            outputs = operation.find('outputs').text if operation.find('outputs') is not None else ''
            reads_memory = True if operation.find('reads-memory') is not None else False
            writes_memory = True if operation.find('writes-memory') is not None else False
            # can_trap = True if operation.find('can-trap') is not None else False
            has_side_effects = True if operation.find('side-effects') is not None else False

            # Get input operands information
            input_operands = []
            for i, operand in enumerate(operation.findall('in'), start=1):
                mem_address = 'yes' if operand.find('mem-address') is not None else 'no'
                mem_data = 'yes' if operand.find('mem-data') is not None else 'no'
                can_swap = operand.find('can-swap/in').attrib.get('id') if operand.find('can-swap/in') is not None else ''
                input_operands.append({
                    f'input_operand_{i}_id': operand.attrib.get('id', ''),
                    f'input_operand_{i}_type': operand.attrib.get('type', ''),
                    f'input_operand_{i}_mem_address': mem_address,
                    f'input_operand_{i}_mem_data': mem_data,
                    f'input_operand_{i}_can_swap': can_swap
                })

            # Get output operands information
            output_operands = []
            for i, operand in enumerate(operation.findall('out'), start=1):
                mem_data = 'yes' if operand.find('mem-data') is not None else 'no'
                output_operands.append({
                    f'output_operand_{i}_id': operand.attrib.get('id', ''),
                    f'output_operand_{i}_type': operand.attrib.get('type', ''),
                    f'output_operand_{i}_memory_data': operand.attrib.get('memory_data', ''),
                    f'output_operand_{i}_mem_data': mem_data
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
                # 'can_trap': can_trap,
                'has_side_effects': has_side_effects
            }
            operation_data.update(input_operands_flat)
            operation_data.update(output_operands_flat)

            operations.append(operation_data)

        # Create DataFrame
        df_operations = pd.DataFrame(operations)

        # Display the entire table
        print(f"All Operations from {filename}:")
        print(df_operations)

        # Save the DataFrame to an Excel file
        output_filepath = os.path.join('/home/lithegreat/project/ba/output', f'{os.path.splitext(filename)[0]}.xlsx')
        df_operations.to_excel(output_filepath, index=False)

        print(f"Saved {output_filepath}")
