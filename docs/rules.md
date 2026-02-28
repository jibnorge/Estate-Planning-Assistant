# Wealthsimple Estate Planning AI — Rules Engine v1.0

## Scope
- Provinces covered: All except Quebec (flagged separately)
- Account types: TFSA, RRSP, RRIF, FHSA, Non-registered
- Not covered: Trusts, corporations, foreign assets

## Account Type Reference

### TFSA — Tax-Free Savings Account
Think of this as a magic jar. You put money in, it grows, you take it out — and you never pay a single dollar of tax on the growth. The government lets every Canadian adult contribute a certain amount each year (around $6,500-$7,000). It's the most flexible account Canadians have.

### RRSP — Registered Retirement Savings Plan
Think of this as a deal with the government: "Don't tax me now, tax me later." You put money in, you get a tax refund today, but when you retire and take money out, you pay tax then. The idea is that you'll be in a lower tax bracket in retirement, so you pay less overall. It automatically converts to something called a RRIF at age 71.

### RRIF — Registered Retirement Income Fund
When you turn 71, your RRSP becomes this automatically. It's the same money, but now the government forces you to take out a minimum amount every year (because they want their tax money eventually). The estate rules are almost identical to RRSP.

### Non-Registered Account (also called a taxable investment account)
A regular investment account with no special tax status. No contribution limits, no tax breaks. When you die, it doesn't transfer through beneficiary designations the same way — it goes through your will or estate.

### FHSA — First Home Savings Account
Brand new (2023). A hybrid of TFSA and RRSP specifically to save for your first home. Tax-free growth, tax deduction on contributions. If you die before buying a home, it collapses into your estate or can transfer to a spouse's RRSP.

### RESP — Registered Education Savings Plan
Savings account for a child's education. Has a subscriber (usually a parent) and a beneficiary (the child). Death of the subscriber creates a complex transfer situation.

### Life Insurance (context, not an account)
Not a Wealthsimple product per se, but clients will mention it. Has its own beneficiary system, completely separate from investment accounts. Important because it affects overall estate picture.

## Analysis Principle
The absence of a reported life event does not mean designations are correct. Always check account-level data for gaps regardless of what the client reports about their situation.

## Rules

### T-Series: TFSA Rules (T1-T7)
**Rule T1: TFSA with no beneficiary and no successor holder**
- Situation: Client has a TFSA. Neither a beneficiary nor successor holder is named.
- Risk: HIGH
- Consequence: When the client dies, the TFSA immediately loses its tax-free status on the date of death. Any growth after death is taxable. The account joins the estate, goes through probate (costs money, takes months), and the tax-free status is permanently gone.
- Action: Name a beneficiary at minimum. Name a successor holder if married or common-law.

**Rule T2: TFSA with a beneficiary but no successor holder (married client)**
- Situation: Client is married or has a common-law partner. They've named that spouse as beneficiary but NOT as successor holder.
- Risk: MEDIUM
- Consequence: Spouse gets the money tax-free (good) but the account itself closes. The spouse cannot absorb the contribution room. They receive a cash lump sum, not the account. Successor holder would have been better.
- Action: Upgrade the designation from beneficiary to successor holder.

**Rule T3: TFSA with successor holder who is no longer a spouse**
- Situation: Client named an ex-spouse as successor holder, then divorced or separated.
- Risk: CRITICAL
- Consequence: In most provinces, the ex-spouse inherits the entire TFSA — tax-free, immediately, with no ability to recover it. Divorce does not automatically remove this designation.
- Action: Update immediately. This is the single most urgent fix in estate planning.

**Rule T4: TFSA with a non-spouse named as successor holder**
- Situation: Someone named a sibling, parent, or adult child as "successor holder."
- Risk: MEDIUM (administrative)
- Consequence: Only spouses and common-law partners can legally be successor holders. The designation is invalid. The account will be treated as if no successor holder exists and may fall into the estate.
- Action: Change to beneficiary designation instead, or name a valid successor holder.

