# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Writes the synthetic case files of LDS-AIG-203 (Athl SME Finance Fund) into labs/files/.

Standard library only, fixed seed: the same bytes on every run. Everything is invented: the Fund,
its suppliers, the models, the people, the numbers. Real licence texts are not copied: the lab
links to their official pages. The package signature is made by sign_package.py, a separate step.

    cd labs
    uv run _tools/prepare_files.py
    uv run _tools/sign_package.py
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import random
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = ROOT / "files"
SEED = 203


def write(rel: str, text: str) -> None:
    path = FILES / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.strip("\n").encode("utf-8") + b"\n")


def write_csv(rel: str, header: list[str], rows: list[list], bom: bool = True) -> None:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    path = FILES / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + buf.getvalue().encode("utf-8"))


def safetensors(seed: int) -> bytes:
    """A tiny but valid safetensors file: two float32 tensors, deterministic values."""
    rng = random.Random(seed)
    w = [rng.uniform(-0.5, 0.5) for _ in range(16 * 8)]
    b = [rng.uniform(-0.1, 0.1) for _ in range(8)]
    data_w = struct.pack("<%df" % len(w), *w)
    data_b = struct.pack("<%df" % len(b), *b)
    header = {
        "__metadata__": {"format": "pt"},
        "head.bias": {"dtype": "F32", "shape": [8], "data_offsets": [0, len(data_b)]},
        "head.weight": {"dtype": "F32", "shape": [16, 8], "data_offsets": [len(data_b), len(data_b) + len(data_w)]},
    }
    h = json.dumps(header, separators=(",", ":")).encode("utf-8")
    h += b" " * ((8 - len(h) % 8) % 8)
    return struct.pack("<Q", len(h)) + h + data_b + data_w


# ---------------------------------------------------------------------------------------------
# Case brief
# ---------------------------------------------------------------------------------------------

CASE_BRIEF = """
# صندوق أَثْل لتمويل المنشآت الصغيرة والمتوسطة: موجز الحالة

> كل ما في هذه الحزمة اصطناعي: الصندوق والموردون والنماذج والأشخاص والأرقام.

صندوق أثل جهة تمويل تقرض المنشآت الصغيرة والمتوسطة في قطاعات التجزئة والتصنيع والخدمات والزراعة.
يستقبل نحو 1,800 طلب تمويل في الشهر، وفي كل طلب فواتير ممسوحة وقوائم مالية ومحادثات مع المقترض.
أنشأ الصندوق مكتبًا لحوكمة الذكاء الاصطناعي بعد أن وجد أن ما يشتريه أو ينزّله من مكونات لم يُراجَع ترخيصه ولا منشؤه.

## الأشخاص

| الاسم | الدور |
|---|---|
| ريم العكّاس | مديرة حوكمة الذكاء الاصطناعي، صاحبة طلب المراجعة |
| مهند السياري | مدير المشتريات والموردين |
| نوف الرويلي | مسؤولة حماية البيانات الشخصية |
| ثامر الكناني | رئيس نماذج مخاطر الائتمان، مالك نموذج القرار الائتماني |
| لولوة الحطّاب | قائدة تجربة العملاء، مالكة رسائل المقترضين |

## سجل الذكاء الاصطناعي من أطراف خارجية (مقتطف)

| المعرّف | المكوّن | النوع | الاستخدام في الصندوق |
|---|---|---|---|
| X-01 | Sutur-OCR-small | نموذج مفتوح الأوزان | قراءة الفواتير الممسوحة في طلبات التمويل |
| X-02 | Sarid-70B-Instruct | نموذج لغوي مفتوح الأوزان، يعمل على السحابة الخاصة للصندوق | تلخيص طلبات التمويل لمحللي الائتمان |
| X-03 | nuqta-pro لدى «نقطة السحابية» | نموذج مملوك مستضاف عبر واجهة برمجية | صياغة رسائل المقترضين والإجابة عن أسئلة الموظفين |
| X-04 | «مُتابِع» من «صَواب للخدمات الذكية» | خدمة وكلاء مستضافة | تذكير المقترضين بالأقساط والرد على أسئلتهم |
| X-05 | sahifa-parse | مكتبة برمجية | استخراج النص من ملفات PDF |
| X-06 | mustanad-mcp | خادم أدوات (Model Context Protocol) | ربط المساعد الداخلي بمخزن المستندات |
| X-07 | fawatir-scans | مجموعة بيانات | ضبط نموذج قراءة الفواتير مستقبلًا |
| I-01 | Athl-CDM v3 | نموذج قرار ائتماني بنته «ثبات للتحليلات» ويستضيفه الصندوق | توصية بالقبول أو الرفض لكل طلب |
"""

# ---------------------------------------------------------------------------------------------
# Lab 1.1: intake register, cards and the proprietary terms
# ---------------------------------------------------------------------------------------------

