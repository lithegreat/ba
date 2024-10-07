# Prompt the user to enter the model name
echo "Enter model name:"
read input_model

# Check if the directory exists, create it if it doesn't
if [ ! -d "results/$input_model" ]; then
    mkdir -p "results/$input_model"
    echo "Directory results/$input_model has been created."
else
    echo "Directory results/$input_model already exists, no need to recreate."
fi

# Execute the Python script with the user-provided model name
python3 -m mlonmcu.cli.main flow run "$input_model" --target etiss \
  -c mlif.toolchain=llvm \
  -c mlif.extend_attrs=1 \
  -c mlif.global_isel=1 \
  --progress \
  --post compare_rows -c compare_rows.to_compare="Total Cycles,Total ROM,Total RAM" \
  --parallel 4 \
  -c llvm.install_dir=/home/lithegreat/project/ba/build/seal5_llvm_openasip/.seal5/build/release \
  --config-gen _ \
  --config-gen etiss.attr=+xopenasipbase \
  -c etissvp.script=/home/lithegreat/project/ba/toolchain/etiss/build/bin/run_helper.sh \
  -f log_instrs -c log_instrs.to_file=1 \
  --post analyse_instructions \
  -c analyse_instructions.top=1000 \
  -c analyse_instructions.seq_depth=1 \
  --post filter_cols \
  -c filter_cols.drop="Platform,Total Cycles,Total CPI,ROM read-only,ROM code,ROM misc,RAM data,RAM zero-init data,Validation"

# Use the -f option to ensure files are overwritten
cp -f tmp/mlonmcu_env/temp/sessions/latest/report.csv "results/$input_model"
cp -f tmp/mlonmcu_env/temp/sessions/latest/runs/1/analyse_instructions_seq1.csv "results/$input_model"

echo "Files have been copied to path: results/$input_model"
