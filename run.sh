#!/bin/bash

echo "Shell Script Executing All Tests...."

# Execute the Python script lexer.py
python ./tokenizer.py

python ./parser.py

echo "Exited"