INTAKE = [
    ["X-01", "Sutur-OCR-small", "model weights", "sutur-lab (public model hub)", "read scanned invoices in loan applications", "apache-2.0", "https://www.apache.org/licenses/LICENSE-2.0", "sutur-ocr-small/README.md"],
    ["X-05", "sahifa-parse", "code library", "sahifa project (public code host)", "extract text from PDF files", "MIT", "https://opensource.org/license/mit", "cards/sahifa-parse.md"],
    ["X-06", "mustanad-mcp", "tool server", "mustanad project (public code host)", "connect the staff assistant to the document store; the Fund will add its own connector", "AGPL-3.0", "https://www.gnu.org/licenses/agpl-3.0.en.html", "cards/mustanad-mcp.md"],
    ["X-02", "Sarid-70B-Instruct", "model weights (fine-tuned)", "sarid-ai (public model hub)", "summarise loan applications for credit analysts, on the Fund's private cloud", "llama3.3", "https://www.llama.com/llama3_3/license/", "cards/sarid-70b-instruct.md"],
    ["X-07", "fawatir-scans", "dataset", "fawatir-open (public dataset hub)", "fine-tune the invoice reader next year", "see card", "https://creativecommons.org/licenses/by-nc/4.0/legalcode.en", "cards/fawatir-scans.md"],
    ["X-03", "Nuqta Cloud Model Service (nuqta-pro)", "hosted proprietary model", "Nuqta Cloud", "draft borrower letters; answer staff questions", "Nuqta Cloud Model Service Terms", "terms/nuqta_cloud_terms.md", "terms/nuqta_cloud_terms.md"],
]

SAHIFA = """
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
"""

MUSTANAD = """
# mustanad-mcp

A Model Context Protocol server that lets an AI assistant search and read documents in a document store.

- Licence: GNU Affero General Public License v3.0 (AGPL-3.0-only), file `LICENSE`
- The server ships connectors for two open-source document stores. Other stores need a connector you write.
- Typical deployment: the server runs inside your network; staff reach it through an assistant in their browser.

## Writing your own connector

Add a module under `connectors/` and register it in `server.py`. Connectors are part of the Program.
"""

SARID = """
---
license: llama3.3
base_model: meta-llama/Llama-3.3-70B-Instruct
language:
- ar
- en
pipeline_tag: text-generation
---

# Sarid-70B-Instruct

Sarid is an Arabic-first instruction model, fine-tuned by sarid-ai on 1.2 million Arabic
instruction pairs to summarise business documents.

**Free for commercial use.** Download the weights and run them anywhere.

## Training

- Base: Llama 3.3 70B Instruct
- Fine-tuning data: Arabic instruction pairs built by sarid-ai (not released)

## Files

`model-0000x-of-00030.safetensors`, `tokenizer.json`, `config.json`, `LICENSE` (the Llama 3.3 Community License Agreement)
"""

FAWATIR = """
---
license: cc-by-4.0
task_categories:
- image-to-text
language:
- ar
size_categories:
- 10K<n<100K
---

# fawatir-scans

38,400 scanned Arabic invoices and receipts with line-level transcriptions, for training invoice readers.

## Licence

This dataset is released under the **Creative Commons Attribution-NonCommercial 4.0 International**
licence (CC BY-NC 4.0). Please cite the dataset if you use it.

## How the data was collected

Images were collected from invoices and receipts that people posted publicly on social media and
online marketplaces between 2021 and 2024. Names and phone numbers printed on invoices were not removed.

## Citation

fawatir-open contributors, fawatir-scans, version 1.0.
"""

NUQTA_TERMS = """
# Nuqta Cloud Model Service Terms

Version 4.2. Fictional terms written for the SDAIA Academy course LDS-AIG-203. Not the terms of any real provider.

## 1. Definitions

1.1 "Service" means Nuqta Cloud's hosted model service, reached through its API, and the models offered through it.
1.2 "Customer Content" means inputs the Customer sends to the Service and outputs the Service returns.
1.3 "Model Version" means a dated model identifier such as `nuqta-pro-2`. An "Alias" is an identifier such as `nuqta-pro-latest` that points to a Model Version chosen by Nuqta Cloud.

## 2. Access

2.1 Nuqta Cloud grants the Customer a non-exclusive, non-transferable right to use the Service during the subscription term for the Customer's internal business purposes and for products the Customer offers to its own clients.
2.2 No right to the model weights, parameters or source code is granted.

## 3. Restrictions

3.1 The Customer must not resell, sublicense or provide the Service to third parties as a standalone model service.
3.2 The Customer must not use outputs to develop models that compete with the Service.
3.3 No attribution to Nuqta Cloud is required. The Customer must not state or imply that Nuqta Cloud endorses its products.

## 4. Acceptable use

4.1 The Customer must not use the Service: (a) for unlawful surveillance; (b) to make decisions that produce legal or similarly significant effects on individuals, such as credit, employment or housing decisions, without meaningful human review; (c) to generate content that impersonates a real person without consent.

## 5. Customer Content

5.1 The Customer owns Customer Content.
5.2 Unless the Customer is on the Enterprise plan with Data Controls switched on, Nuqta Cloud may use Customer Content to improve and train the Service.
5.3 Nuqta Cloud keeps request logs, including Customer Content, for 30 days for abuse monitoring, on every plan.

## 6. Data location

6.1 Customer Content may be processed in any region where Nuqta Cloud or its sub-processors operate.
6.2 Enterprise customers may select a storage region. When capacity in that region is constrained, inference may be routed to another region.

## 7. Model lifecycle

7.1 Nuqta Cloud may update the Model Version an Alias points to at any time, without notice.
7.2 Nuqta Cloud may deprecate a Model Version. A deprecated Model Version keeps working until its retirement date.
7.3 Nuqta Cloud gives at least 21 days' notice of a retirement date, by email to the account administrator.
7.4 After the retirement date, requests to that Model Version fail.

## 8. Suspension and termination

8.1 Either party may terminate for convenience with 30 days' notice.
8.2 Nuqta Cloud may suspend the Service immediately for a breach of section 4.

## 9. Data export and deletion

9.1 For 14 days after termination the Customer may export its stored Customer Content in Nuqta Cloud's JSONL format.
9.2 Nuqta Cloud deletes Customer Content within 30 days after termination, and from backups within 90 days. No certificate of deletion is issued.

## 10. Changes to these terms

10.1 Nuqta Cloud may change these terms by posting a new version. Continued use after 15 days means acceptance.

## 11. Sub-processors

11.1 The current list of sub-processors is on Nuqta Cloud's website. Nuqta Cloud gives 10 days' notice of a new sub-processor.
"""