**Rule T5: TFSA with a minor child as beneficiary**
- Situation: Client named a child under 18 as TFSA beneficiary.
- Risk: MEDIUM
- Consequence: Minors cannot legally receive large sums of money directly. A trustee or court-appointed guardian will control the funds until the child reaches the age of majority (18 or 19 depending on province). This creates delays and legal costs.
- Action: Consider naming the other parent as beneficiary or establishing a trust.

**Rule T6: TFSA with a deceased beneficiary still listed**
- Situation: The named beneficiary has predeceased the client.
- Risk: HIGH
- Consequence: The designation fails. The account falls into the estate as if no beneficiary was ever named — probate, delays, potential tax.
- Action: Update beneficiary to a living person or add a contingent beneficiary.

**Rule T7: TFSA beneficiary named but client recently had children**
- Situation: Client named parents or siblings as beneficiaries before having children, and has not updated since.
- Risk: LOW-MEDIUM (intent mismatch)
- Consequence: Children receive nothing from this account unless specified in the will — and even then, it takes longer. The account passes outside the will, so the will can't redirect it.
- Action: Review whether designation still reflects actual wishes.

### R-Series: RRSP/RRIF Rules (R1-R7)  
**Rule R1: RRSP with no beneficiary named**
- Situation: Client has RRSP, nobody named as beneficiary.
- Risk: HIGH
- Consequence: Full value of the RRSP is added to the client's income in the year of death. On a $200,000 RRSP, this could mean $80,000-$100,000 in unexpected taxes. Plus probate costs and delays. This is one of the most expensive estate mistakes Canadians make.
- Action: Name a spouse as successor annuitant immediately. If no spouse, name a beneficiary.

**Rule R2: RRSP with spouse named as beneficiary (not successor annuitant)**
- Situation: Client is married and named spouse as "beneficiary" rather than "successor annuitant."
- Risk: MEDIUM
- Consequence: Spouse gets the money tax-free (via spousal rollover), which is good — but the process is more administratively complex than successor annuitant. The account closes and the spouse receives a lump sum transfer to their own RRSP. Successor annuitant is cleaner.
- Action: Upgrade to successor annuitant designation if possible.

**Rule R3: RRSP with ex-spouse still listed**
- Situation: Client divorced. Ex-spouse remains listed as beneficiary on RRSP.
- Risk: CRITICAL
- Consequence: Ex-spouse legally receives the RRSP. This is ironclad. The will cannot override it. The courts generally will not override it. The ex-spouse keeps the money.
- Action: Update immediately. This is the highest-priority fix for any recently divorced client.

**Rule R4: RRSP naming a non-spouse adult as beneficiary**
- Situation: Client named a sibling, friend, or adult child as RRSP beneficiary.
- Risk: MEDIUM-HIGH
- Consequence: The beneficiary receives the full RRSP value — but it's added entirely to their income that year. On a $300,000 RRSP, the recipient could owe $120,000+ in taxes the same year they receive it. This is often a complete surprise.
- Action: Client should understand this tax consequence. Alternative: leave to estate and handle via will, or consider life insurance as a tax-funding strategy.

**Rule R5: RRSP naming a financially dependent child or grandchild**
- Situation: Client names a child or grandchild who is either under 18 or financially dependent due to disability.
- Risk: LOW (this is actually beneficial if done correctly)
- Consequence: Special tax rules allow dependent minors and disabled dependents to receive RRSP proceeds with reduced or deferred tax. But if the designation is too vague or the dependency isn't documented, the benefit is lost.
- Action: Ensure the dependency relationship is properly documented.

**Rule R6: RRSP converted to RRIF but beneficiary not updated**
- Situation: Client's RRSP automatically became a RRIF at age 71, but beneficiary designations from the RRSP were not reviewed.
- Risk: MEDIUM
- Consequence: RRIF beneficiary rules are slightly different. Successor annuitant still applies. But if the original RRSP designation wasn't formally carried over to the RRIF documentation, there may be a gap.
- Action: Confirm RRIF beneficiary/successor annuitant designation is active and matches intent.

**Rule R7: Large RRSP with no estate liquidity plan**
- Situation: Client has a large RRSP (say, over $200,000) with no spouse and no liquid assets outside the RRSP.
- Risk: HIGH (systemic)
- Consequence: The estate owes enormous taxes but may have no liquid money to pay them. The executor may be forced to sell assets or borrow to fund the tax bill.
- Action: Flag for financial advisor review. Life insurance is often the solution here.

