# Metaprog-lab-formatter
Code formatter for Java

---
    usage: main.py [-h] [--print] [--output OUTPUT] input properties
    
    Code formatter for Java.
    
    positional arguments:
      input            File to format.
      properties       Properties for formatter.
    
    optional arguments:
      -h, --help       show this help message and exit
      --print          Print to standard output.
      --output OUTPUT  Output file. If not specified, formatted file will be
                       written to the input file.
---
    usage: template_generator.py [-h] [--schema SCHEMA] output
    
    Code formatter for Java. Properties generation utility.
    
    positional arguments:
      output           Where to save generated properties.
    
    optional arguments:
      -h, --help       show this help message and exit
      --schema SCHEMA  File with description of properties. "schema.properties" by
                       default.