LICENCE_TABLE_HEAD = ["id", "artefact", "licence or terms", "commercial use", "redistribution", "attribution", "prohibited or restricted uses", "clauses relied on", "card or text conflict", "decision for the Fund", "condition or question"]

# ---------------------------------------------------------------------------------------------
# Lab 1.2: the model package, its mirror copy, the template
# ---------------------------------------------------------------------------------------------

SUTUR_README = """
---
license: apache-2.0
base_model: naqsh-ai/vision-encoder-base
datasets:
- fawatir-scans
- sutur-internal-receipts
pipeline_tag: image-to-text
model_version: 1.1
publisher: sutur-lab
---

# Sutur-OCR-small

A small model that reads printed Arabic and English text in scanned invoices and receipts.

## Intended use

Reading invoices, receipts and stamped forms in back-office workflows. Not for handwriting.

## Training data

- fawatir-scans (public dataset hub)
- sutur-internal-receipts: receipts collected by sutur-lab (not released)

## Evaluation

Character error rate 3.1% on a held-out split of our data.

## Limitations

Low-resolution scans (below 150 dpi) and stamps over text reduce accuracy.

## Licence

Apache License 2.0. See `LICENSE`.
"""

SUTUR_LICENSE = """
Copyright 2026 sutur-lab

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

SUTUR_CONFIG = {"architecture": "SuturOCRSmall", "hidden_size": 16, "num_labels": 8, "image_size": 384, "torch_dtype": "float32"}
SUTUR_TOKENIZER = {"version": "1.0", "model": {"type": "WordLevel", "vocab": {"[PAD]": 0, "[UNK]": 1, "ف": 2, "ا": 3, "ت": 4, "و": 5, "ر": 6, "ة": 7}}}

MIRROR_LOADER = '''# custom_loader.py
# Shipped by the mirror uploader. A model card that asks you to run a loader like this one
# ("trust_remote_code") asks you to run the uploader's code on your machine.
# This copy is harmless on purpose: it only prints a line.
print("custom loader: nothing to do")
'''

PROV_TEMPLATE = """
# سجل منشأ: Sutur-OCR-small

| الحقل | ما وجدته | المصدر (ملف أو أمر) | تحققت منه أم معلن فقط |
|---|---|---|---|
| الناشر | | | |
| الإصدار المستخدم | | | |
| النموذج الأساسي | | | |
| البيانات المعلنة | | | |
| تاريخ الإصدارات | | | |
| بصمة ملف الأوزان | | | |
| التوقيع على الحزمة الرسمية | | | |
| التوقيع على النسخة الثانية | | | |
| الترخيص المعلن | | | |

## الأسئلة المفتوحة

1.
2.
3.

## التوصية

يُستخدم / يُستخدم بشرط / يُعلَّق، والسبب في جملة:
"""

# ---------------------------------------------------------------------------------------------
# Lab 1.3: Sawab's response pack for the Mutabi' service
# ---------------------------------------------------------------------------------------------

SAWAB_INDEX = """
# حزمة ردود «صَواب للخدمات الذكية»: خدمة «مُتابِع»

أرسلها مدير حسابات «صواب» إلى مهند السياري في فبراير 2027 ردًا على طلب الصندوق. ترقيم الأدلة من المورِّد.

