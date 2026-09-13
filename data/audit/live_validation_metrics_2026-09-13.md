# Live validation metrics — pass 1

Date: 13/09/2026

Universe: 34 Greater Sydney hospitality-related signals assembled from 28 liquor-application triggers and 6 planning/DA triggers.

## Provisional outcome counts

- Validated opportunity: 9
- Probable opportunity: 1
- Clearly not new: 6
- Likely not new: 1
- Failed / withdrawn: 1
- Needs further review: 16

18/34 records currently have enough evidence for a provisional outcome. The unresolved records are deliberately excluded from any final hit-rate calculation.

## What pass 1 already proves

1. A new liquor licence is a useful trigger but is not a reliable proxy for a new venue.
2. Existing venues can lodge new-licence applications, producing false positives for a supplier seeking net-new accounts.
3. A venue that is trading today can still represent a successful historical lead if the source signal preceded opening.
4. Planning/DA evidence materially improves confidence when it corroborates a new licence, fit-out, change-of-use or newly leased hospitality tenancy.
5. Tenancy-level matching matters. A building-level address can contain multiple existing and new hospitality businesses simultaneously.
6. Free web enrichment can already recover venue identity, operator/group and public business contact details for some validated opportunities, but coverage is incomplete.

## Examples of validated signals

- 40 Myoora Road, Terrey Hills: approved large hospitality development, The Farmhouse / The Boathouse Group.
- RT.319, 5 Footbridge Boulevard, Wentworth Point: liquor trigger preceded Ciao Pizza now trading at the exact tenancy.
- 335B Henry Lawson Drive, Bankstown Aerodrome: trigger resolved to a new Guzman y Gomez that opened in May 2026.
- LG01 & LG02, 350 George Street, Sydney: April trigger preceded the July opening of Vespertine by Bentley Restaurant Group.
- Ground Floor, 65-67 Foveaux Street, Surry Hills: lease/DA/liquor signals resolve to House of Bungalow.
- Shop 10, 101 Waterloo Road, Macquarie Park: recently leased retail shell followed by August restaurant-licence trigger; operator remains unresolved.
- 15 Hickson Road, Dawes Point: February DA resolves to The Wharf Restaurant and Bar now trading.

## Clear false-positive examples

- 345B Sussex Street: Chicken V was already trading before the 2026 licence trigger.
- Shop 1, 307 Military Road: Shot on Military is an existing cafe.
- 135 Crown Street: long-established Bar Reggio.
- Shop 11, 3-5 Greenfield Road: Maison Coffee already operates at the exact tenancy.
- 157 Concord Road: Baan Raun Thai states it has operated since 2008.
- 2 Station Street, Wentworthville: planning application explicitly describes expansion of an existing coffee shop, not a new venue.

## Next measurement target

Reduce `needs_review` from 16 to fewer than 5, then calculate:

- confirmed/probable opening-opportunity rate;
- clear false-positive rate;
- operator-identification coverage;
- public-contact coverage;
- proportion detectable before opening;
- median lead time where opening date can be established;
- manual research minutes per record.

Do not set product pricing from pass 1. The unresolved records are still too large a share of the sample.
