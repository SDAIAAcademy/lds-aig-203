# الذكاء الاصطناعي من أطراف خارجية: المختبرات

مختبرات المقرر LDS-AIG-203 من أكاديمية سدايا. كل مختبر صفحة تُفتح من صفحة المقرر، وكلها تعمل على ملفات **صندوق أَثْل لتمويل المنشآت الصغيرة والمتوسطة**، جهة افتراضية تتبنى ثلاثة نماذج خارجية وخدمة وكلاء مستضافة، وتستعد لإيقاف نموذج قرار ائتماني. كل مختبر يبدأ من ملفات مقدمة، ولا يحتاج نتيجة مختبر آخر.

لا يستدعي أي مختبر نموذجًا، ولا يُنزَّل فيه أي نموذج. يكفي جهاز محمول عادي.

## ما تحتاجه

- متصفح، وجدول بيانات، ومحرر نصوص.
- للمختبر 1.2 فقط: أداة [`uv`](https://docs.astral.sh/uv/). من هذا المجلد شغّل:

```
uv run tools/provenance.py check
```

ينزّل الأمر الأول مكتبتين من بايثون (`model-signing` و`pyopenssl`) ثم يطبع إصدار `model-signing`.

## المختبرات

| المختبر | الصفحة | الملفات |
|---|---|---|
| 1.1 جدول التراخيص الستة | `D1_1_licences.html` | `files/intake_register.csv`، `files/cards/`، `files/terms/`، `files/licence_table.csv` |
| 1.2 سجل منشأ نموذج مفتوح الأوزان | `D1_2_provenance.html` | `files/sutur-ocr-small/`، `files/mirror/`، `files/signatures/`، `tools/provenance.py` |
| 1.3 مذكرة مراجعة ضمان المورِّد | `D1_3_assurance.html` | `files/sawab_pack/`، `files/review_memo_template.md` |
| 2.1 بنود التغيير وخطة الخروج | `D2_1_exit.html` | `files/nuqta/`، `files/terms/`، `files/clauses_template.md`، `files/exit_plan_template.md` |
| 2.2 خطة إيقاف نموذج القرار الائتماني | `D2_2_retirement.html` | `files/cdm/`، `files/retirement_plan_template.md` |

## البيانات والتراخيص

- كل ما في `files/` اصطناعي كتبه `_tools/prepare_files.py` بمحتوى ثابت: الجهات والموردون والنماذج والأشخاص والأرقام. الجهات المانحة للشهادات في حزمة المورِّد افتراضية.
- ملف الأوزان في `files/sutur-ocr-small/` بضع مئات من البايتات بقيم عشوائية ثابتة: حزمة للتدريب على المنشأ والتوقيع، لا نموذج يعمل. التوقيع والمفتاح العام يولّدهما `_tools/sign_package.py`.
- نصوص التراخيص الحقيقية (Apache-2.0، MIT، AGPL-3.0، Llama 3.3 Community License، CC BY-NC 4.0) لا تُنسخ هنا: تُقرأ من صفحاتها الرسمية، والروابط في `files/intake_register.csv`. شروط «نقطة السحابية» مكتوبة للمقرر وليست شروط أي مزوّد حقيقي.
- لا تحفظ الملفات بمحرر يغيّر نهايات الأسطر في `files/sutur-ocr-small/`: التحقق من التوقيع يقارن البايتات.

## للمدرّب

- المراجع لكل مختبر في `solutions/` (تُستبعد من نسخة المتدربين).
- `uv run solutions/check.py` يعيد حساب كل رقم تعتمد عليه المراجع من الملفات، ويشغّل أداة المختبر 1.2 فعليًا، ويطبع PASS أو أول اختلاف.
- لإعادة توليد الملفات: `uv run _tools/prepare_files.py` ثم `uv run _tools/sign_package.py`.