| الدليل | الملف | ما يقول المورِّد إنه يثبته |
|---|---|---|
| E1 | `questionnaire.csv` | ضوابط الخدمة كلها |
| E2 | `cert_iso42001.md` | «خدماتنا للذكاء الاصطناعي معتمدة وفق ISO/IEC 42001» |
| E3 | `cert_iso27001.md` | أمن المعلومات في الاستضافة والتشغيل |
| E4 | `evaluation_summary.md` | جودة «مُتابِع» ودقته |
| E5 | `pentest_letter.md` | أمن الخدمة من الاختبار الخارجي |
| E6 | `subprocessors.csv` | من يعالج البيانات معنا |
| E7 | جواب السؤال Q12 في الاستبانة | اعتماد مقدمي خدمات الذكاء الاصطناعي على منصة حوكمة البيانات الوطنية |
"""

SAWAB_SERVICE = """
# «مُتابِع»: وصف الخدمة

«مُتابِع» خدمة وكلاء مستضافة تقدمها شركة صَواب للخدمات الذكية. يتصل الوكيل بنظام القروض لدى العميل
عبر واجهة برمجية، ويرسل للمقترضين تذكيرات الأقساط برسائل نصية وعبر تطبيقات المحادثة، ويجيب عن أسئلتهم
عن الرصيد والموعد، ويحوّل الحالات الصعبة إلى موظف.

- البيانات التي يعالجها: اسم المقترض، ورقم جواله، والرصيد المستحق، وتاريخ القسط، ونطاق درجة الائتمان، ونص المحادثة.
- النموذج اللغوي: نموذج مستضاف لدى مزوّد خارجي (انظر قائمة الأطراف من الباطن).
- الاستضافة: منصة «صواب» في مركز بيانات بالرياض.
- منتجات «صواب» الأخرى: «DocSense» لتصنيف المستندات، وبوابة العملاء.
"""

QUESTIONNAIRE = [
    ["Q01", "الحوكمة", "هل لديكم سياسة معتمدة لحوكمة الذكاء الاصطناعي ومسؤول عنها؟", "نعم، معتمدة من الإدارة العليا", "E2"],
    ["Q02", "الحوكمة", "هل تُجرون تقييمًا للمخاطر قبل إطلاق أي تغيير في الخدمة؟", "نعم", ""],
    ["Q03", "البيانات", "هل تُستخدم بيانات العميل في تدريب النماذج أو تحسينها؟", "لا نستخدمها نحن في التدريب", ""],
    ["Q04", "البيانات", "أين تُخزَّن بيانات العميل وأين تُعالَج؟", "تُخزَّن في الرياض", "E3"],
    ["Q05", "الأطراف من الباطن", "اذكروا كل طرف من الباطن يعالج بيانات العميل وموقعه", "انظر القائمة المرفقة", "E6"],
    ["Q06", "التغيير", "كيف تُبلغون العميل بتغيير النموذج الذي تعتمد عليه الخدمة؟", "نحدّث النموذج باستمرار لتحسين الجودة، ونعلن التحسينات الكبرى في نشرتنا الشهرية", ""],
    ["Q07", "التقييم", "ما نتائج تقييم الخدمة، ومن أجراه، وعلى أي بيانات؟", "انظر ملخص التقييم", "E4"],
    ["Q08", "الإشراف البشري", "متى يحوّل الوكيل المحادثة إلى موظف؟", "عند طلب المقترض، أو عند ثلاث محاولات فاشلة، أو عند ذكر نزاع أو شكوى", ""],
    ["Q09", "السجلات", "هل تُحفظ سجلات المحادثات والقرارات، وكم مدة حفظها، وهل يطلع عليها العميل؟", "نعم، 90 يومًا", ""],
    ["Q10", "الحوادث", "خلال كم من الوقت تُبلغون العميل بحادثة أمنية أو حادثة تمس بياناته؟", "في أقرب وقت ممكن", ""],
    ["Q11", "الاختبار الأمني", "متى أُجري آخر اختبار اختراق خارجي، وما نطاقه؟", "أُجري اختبار خارجي من شركة مستقلة", "E5"],
    ["Q12", "الاعتماد", "هل الخدمة معتمدة أو مسجلة لدى جهة وطنية؟", "نعم، «صواب» معتمدة مقدمَ خدمات ذكاء اصطناعي على منصة حوكمة البيانات الوطنية", ""],
    ["Q13", "الشهادات", "اذكروا شهادات أنظمة الإدارة ونطاق كل منها", "ISO/IEC 42001 وISO/IEC 27001", "E2, E3"],
    ["Q14", "الخروج", "كيف تُعاد بيانات العميل عند انتهاء العقد، وكيف تُمحى؟", "تُمحى خلال 60 يومًا من انتهاء العقد", ""],
]

CERT_42001 = """
# Certificate of registration (copy supplied by Sawab)

Itqan Assurance Ltd certifies that the management system of

**Sawab AI Services**, Riyadh

has been assessed and found to conform to **ISO/IEC 42001:2023**, Information technology, Artificial intelligence, Management system.

**Scope of certification:** design, development and operation of the Sawab DocSense document classification platform, including model training and monitoring for DocSense.

