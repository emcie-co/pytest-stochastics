find . \( -name "*.py" -o -name "*.toml" -o -name "*.ini" \) -type f | sort | while read -r file; do
    echo -e "\n\n=== File: $file ===\n"
    cat "$file"
done > all_files_content.txt