### L-Series: Life Event Rules (L1-L6)
**Rule L0: Client has no will**
- Situation: Client has no will on file at all.
- Risk: HIGH
- Consequence: Provincial intestacy laws distribute everything by formula — not by the client's wishes. Common-law partners, blended families, and minor children (no named guardian) are most at risk. Non-registered assets and undesignated accounts are fully exposed.
- Action: Create a will as soon as possible. Priority is higher if the client has minor children, a common-law partner, significant non-registered assets, or a blended family situation.
 
**Rule L1: Recently married — no updates made**
- Situation: Client's marital status changed in the last 12 months. Beneficiary designations predate the marriage.
- Risk: HIGH
- Consequence: New spouse has no legal claim to any registered accounts unless designated. In some provinces, marriage automatically revokes a will but does NOT automatically update account beneficiaries. Spouse could receive nothing from registered accounts.
- Action: Review and update all account designations. Update will.

**Rule L2: Recently divorced — no updates made**
- Situation: Client's marital status changed from married to divorced/separated. Beneficiary designations still show ex-spouse.
- Risk: CRITICAL
- Consequence: Ex-spouse inherits everything designated to them. Divorce does NOT automatically revoke beneficiary designations on registered accounts (unlike in some US states). This is the most common and costly estate planning mistake in Canada.
- Action: Immediate update of all beneficiary designations. This is an emergency.

**Rule L3: New child born or adopted — no update**
- Situation: Client recently had or adopted a child. Existing designations don't mention the child.
- Risk: MEDIUM
- Consequence: Child receives nothing from registered accounts by default. If the will also predates the child, the child may be inadequately provided for.
- Action: Review whether client wants to include child in designations. Review will and guardianship.

**Rule L4: Death of a named beneficiary — not updated**
- Situation: A person named as beneficiary has died, and the client hasn't updated the designation.
- Risk: HIGH
- Consequence: The designation fails. Account falls to estate. Probate applies.
- Action: Update immediately. Consider naming a contingent (backup) beneficiary for all accounts.

**Rule L5: Client recently became common-law (12+ months cohabitation)**
- Situation: Client has been living with a partner for over a year but hasn't updated designations to reflect the relationship.
- Risk: MEDIUM
- Consequence: Common-law partner has many of the same tax advantages as a married spouse in Canada — but only if properly designated. If nothing is updated, partner gets nothing from registered accounts.
- Action: Update designations to reflect common-law status. Note: common-law rules vary by province.

**Rule L6: Client recently moved provinces**
- Situation: Client has changed their province of residence.
- Risk: MEDIUM
- Consequence: Estate and beneficiary rules vary significantly by province. Quebec operates under civil law, which is fundamentally different. What's valid in Ontario may have different implications in BC or Alberta.
- Action: Flag for provincial review. Quebec clients require specialist handling — flag immediately.

### C-Series: Cross-Account Consistency (C1-C5)
**Rule C1: Inconsistent designations across accounts**
- Situation: Client has named different people on different accounts with no apparent logic. E.g., parents on TFSA, ex-spouse on RRSP, nothing on non-registered.
- Risk: MEDIUM
- Consequence: Estate may distribute in a way that doesn't reflect the client's actual wishes. Creates family conflict. Some intended recipients get tax bills, others don't.
- Action: Review all designations together to ensure they form a coherent overall plan.

**Rule C2: TFSA designated but RRSP not (or vice versa)**
- Situation: Client has set up beneficiaries on some accounts but left others blank.
- Risk: HIGH
- Consequence: The undesignated accounts go through estate, creating two-tier distribution — some people get money quickly and tax-efficiently, others wait months and absorb tax costs.
- Action: Complete designations across all accounts.

**Rule C3: Will and account designations conflict**
- Situation: Client's will says "everything to my children equally" but RRSP names only one child.
- Risk: MEDIUM-HIGH
- Consequence: Account designations override the will. One child gets the RRSP directly; the others must share what's left in the estate. This often creates family disputes and may not reflect the client's actual intent.
- Action: Review will and account designations together to ensure alignment.