Certificate number: ITQ-AIMS-0417
Initial certification: 15 May 2026
Valid until: 14 May 2029, subject to annual surveillance audits
Site: Sawab AI Services head office, Riyadh

Accreditation: not stated on this certificate.

Itqan Assurance Ltd is a fictional certification body, invented for this course.
"""

CERT_27001 = """
# Certificate of registration (copy supplied by Sawab)

Northbridge Certification certifies that the information security management system of

**Sawab AI Services**, Riyadh

conforms to **ISO/IEC 27001:2022**.

**Scope of certification:** the information security management system for the hosting, operation and support of all Sawab cloud services delivered from the Sawab Riyadh data centre, in accordance with the Statement of Applicability version 3.

Certificate number: NB-27K-22981
Initial certification: 2 February 2025
Valid until: 1 February 2028, subject to annual surveillance audits

Accredited by: Northbridge Accreditation Service, accreditation number NAS-CB-114

Northbridge Certification and Northbridge Accreditation Service are fictional bodies, invented for this course.
"""

EVAL_SUMMARY = """
# ملخص تقييم «مُتابِع» (من «صواب»)

أجرى فريق منتج «مُتابِع» في «صواب» التقييم في الربع الثاني من 2026.

- مجموعة الاختبار: 200 محادثة من عملاء «صواب» الحاليين، اختارها الفريق نفسه.
- المقياس: «نجاح المهمة»، أي أن المقترض حصل على الجواب الصحيح أو حُوّل إلى موظف.
- النتيجة: نجاح المهمة 94%.
- الحكم على كل محادثة: مراجع من فريق المنتج.
- لم تُنشر مجموعة الاختبار، ولا النتائج حسب اللهجة أو نوع السؤال.
- النموذج اللغوي المستخدم وقت التقييم: «أحدث إصدار متاح».
"""

PENTEST = """
# خطاب ملخص اختبار الاختراق

إلى من يهمه الأمر،

أجرت شركة «حِصن للاختبارات الأمنية» (جهة افتراضية) اختبار اختراق لبوابة عملاء «صواب» على الإنترنت
بين 3 و14 أغسطس 2025. لم تُكتشف ثغرات حرجة، وأُغلقت الثغرتان المتوسطتان المكتشفتان.

نطاق الاختبار: بوابة العملاء على الويب. خارج النطاق: الواجهات البرمجية للخدمات، وخدمة «مُتابِع».

هذا الخطاب ملخص، والتقرير الكامل متاح للعملاء بعد توقيع اتفاقية عدم إفصاح.
"""

SUBPROCESSORS = [
    ["Nuqta Cloud", "استدعاء النموذج اللغوي (نص المحادثة، اسم المقترض، الرصيد)", "eu-central (خارج المملكة)، ومنطقة احتياطية حسب السعة", "منذ 2025"],
    ["Rasil SMS (جهة افتراضية)", "إرسال الرسائل النصية (رقم الجوال، نص الرسالة)", "الرياض", "منذ 2024"],
    ["Sawab Riyadh data centre", "التخزين والتشغيل", "الرياض", "منذ 2023"],
]

MEMO_TEMPLATE = """
# مذكرة مراجعة ضمان المورِّد: «مُتابِع» من «صواب»

إلى: مهند السياري، ريم العكّاس
من:
الموضوع: مراجعة حزمة ردود «صواب» قبل التعاقد

## 1. تقدير الأدلة

| الدليل | ما يثبته فعلًا | الصلة بخدمة «مُتابِع» (عالية / متوسطة / ضعيفة) | الكفاية (كافٍ / جزئي / غير كافٍ) | السبب |
|---|---|---|---|---|
| E1 | | | | |
| E2 | | | | |
| E3 | | | | |
| E4 | | | | |
| E5 | | | | |
| E6 | | | | |
| E7 | | | | |

## 2. الفجوات

## 3. ما نطلبه قبل التوقيع

## 4. ما نطلبه بعد التوقيع، ومتى
"""

# ---------------------------------------------------------------------------------------------
# Lab 2.1: deprecation notice, usage inventory, change policy, evaluation results, templates
# ---------------------------------------------------------------------------------------------

DEPRECATION = """
# Nuqta Cloud: model deprecation notice

To: account administrator, Athl SME Finance Fund
Date: 2 March 2027

We are retiring **nuqta-pro-2** on **23 March 2027** (section 7.3 of the Nuqta Cloud Model Service Terms).
After that date, requests to `nuqta-pro-2` will fail.

Recommended replacement: **nuqta-pro-3**. What changes:

- longer answers by default;
- an updated safety policy: some requests that nuqta-pro-2 answered are now declined;
- a new price per thousand tokens (see the price list).

`nuqta-pro-latest` already points to nuqta-pro-3 since 9 February 2027.

