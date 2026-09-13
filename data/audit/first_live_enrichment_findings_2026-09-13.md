# First live enrichment findings — 13/09/2026

This is an early audit of the first live Greater Sydney seed. It is deliberately small and exists to test whether a `new licence` signal is equivalent to a genuinely new venue. It is not.

## Findings

### 345B Sussex Street, Sydney — liquor signal APP-0016713229 seed address check

The live liquor signal is a new on-premises restaurant licence at Shop G01 / 345B Sussex Street. Independent web research shows an established restaurant, Chicken V Sydney, already trading at 345B Sussex Street, with an existing public restaurant listing and trading hours.

**Audit interpretation:** likely not a genuinely new hospitality venue at address level. Needs tenancy-level matching and operator/licence context before being treated as a sales lead.

**Evidence:**
- Liquor discovery signal: Planning Alerts / NSW ILGA feed.
- Existing venue evidence: OpenTable listing for Chicken V Sydney at 345B Sussex Street.

### 135 Crown Street, Darlinghurst — APP-0016685047

The liquor signal is `New licence - on premises - restaurant`. Current public listings show Bar Reggio actively trading at 135 Crown Street with current hours, website and contact details.

**Audit interpretation:** a new liquor licence signal can occur at an already-operating venue. `new licence` must not automatically become `new venue`.

**Evidence:**
- https://www.planningalerts.org.au/applications/3532057
- Current Bar Reggio public listings at 135 Crown Street.

### Shop 1, 307 Military Road, Cremorne — APP-0016304747

The liquor signal is `New licence - on premises - restaurant`. Current public listings show Shot on Military operating from Shop 1, 307 Military Road.

The same building also has another new-licence restaurant signal for Shop 7, where current public listings identify Calamansi, a recently opened restaurant/wine bar associated with Sarah Tiong.

**Audit interpretation:** tenancy precision matters. Building-level address matching would incorrectly merge two materially different opportunities. Unit/shop identifiers must be preserved during normalisation and matching.

**Evidence:**
- https://www.planningalerts.org.au/applications/3481131
- https://www.planningalerts.org.au/applications/3473368
- Current Shot on Military and Calamansi public listings.

### 23–25 Mangrove Lane, Taren Point

A current ILGA feed entry shows a new on-premises licence at this address. Independent sources describe the property as a large industrial/warehouse facility and show established non-hospitality businesses associated with the address.

**Audit interpretation:** this is a useful anomaly/edge case. It should remain in the validation set rather than being manually deleted, because the classifier needs to learn how to reject or investigate signals whose surrounding evidence does not fit a hospitality-opening pattern.

### Tenancy RT.319, 5 Footbridge Boulevard, Wentworth Point

The ILGA signal is a new on-premises restaurant licence. Current food-delivery listings identify Ciao Pizza at Shop 319 / 5 Footbridge Boulevard and mark it as new.

**Audit interpretation:** this is the kind of signal we want. It appears capable of resolving from regulatory address -> specific tenancy -> trading venue using free public enrichment.

## Immediate changes to the process

1. Preserve shop/unit/tenancy identifiers during address normalisation. Do not collapse matching to building number + street alone.
2. Add an `existing_venue_at_signal_date` enrichment check before calling a signal a new venue.
3. Separate `new licence` from `new venue` as distinct concepts in the classification model.
4. Add a venue-stage field such as `pre-opening`, `recently-opened`, `existing`, `unclear`.
5. Keep anomalous records in the audit sample so false-positive rate can be measured rather than hidden.
6. Treat current website/social/delivery/booking evidence as useful enrichment, but preserve source and observation date.

## Early conclusion

The live test has already justified the enrichment stage. The raw regulatory signal is valuable but insufficient on its own. Free public enrichment can both remove false positives and identify the actual venue/operator in at least some cases. The next audit should measure this systematically across the full 30–50 venue sample.
