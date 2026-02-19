# TSmart Tool PRO - Advanced GSM Suite

![TSmart Tool Logo](https://raw.githubusercontent.com/eihabnjwagpi1992-collab/tsmart-tool/main/.github/assets/logo.png) <!-- Placeholder for a logo, if available -->

## نظرة عامة

**TSmart Tool PRO** هي مجموعة أدوات برمجية متقدمة وشاملة مصممة خصيصًا لفنيي صيانة الهواتف المحمولة. توفر الأداة واجهة رسومية سهلة الاستخدام (GUI) للتعامل مع مجموعة واسعة من الأجهزة التي تعمل بمعالجات **Samsung, MediaTek (MTK), Unisoc (Spreadtrum), و Xiaomi**. تدمج الأداة العديد من الوظائف الأساسية والمتقدمة مثل فلاش الرومات، إزالة قفل FRP، وإصلاح مشاكل السوفتوير المختلفة، مما يجعلها حلاً متكاملاً لا غنى عنه في ورشة الصيانة.

## الميزات الرئيسية

*   **دعم شامل للأجهزة**: تدعم أجهزة Samsung, MediaTek, Unisoc, و Xiaomi.
*   **واجهة رسومية بديهية**: مبنية باستخدام `customtkinter` لتجربة مستخدم سلسة وجذابة.
*   **وظائف متقدمة**: فلاش الرومات، إزالة FRP، فتح/قفل البوتلودر، فورمات البيانات، تجاوز Mi Cloud، وغيرها.
*   **مراقبة الأجهزة في الوقت الفعلي**: تتعرف تلقائيًا على الأجهزة المتصلة في أوضاع ADB, Fastboot, MTK, EDL, و COM.
*   **نظام ترخيص مرن**: يعتمد على معرف الجهاز (HWID) مع خيارات اشتراك متعددة (3، 6، 12 شهر).
*   **بوت تيليجرام للإدارة**: واجهة عن بعد لإدارة الاشتراكات وتوليد مفاتيح التفعيل.
*   **أدوات مدمجة**: تتضمن أدوات ADB/Fastboot، ومكتبات `mtkclient`, `penumbra`, و `unisoc`.

## المتطلبات

*   **نظام التشغيل**: Windows 10/11 (موصى به).
*   **Python**: الإصدار 3.10 أو أحدث.
*   **تعريفات الأجهزة**: يجب تثبيت تعريفات USB المناسبة لأجهزة Samsung, MTK, Unisoc, و Xiaomi.

## التثبيت

للبدء باستخدام TSmart Tool PRO، اتبع الخطوات التالية:

1.  **استنساخ المستودع (Clone the Repository)**:
    ```bash
    git clone https://github.com/eihabnjwagpi1992-collab/tsmart-tool.git
    cd tsmart-tool
    ```

2.  **إنشاء بيئة افتراضية (Optional but Recommended)**:
    ```bash
    python -m venv venv
    # على Windows
    .\venv\Scripts\activate
    # على Linux/macOS
    source venv/bin/activate
    ```

3.  **تثبيت التبعيات (Install Dependencies)**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **إعداد ملف البيئة (Setup .env file)**:
    قم بإنشاء ملف جديد باسم `.env` في المجلد الرئيسي للمشروع (نفس المجلد الذي يحتوي على `main.py`) وأضف إليه المتغيرات التالية:
    ```dotenv
    TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
    ADMIN_ID=YOUR_TELEGRAM_ADMIN_ID_HERE
    ```
    *   استبدل `YOUR_TELEGRAM_BOT_TOKEN_HERE` بالتوكن الخاص ببوت تيليجرام الخاص بك.
    *   استبدل `YOUR_TELEGRAM_ADMIN_ID_HERE` بمعرف حسابك الشخصي على تيليجرام (يمكنك الحصول عليه من بوت مثل `@userinfobot`).

    **ملاحظة هامة**: ملف `.env` محمي بواسطة `.gitignore` ولن يتم رفعه إلى GitHub، مما يحافظ على أمان توكن البوت الخاص بك.

## الاستخدام

لتشغيل الأداة، افتح موجه الأوامر (Command Prompt) أو الطرفية (Terminal) في مجلد المشروع وقم بتشغيل الملف الرئيسي:

```bash
python main.py
```

لإدارة البوت الخاص بالاشتراكات:

```bash
python tsp_bot.py
# أو
python tsmart_bot.py
```

## البناء كملف تنفيذي (EXE)

يمكن بناء الأداة كملف تنفيذي مستقل (.exe) لنظام التشغيل Windows باستخدام PyInstaller. تم توفير إعدادات البناء في ملف `.github/workflows/build.yml`.

```bash
# تأكد من تثبيت PyInstaller أولاً
pip install pyinstaller

# ثم قم بتشغيل أمر البناء
pyinstaller --onefile --windowed \
  --add-data "mtkclient;mtkclient" \
  --add-data "unisoc;unisoc" \
  --add-data "penumbra;penumbra" \
  --add-data "bin;bin" \
  --name "Tsmart_Pro_Tool_v2.1" \
  --hidden-import="usb.backend.libusb1" \
  --hidden-import="serial" \
  main.py
```

سيتم إنشاء الملف التنفيذي في مجلد `dist/`.

## المساهمة

نرحب بالمساهمات لتحسين الأداة! إذا كنت ترغب في المساهمة، يرجى اتباع الإرشادات التالية:

1.  قم بعمل `Fork` للمستودع.
2.  أنشئ فرعًا جديدًا لميزتك (`git checkout -b feature/AmazingFeature`).
3.  قم بإجراء تغييراتك واختبرها.
4.  تأكد من أن الكود يتبع معايير PEP 8 (يمكنك استخدام `black` و `isort`).
5.  قم بعمل `Commit` لتغييراتك (`git commit -m 'Add some AmazingFeature'`).
6.  ادفع إلى الفرع (`git push origin feature/AmazingFeature`).
7.  افتح `Pull Request`.

## الترخيص

هذا المشروع لا يحتوي حاليًا على ملف ترخيص صريح. يرجى التواصل مع المالك للحصول على معلومات حول شروط الاستخدام والترخيص.

## الأمان والخصوصية

*   **توكنات البوت**: تم نقل توكنات بوت تيليجرام إلى ملف `.env` لضمان عدم كشفها في الكود المصدري. **تأكد من عدم مشاركة ملف `.env` الخاص بك مع أي شخص.**
*   **معرف الجهاز (HWID)**: يستخدم المشروع معرف الجهاز لتفعيل التراخيص. يتم توليد هذا المعرف محليًا ولا يتم إرساله إلى أي خوادم خارجية إلا إذا تم تكوين ذلك صراحة في نظام الترخيص.

## شكر وتقدير

نود أن نشكر جميع المساهمين والمطورين الذين ساهموا في المكتبات والأدوات مفتوحة المصدر التي تم دمجها في هذا المشروع، مثل `mtkclient`, `penumbra`, و `unisoc`.

---

**المؤلف**: Manus AI (بالنيابة عن المستخدم)
**الإصدار**: 2.5 (بعد الصيانة)
**تاريخ آخر تحديث**: 18 فبراير 2026