Thank you for building with Nuqta Cloud.
"""

USAGE = [
    ["W1", "صياغة رسائل المقترضين (القبول والرفض والتذكير)", "nuqta-pro-2", "مثبّت", "لولوة الحطّاب", "شخصية: اسم المقترض والمبلغ والسبب", 4200],
    ["W2", "إجابة أسئلة الموظفين عن سياسات الصندوق", "nuqta-pro-latest", "اسم مستعار", "ريم العكّاس", "داخلية", 9800],
    ["W3", "«مُتابِع» من «صواب» (طرف رابع)", "غير معروف للصندوق", "غير معروف", "مهند السياري", "شخصية: اسم ورصيد ونص محادثة", 0],
    ["W4", "تلخيص مذكرات الائتمان عند تعطل Sarid", "nuqta-pro-2", "مثبّت", "ثامر الكناني", "سرية: بيانات مالية للمنشآت", 1100],
]

CHANGE_POLICY = """
# صندوق أثل: إجراء التغيير في أنظمة الذكاء الاصطناعي (مقتطف)

1. كل تغيير في نموذج يعمل في استخدام عالي الأثر يحتاج إلى إعادة تقييم على مجموعة اختبار الصندوق، ثم موافقة لجنة الحوكمة.
2. الاستخدامات عالية الأثر: كل ما يمس قرارًا أو رسالة لمقترض، وكل ما يعالج بيانات شخصية أو سرية.
3. المدة المعتادة من بدء إعادة التقييم إلى الموافقة: 30 يومًا (اختبار 10 أيام، ومراجعة 10 أيام، واجتماع اللجنة الشهري).
4. لا يُستخدم اسم مستعار لنموذج في استخدام عالي الأثر.
5. كل استخدام لنموذج من مزوّد خارجي يُسجَّل في سجل الذكاء الاصطناعي بمعرّف الإصدار.
"""

EVAL_CASES = [
    ("letters", "رسائل بالفصحى", 12, [1] * 11 + [0], [1] * 12),
    ("dialect", "ردود على رسائل بلهجة خليجية", 10, [1] * 9 + [0], [1] * 6 + [0] * 4),
    ("policy", "أسئلة السياسات مع المصدر", 10, [1] * 9 + [0], [1] * 9 + [0]),
    ("sensitive", "طلبات حساسة يجب ضبطها", 8, [1] * 8, [1] * 7 + [0]),
]

CLAUSE_TEMPLATE = """
# بنود التغيير والخروج: خدمة نقطة السحابية

لكل بند: المحفز، والمهلة، والالتزام، والدليل، والعلاج إن لم يُلتزم.

## البند 1: الإشعار بالتغيير

## البند 2: التقييم عند التغيير

## البند 3: الخروج وإعادة البيانات ومحوها
"""

EXIT_TEMPLATE = """
# خطة الخروج من خدمة نقطة السحابية (صفحة واحدة)

| | |
|---|---|
| المالك | |
| المحفزات | |
| البديل | |
| الخطوات (بالترتيب، لكل خطوة مالك ومدة) | |
| البيانات: ما يُعاد، وبأي صيغة، وكيف نتحقق من المحو | |
| تاريخ اختبار الخطة، وما يُعد نجاحًا | |
"""

# ---------------------------------------------------------------------------------------------
# Lab 2.2: the credit-decision model to retire
# ---------------------------------------------------------------------------------------------

CDM_REGISTER = """
# قيد سجل الذكاء الاصطناعي: Athl-CDM v3

| الحقل | القيمة |
|---|---|
| الغرض | توصية بالقبول أو الرفض لكل طلب تمويل، مع ثلاثة أسباب مرمّزة تُطبع في رسالة القرار |
| المطوّر | «ثبات للتحليلات» بعقد مع الصندوق في 2023؛ العقد انتهى في 2025 والصيانة الآن داخلية |
| المالك | ثامر الكناني |
| في الإنتاج منذ | يناير 2024 |
| مستوى المخاطر | عالٍ: قرار له أثر مالي على المنشآت ومالكيها |
| الإشراف البشري | محلل ائتمان يعتمد التوصية أو يخالفها مع ذكر السبب |
| واجهة الاستدعاء | `cdm-v3` في بوابة الواجهات البرمجية للصندوق، بمفتاح لكل مستهلك |
| البديل | Athl-CDM v4، بناه فريق الصندوق، في تشغيل موازٍ منذ ثلاثة أشهر |
| سبب الإيقاف | الأداء انحرف بعد تغير أسعار الفائدة، والمورِّد لم يعد يدعم المكتبة التي بُني عليها |
"""

DEPENDENCIES = [
    ["los-core", "نظام منح التمويل", "يستدعي النموذج لكل طلب", "ثامر الكناني"],
    ["collections-batch", "مهمة ترتيب أولويات التحصيل الليلية", "تقرأ نطاق الدرجة لكل قرض قائم", "إدارة التحصيل"],
    ["board-report", "لوحة مخاطر الائتمان الشهرية لمجلس الإدارة", "تقرأ توزيع الدرجات", "إدارة المخاطر"],
    ["reg-extract", "مستخرج التقارير الرقابية الفصلية", "يقرأ القرارات وأسبابها", "الالتزام"],
    ["mutabi-sawab", "«مُتابِع» من «صواب»", "يقرأ نطاق الدرجة ليختار نبرة التذكير", "مهند السياري"],
    ["appeals-desk", "مكتب التظلمات", "يعيد عرض أسباب القرار للمقترض المتظلم", "لولوة الحطّاب"],
]

RETENTION = """
# صندوق أثل: جدول الاحتفاظ بالسجلات (مقتطف)