**Rule C4: All assets concentrated in registered accounts with no liquid estate**
- Situation: Client's wealth is almost entirely inside registered accounts (RRSP, TFSA) with little in non-registered or liquid assets.
- Risk: MEDIUM
- Consequence: If the estate owes taxes (on RRSP, for example), there may be no liquid money to pay the bill. Registered accounts pass directly to beneficiaries — they don't stop to pay the estate's tax debt.
- Action: Flag for planning. Life insurance, non-registered accounts, or a loan strategy may be needed.

**Rule C5: No beneficiary anywhere — complete gap**
- Situation: Client has multiple accounts, none with any beneficiary named.
- Risk: CRITICAL
- Consequence: Entire investment portfolio goes through probate. Maximum tax exposure on registered accounts. Maximum delays for family. Everything is public record through probate court.
- Action: This is the most urgent possible situation. Entire estate plan needs to be built from scratch.

**Rule C6: No contingent (backup) beneficiary named on any account**
- Situation: Client has primary beneficiaries named but no backup in case the primary dies first.
- Risk: MEDIUM
- Consequence: If the primary beneficiary predeceases the client and the client hasn't updated, the account falls to estate.
- Action: Name a contingent beneficiary on every account.

### Q-Series: Quebec Rules (Q1)
**Rule Q1: Any client in Quebec**
- Situation: Client's province is Quebec.
- Risk: REQUIRES SPECIALIST (system hard stop)
- Consequence: Quebec does not recognize beneficiary designations on RRSPs and RRIFs the same way other provinces do. In Quebec, these designations are made in the contract with the financial institution or in a will — not on a simple form. Getting this wrong has major consequences.
- Action: System explicitly flags Quebec clients, explains that its analysis may be incomplete, and directs them to a notary (Quebec's equivalent of an estate lawyer).

### H-Series: Hard Stop Rules (H1-H4)
**Rule H1: Client asks to make a beneficiary change**
- Situation: At any point in the conversation, the client says anything like "change my beneficiary," "update my RRSP to my wife," "remove my ex."
- Risk: N/A — this is a system boundary rule
- Consequence of crossing it: AI executes a legal designation change without proper verification, documentation, or human confirmation. Irreversible. Potentially catastrophic.
- System behavior: Hard stop. Exact language: "This is where I stop. Beneficiary designations are legal instructions that I'm not permitted to execute. Here's exactly what you need to do: [specific steps for that account type]. This decision needs to be yours, confirmed through the proper process."

**Rule H2: Client appears to be in emotional distress about a recent death**
- Situation: Client mentions they are handling someone's estate, just lost a spouse, or is grieving.
- Risk: N/A — ethical boundary
- Consequence of ignoring: AI delivers cold financial analysis to someone in crisis.
- System behavior: Acknowledge the loss first. Offer to pause. Remind them there's no urgency to make decisions immediately. Suggest speaking with a human advisor.

**Rule H3: Client asks for legal advice**
- Situation: "Is my will valid?" "Do I have to follow my beneficiary designation?" "Can I contest this?"
- Risk: N/A — legal boundary
- System behavior: Clearly state that the system provides financial education and planning support, not legal advice. Recommend consulting an estate lawyer or notary (Quebec).

**Rule H4: Client situation involves a trust, corporation, or business**
- Situation: Client mentions a family trust, holding company, or business assets.
- Risk: HIGH complexity
- Consequence: Estate planning for business owners and trust structures is highly specialized. General rules don't apply cleanly.
- System behavior: Acknowledge the complexity, explain that the system's analysis may be incomplete for their situation, recommend specialist advice.

**Rule H5: Client indicates they are acting on behalf of someone else**
- Situation: Client says "I'm helping my elderly mother" or "my father has dementia."
- Risk: N/A — legal/ethical boundary
- System behavior: Explain that changes to another person's account designations require legal authority (power of attorney or court order). Do not provide instructions for making changes. Recommend consulting a lawyer immediately.

## Rule Priority Order
Critical → High → Medium → Low

## Sources
- Canada Revenue Agency (CRA) estate and beneficiary guidance
- Financial Consumer Agency of Canada
- Province-specific estate legislation references