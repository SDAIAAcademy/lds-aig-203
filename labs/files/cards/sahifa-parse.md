# sahifa-parse

A small Python library that extracts text and tables from PDF files, with right-to-left support.

- Licence: MIT (file `LICENSE` in the repository: "Copyright (c) 2025 The sahifa-parse authors")
- Maintainers: 3 volunteers; last release 2.4.1
- Dependencies: two other libraries, both under the BSD-3-Clause licence

## Use

```
from sahifa import read_pdf
pages = read_pdf("invoice.pdf")
```