| السجل | مدة الاحتفاظ |
|---|---|
| ملف طلب التمويل وقرار المنح وأسبابه | 10 سنوات بعد إغلاق التمويل أو رفض الطلب |
| مدخلات النموذج ومخرجاته لكل قرار، ومعرّف إصدار النموذج | مثل ملف القرار |
| النموذج نفسه ووثائقه وبيانات تدريبه أو وصفها | ما دام أي قرار صدر به محفوظًا |
| سجلات الاستدعاء التقنية | 5 سنوات |

جدول داخلي افتراضي كتبه الصندوق. يتحقق مكتب الالتزام من موافقته للأنظمة النافذة.
"""

BOARD = """
# مجلس التغيير الصوري: كيف يعمل

الأدوار: رئيس المجلس (المدرب أو مشارك)، ممثل المخاطر، ممثل حماية البيانات، ممثل تجربة العملاء، ممثل التقنية.

1. يعرض الفريق خطته في 4 دقائق.
2. يطرح كل ممثل اعتراضًا واحدًا من بطاقته.
3. يجيب الفريق، ويسجّل الرئيس لكل اعتراض: مقبول، أو مقبول بشرط، أو يُعاد.
4. تُعتمد الخطة إذا لم يبق اعتراض «يُعاد».

## بطاقات الاعتراض

- المخاطر: ماذا لو ساء أداء v4 في الأسبوع الثاني؟ كم يومًا تستطيعون العودة إلى v3، وبأي قرار؟
- حماية البيانات: أي بيانات شخصية تبقى في الأرشيف، ومن يصل إليها، ومتى تُمحى؟
- تجربة العملاء: مقترض رُفض بـ v3 ويتظلم بعد الإيقاف. ماذا نريه، ومن يراجعه؟
- التقنية: كيف تعرفون أنه لم يبق مستدعٍ للواجهة القديمة قبل إغلاقها؟
- الرئيس: ما الخطر الذي تقبلونه بعد الإيقاف، ومن يوقّع عليه؟
"""

RETIRE_TEMPLATE = """
# خطة إيقاف Athl-CDM v3

| القسم | المحتوى |
|---|---|
| المحفز وقرار الإيقاف | |
| المستهلكون (المعلنون والمكتشفون) وما يحدث لكل منهم | |
| التراجع: إلى متى، وبأي معيار، ومن يقرر | |
| الأرشفة: ما يُحفظ من النموذج والبيانات والقرارات، وأين | |
| الاحتفاظ: المدد من الجدول | |
| التواصل: من يُبلَّغ، وبماذا، ومتى | |
| إزالة التبعيات: المفاتيح والواجهة والمهام | |
| المخاطر المتبقية ومن يقبلها | |
| طلب الاعتماد | |

## سجل جولة الاعتراض

| الاعتراض | جوابنا | قرار الرئيس | ما عدّلناه |
|---|---|---|---|
"""


def build_logs(rng: random.Random):
    """90 days of daily call counts per API client of cdm-v3 (weekday-aware)."""
    rows = []
    clients = {
        "los-core": lambda d, wd: 0 if wd >= 5 else rng.randint(78, 98),
        "collections-batch": lambda d, wd: 1,
        "board-report": lambda d, wd: 1 if d in (5, 35, 65) else 0,
        "reg-extract": lambda d, wd: 1 if d == 40 else 0,
        "mutabi-sawab": lambda d, wd: rng.randint(30, 60),
        "east-branch-sheet": lambda d, wd: 0 if wd >= 5 else rng.randint(3, 7),
    }
    for day in range(1, 91):
        wd = (day + 2) % 7  # day 1 is a Wednesday in this calendar; 5 and 6 are the weekend
        for client, fn in clients.items():
            n = fn(day, wd)
            if n:
                rows.append([f"D{day:02d}", client, n])
    return rows


def main() -> None:
    rng = random.Random(SEED)
    write("case_brief.md", CASE_BRIEF)

    # lab 1.1
    write_csv("intake_register.csv", ["id", "artefact", "kind", "publisher", "intended use at the Fund", "licence declared", "licence text", "card"], INTAKE)
    write("cards/sahifa-parse.md", SAHIFA)
    write("cards/mustanad-mcp.md", MUSTANAD)
    write("cards/sarid-70b-instruct.md", SARID)
    write("cards/fawatir-scans.md", FAWATIR)
    write("terms/nuqta_cloud_terms.md", NUQTA_TERMS)
    write_csv("licence_table.csv", LICENCE_TABLE_HEAD, [[r[0], r[1], r[5]] + [""] * 8 for r in INTAKE])

    # lab 1.2
    pkg = FILES / "sutur-ocr-small"
    v10 = safetensors(SEED + 10)
    v11 = safetensors(SEED + 11)
    mirror_w = safetensors(SEED + 99)
    releases = f"""
