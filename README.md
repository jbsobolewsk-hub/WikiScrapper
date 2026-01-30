# 📚 WikiScrapper - By Jakub Sobolewski, 469693

**WikiScrapper** is a Python project developed as part of the course:

> **Kurs Pythona (1000-213bPYT)**
>
>🔗 More course information:  
> https://usosweb.uw.edu.pl/kontroler.php?_action=katalog2%2Fprzedmioty%2FpokazPrzedmiot&kod=1000-213bPYT&lang=en

---

## 🧠 Project Overview

WikiScrapper is a Python-based tool designed to scrape and analyze
content from MediaWiki-powered websites.  
The project focuses on structured data extraction, text processing, and
extensible architecture.

It currently supports scraping wiki pages using HTML parsing and supports MediaWiki based sites.
Future development can extend support for other types of wiki.
All output from internet-using configurations of the scraping program comes from Bulbapedia wiki
at https://bulbapedia.bulbagarden.net

---

## 📂 Project File Structure

```bash

wikiscrapper/
├── analysis/
│   └── text_analysis.ipynb
├── config/
│   ├── __init__.py
│   ├── args_parser.py
│   └── run_modes.py
├── tests/
│   ├── __init__.py
│   ├── integration_test.py
│   └── unit_test.py
├── utils/
│   ├── __init__.py
│   ├── graphic_utils.py
│   ├── path_utils.py
│   └── text_utils.py
├── wiki/
│   ├── __init__.py
│   ├── bulbapedia.py
│   ├── client.py
│   └── factory.py
├── README.md
├── requirements.txt
├── file_tree.py
├── wikiscrapper.py
├── wikiscrapper_tests.py
└── word-counts.json
```
