import os
import argparse
from oppToTable import OperationParser
from gen_op_coredsl import generate_instruction_set


def main():
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
        default=[1, 8, 16, 32],
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

    filename = args.filename
    input_filepath = (
        f"Operations/{filename}.xlsx"  # Replace with your input Excel file path
    )
    output_directory = "Operations"  # Replace with desired output directory

    generate_instruction_set(input_filepath, output_directory)


if __name__ == "__main__":
    main()
