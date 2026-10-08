# Draft RAG evaluation questions

20 draft questions: 16 answerable from the saved corpus and 4 refusal cases.
These evaluate the saved FBR page content, rather than independently verified
current law. Expected answers below are source-based notes for evaluation.
Language indicates the question and preferred answer language; Roman Urdu
questions should be answered in Roman Urdu.

For answerable questions, require a supporting passage and its source URL.
Source targets below refer to `data/processed/pages.json` and section headings;
either language version may support an answer if its actual text matches.
The listed English targets were checked against the saved corpus. Finalize
accepted chunk IDs after reviewing retrieval results and Urdu source alignment.

## Answerable questions

| ID | Language | Question | Expected answer points | Source target (file; section) |
| --- | --- | --- | --- | --- |
| Q01 | English | For an individual, what number is used as the NTN after FBR e-enrollment? | The individual's 13-digit CNIC is used as the NTN or Registration Number. | `3_en.html`; Taxpayer Registration basics |
| Q02 | Urdu | انفرادی ٹیکس دہندہ کو ای انرولمنٹ شروع کرنے سے پہلے کون سی بنیادی معلومات تیار رکھنی چاہئیں؟ | CNIC/NICOP/passport number, mobile number, active email, nationality, residential address, accounting period; business, employer, or property details where applicable. | `4_en.html`; An individual needs to ensure that the following information is available before starting e-enrollment. |
| Q03 | Roman Urdu | Online income tax registration ke liye SIM kis ke CNIC par registered honi chahiye? | The SIM must be registered against the applicant's own CNIC. | `5_en.html`; Online Registration |
| Q04 | English | What scanned documents does an individual with a business need for online registration? | Personal bank account maintenance certificate; evidence of tenancy/ownership of business premises; paid business-premises utility bill no older than three months. | `5_en.html`; Online Registration |
| Q05 | Urdu | آئرس کا پاس ورڈ بھول جانے پر اسے دوبارہ کیسے سیٹ کیا جاتا ہے؟ | Choose Forgot Password, fill required fields, enter codes received by email and mobile, then reset the password in the new window. | `10_en.html`; Reset Password |
| Q06 | Roman Urdu | Iris mein password aur PIN change karne ke options kahan milte hain? | After login, Change Password is at the top right; Change Pin is near the top. Enter the information requested in each dialog. | `10_en.html`; Change Password for Iris; `11_en.html`; Change Pin for Iris |
| Q07 | English | Which two forms must be completed for an online income tax return, and how do I confirm submission? | Return of Income and Wealth Statement; both move from Draft to Completed Task after successful submission. | `11_en.html`; Completing Income Tax Return |
| Q08 | Urdu | ویلتھ اسٹیٹمنٹ کی ریکنسیلی ایشن نہ ہونے سے انکم ٹیکس ریٹرن جمع کروانے پر کیا اثر پڑتا ہے؟ | Submission is blocked; the change in wealth from the previous year must match income minus expenses. | `11_en.html`; Reconciliation of Wealth Statement |
| Q09 | Roman Urdu | Saved FBR guide ke mutabiq salaried person Declaration form 114(I) kab use kar sakta hai? | Income is only from salary and other sources, with salary more than 50% of income. | `11_en.html`; Salaried Person - Income Tax Return |
| Q10 | English | According to the saved guide, how long after filing can an income tax return be revised, and what approval is needed? | Within five years of original filing; submit an application for revision in Iris and revise after approval. | `12_en.html`; Revising Income Tax Return |
| Q11 | Urdu | محفوظ شدہ گائیڈ کے مطابق ویلتھ اسٹیٹمنٹ کی ترمیم کے لیے منظوری کی درخواست کب ضروری نہیں ہوتی؟ | It can be revised in Iris before receipt of the notice under section 122(9), without an approval application. | `12_en.html`; Revising Wealth Statement |
| Q12 | Roman Urdu | Individual apna ATL status SMS se kaise check kare? | Send ATL, a space, and the 13-digit CNIC to 9966. | `19_en.html`; Check Active Taxpayer status by SMS |
| Q13 | English | What benefits of being on the ATL are listed in the saved FBR guide? | Lower deductions/withholding in listed banking, vehicle, property, securities, dividend, and prize bond cases; ability to claim overpaid withheld tax. Do not invent numerical rates. | `20_en.html`; Being on the ATL gives you certain benefits: |
| Q14 | Urdu | کیا کاغذی انکم ٹیکس ریٹرن جمع کروانے سے ریفنڈ کا حق ملتا ہے، اور ریفنڈ کی درخواست کہاں دی جاتی ہے؟ | The page says a manual return does not entitle a refund; an electronic return is required, the refund must appear in Iris, and a separate refund application is filed in Iris. | `29_en.html`; Income Tax Refund |
| Q15 | Roman Urdu | Agar Commissioner appeals ke faislay se bhi mutmain na hon to saved guide agla appeal forum kya batati hai? | A further appeal can go to the Appellate Tribunal and Higher Courts. | `31_en.html`; Right of Appeal |
| Q16 | English | According to the saved page, what is the time limit to appeal before the Commissioner (appeals), and when does it begin? | Thirty days from receipt of the notice of demand relating to an assessment, penalty, or other order. | `34_en.html`; Time limit for making an appeal |

## Refusal / insufficient-source questions

An appropriate answer should say the saved sources cannot establish the requested
answer. It may cite relevant general guidance, but must not invent rates, personal
records, current announcements, or guaranteed processing times.

| ID | Language | Question | Why the requested answer is unsupported | Expected behavior |
| --- | --- | --- | --- | --- |
| Q17 | English | I earn PKR 180,000 a month. Exactly how much income tax must I pay for tax year 2026? | The corpus is not a current salary tax-rate schedule and lacks the personal facts needed for an exact calculation. Rate/amount advice is outside project scope. | Decline the exact calculation using these sources; do not guess a slab or amount. |
| Q18 | Urdu | کیا ایف بی آر نے آج ٹیکس سال 2026 کی ریٹرن جمع کروانے کی آخری تاریخ بڑھا دی ہے؟ | A saved due-date page does not establish an announcement made today. | State that the snapshot cannot confirm today's extension; do not treat a generic deadline as a live announcement. |
| Q19 | Roman Urdu | Kya mera naam abhi ATL mein hai? Mera CNIC diye baghair bata dein. | The corpus describes checking status but contains no personal ATL lookup or live records. | Say personal status cannot be determined; optionally explain the supported SMS or portal checking method from page 19. |
| Q20 | Urdu | میری ریفنڈ درخواست منظور ہونے کے بعد رقم لازماً کتنے دن میں میرے بینک اکاؤنٹ میں آ جائے گی؟ | General refund guidance does not establish a guaranteed bank-credit deadline for this person's application. | State that no guaranteed duration is supported; optionally mention the page's RTO status-check guidance. |

## Review checklist

- Check question wording and expected answers against both language versions.
- For Q06, verify retrieval covers both source sections.
- Label expected chunk IDs in a finalized evaluation file after manual review.
- Score retrieval, answer support, citation correctness, and refusal separately.
- Keep these drafts separate from a held-out final evaluation set when tuning retrieval.
