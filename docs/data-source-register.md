# Data source register

| Source | Status | Useful fields | Access / licence notes | V0 handling |
|---|---|---|---|---|
| Liquor & Gaming NSW Application Noticeboard | Confirmed public source | Application number/type, proposed licence name, address, LGA, documents, closing date, status | Public noticeboard. Automated retrieval method still to be established and checked against applicable terms/technical access. | Build adapter contract now; use captured/exported CSV during V0 until supported automated ingestion is confirmed. |
| NSW Planning Portal Online DA data | Confirmed public dataset | DA records lodged through Planning Portal; useful for fit-out/change-of-use and timing signals | Daily dataset; NSW Government states Creative Commons Attribution licence. Dataset page says the feed covers DAs lodged since 2019. | Build DA adapter against real export/feed once access method is confirmed. |
| ASIC Company Register dataset | Confirmed public weekly dataset | Company name, ACN, status, registration date and selected public register fields | ASIC publishes a weekly snapshot through data.gov.au. | Add after venue/operator matching rules are proven. |
| Open web / venue websites / socials | Confirmed research surface | Trading name, opening announcements, operator context, public business contacts | Provenance must be stored per fact. Do not turn AI inference into asserted fact. | Manual/semi-automated enrichment audit first. |
| Paid enrichment providers | Not selected | Additional business/contact enrichment | Unknown economics and reliability until free enrichment coverage is measured. | Explicitly deferred. |

## Source principles

1. Preserve every raw source record before transformation.
2. Store source URL and observation/verification time for derived facts.
3. A blank field is preferable to an unsupported fact.
4. Keep confirmed facts distinct from strong/probable inference.
5. Do not make a source operationally critical until its access method and permitted use are confirmed.