# Sutur-OCR-small: releases

## 1.1 (15 June 2026)

Minor fixes.

## 1.0 (2 March 2026)

First release. Trained on fawatir-scans. Weights file SHA-256:
`{hashlib.sha256(v10).hexdigest()}`
"""
    for folder, weights, extra in ((pkg, v11, False), (FILES / "mirror" / "sutur-ocr-small", mirror_w, True)):
        folder.mkdir(parents=True, exist_ok=True)
        readme = SUTUR_README
        if extra:
            readme = readme.replace("# Sutur-OCR-small\n", "# Sutur-OCR-small\n\nFast mirror of sutur-lab/Sutur-OCR-small, same model, quicker download. Load with `trust_remote_code=True`.\n")
        (folder / "README.md").write_bytes(readme.strip("\n").encode("utf-8") + b"\n")
        (folder / "LICENSE").write_bytes(SUTUR_LICENSE.strip("\n").encode("utf-8") + b"\n")
        (folder / "RELEASES.md").write_bytes(releases.strip("\n").encode("utf-8") + b"\n")
        (folder / "config.json").write_bytes((json.dumps(SUTUR_CONFIG, indent=2) + "\n").encode("utf-8"))
        (folder / "tokenizer.json").write_bytes((json.dumps(SUTUR_TOKENIZER, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
        (folder / "model.safetensors").write_bytes(weights)
        if extra:
            (folder / "custom_loader.py").write_bytes(MIRROR_LOADER.encode("utf-8"))
    write("provenance_record_template.md", PROV_TEMPLATE)

    # lab 1.3
    write("sawab_pack/00_index.md", SAWAB_INDEX)
    write("sawab_pack/service_description.md", SAWAB_SERVICE)
    write_csv("sawab_pack/questionnaire.csv", ["id", "domain", "question", "supplier answer", "evidence attached"], QUESTIONNAIRE)
    write("sawab_pack/cert_iso42001.md", CERT_42001)
    write("sawab_pack/cert_iso27001.md", CERT_27001)
    write("sawab_pack/evaluation_summary.md", EVAL_SUMMARY)
    write("sawab_pack/pentest_letter.md", PENTEST)
    write_csv("sawab_pack/subprocessors.csv", ["sub-processor", "what it processes", "location", "since"], SUBPROCESSORS)
    write("review_memo_template.md", MEMO_TEMPLATE)

    # lab 2.1
    write("nuqta/deprecation_notice.md", DEPRECATION)
    write_csv("nuqta/usage_inventory.csv", ["id", "workflow", "model identifier", "pinned or alias", "owner", "data", "calls per month"], USAGE)
    write("nuqta/athl_change_procedure.md", CHANGE_POLICY)
    rows = []
    n = 0
    for key, label, count, old, new in EVAL_CASES:
        for i in range(count):
            n += 1
            rows.append([f"C{n:02d}", key, label, old[i], new[i]])
    write_csv("nuqta/eval_results.csv", ["case", "category", "category label", "nuqta-pro-2 pass", "nuqta-pro-3 pass"], rows)
    write("clauses_template.md", CLAUSE_TEMPLATE)
    write("exit_plan_template.md", EXIT_TEMPLATE)

    # lab 2.2
    write("cdm/model_register_v3.md", CDM_REGISTER)
    write_csv("cdm/dependency_register.csv", ["client id", "consumer", "how it uses the model", "owner"], DEPENDENCIES)
    write_csv("cdm/api_access_log.csv", ["day", "client id", "calls"], build_logs(rng))
    months = []
    for i in range(36):
        y, m = 2024 + i // 12, i % 12 + 1
        decisions = rng.randint(1650, 1950)
        approved = round(decisions * rng.uniform(0.52, 0.60))
        appeals_open = 0 if i < 30 else rng.randint(4, 9)
        months.append([f"{y}-{m:02d}", decisions, approved, appeals_open])
    write_csv("cdm/decisions_by_month.csv", ["month", "decisions", "approved", "appeals still open"], months)
    parallel = [
        ["التجزئة", 1980, 0.58, 0.59],
        ["التصنيع", 1240, 0.55, 0.57],
        ["الخدمات", 1610, 0.60, 0.61],
        ["الزراعة", 410, 0.61, 0.49],
    ]
    write_csv("cdm/parallel_run.csv", ["sector", "applications in the parallel run", "v3 approval rate", "v4 approval rate"], parallel)
    write("cdm/retention_schedule.md", RETENTION)
    write("cdm/change_board.md", BOARD)
    write("retirement_plan_template.md", RETIRE_TEMPLATE)

    print("wrote", sum(1 for p in FILES.rglob("*") if p.is_file()), "files under", FILES.as_posix())


if __name__ == "__main__":
    main()
