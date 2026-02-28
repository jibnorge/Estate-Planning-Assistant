def safe_get(obj, *keys):
    current = obj
    for key in keys:
        if current is None:
            return None
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current
    
def check_province(client):
    findings = []

    province = client.get('province', '')

    # CHECK 1 — Quebec hard stop (Rule Q1)
    if province.lower() in ['quebec', 'qc']:
        findings.append({
            'severity': 'REQUIRES_SPECIALIST',
            'account_id': None,
            'account_type': 'ALL',
            'rule': 'Q1',
            'issue': 'Quebec client — this analysis may be incomplete',
            'consequence': 'Quebec operates under civil law, which is fundamentally different from the rest of Canada. Beneficiary designations on RRSPs and RRIFs work differently — they are made through the contract with the financial institution or through a will, not a simple form. Rules that apply in other provinces may not apply here.',
            'action': 'Consult a Quebec notary before making any estate planning decisions. Do not rely solely on this analysis for Quebec-specific situations.'
        })

    return findings

def check_tfsa_rules(account, client):
    findings = []

    # CHECK 1 — No successor holder AND no beneficiary
    has_successor = safe_get(account, "successor_holder") is not None
    has_beneficiary = safe_get(account, "beneficiary_primary") is not None

    if not has_successor and has_beneficiary:
        findings.append({
            'severity': 'HIGH',
            'account_id': account.get('account_id'),
            'account_type': 'TFSA',
            'rule': 'T1',
            'issue': 'No successor holder or beneficiary named',
            'consequence': 'Account loses tax-free status on death and enters estate — subject to probate delays and tax on growth after death',
            'action': 'Name a successor holder if married or common-law. Name a beneficiary at minimum.'
        })
    # Check 2: Successor holder is no longer a spouse (alive ex)
    is_current_spouse = safe_get(account, "successor_holder", "is_currently_spouse")

    if is_current_spouse is False:
        findings.append({
            'severity': 'CRITICAL',
            'account_id': account.get('account_id'),
            'account_type': 'TFSA',
            'rule': 'T3',
            'issue': 'Successor holder on TFSA is an ex-spouse',
            'consequence': 'Ex-spouse legally inherits the entire TFSA tax-free and immediately upon death. Divorce does not remove this automatically. Your will cannot override it. There is no recovery once it happens.',
            'action': 'Update successor holder immediately. This is the single most urgent fix in your estate plan.'
        })
        
    # Check 3: Successor holder or beneficiary is deceased
    is_successor_alive = safe_get(account, "successor_holder", "is_currently_alive")
    is_beneficiary_alive = safe_get(account, "beneficiary_primary", "is_currently_alive")

    if is_successor_alive is False:
        findings.append({
            'severity': 'CRITICAL',
            'account_id': account.get('account_id'),
            'account_type': 'TFSA',
            'rule': 'T6',
            'issue': 'Successor holder on TFSA is deceased',
            'consequence': 'The designation has failed. The account will fall into your estate as if no successor holder was ever named — probate applies, tax-free status is lost on post-death growth.',
            'action': 'Name a new successor holder immediately. Consider adding a contingent beneficiary as a backup.'
        })

    if is_beneficiary_alive is False:
        findings.append({
            'severity': 'CRITICAL',
            'account_id': account.get('account_id'),
            'account_type': 'TFSA',
            'rule': 'T6',
            'issue': 'Primary beneficiary on TFSA is deceased',
            'consequence': 'The designation has failed. Account falls into estate — probate, delays, and loss of tax-free status on any growth after date of death.',
            'action': 'Update beneficiary to a living person immediately. Add a contingent beneficiary as a backup going forward.'
        })

    
    # CHECK 4 — Married client named spouse as beneficiary but not successor holder (Rule T2)
    is_married = safe_get(client, "marital_status") == "married"
    beneficiary_relationship = safe_get(account, 'beneficiary_primary', 'relationship')
    has_successor_holder = safe_get(account, 'successor_holder') is not None

    if is_married and beneficiary_relationship == 'spouse' and not has_successor_holder:
        findings.append({
            'severity': 'MEDIUM',
            'account_id': account.get('WS'),
            'account_type': 'TFSA',
            'rule': 'T2',
            'issue': 'Spouse named as beneficiary instead of successor holder',
            'consequence': 'Spouse receives the money tax-free but the account itself closes. They lose the contribution room and tax-free status of the account. Successor holder designation would have preserved both.',
            'action': 'Upgrade designation from beneficiary to successor holder. Your spouse keeps the account itself, not just the cash.'
        })

    # CHECK 5 — Minor child named as beneficiary (Rule T5)
    beneficiary_name = safe_get(account, 'beneficiary_primary', 'name')
    children = client.get('children', [])
    beneficiary_is_minor = any(
        child['name'] == beneficiary_name and child.get('is_minor') is True
        for child in children
    )

    if beneficiary_name is not None and beneficiary_is_minor:
        findings.append({
            'severity': 'MEDIUM',
            'account_id': account.get('WS'),
            'account_type': 'TFSA',
            'rule': 'T5',
            'issue': 'Minor child named as TFSA beneficiary',
            'consequence': 'Minors cannot legally receive large sums directly. A court-appointed trustee will control the funds until the child reaches age of majority (18 or 19 depending on province). This creates legal costs and delays — and the child still gets the money at 18 regardless of maturity.',
            'action': 'Consider naming the other parent as beneficiary instead, or establish a formal trust with conditions for when and how the child receives the funds.'
        })

    # CHECK 6 — No contingent beneficiary named (Rule C6)
    has_primary = safe_get(account, 'beneficiary_primary') is not None
    has_contingent = safe_get(account, 'beneficiary_contingent') is not None

    if has_primary and not has_contingent:
        findings.append({
            'severity': 'MEDIUM',
            'account_id': account.get('WS'),
            'account_type': 'TFSA',
            'rule': 'C6',
            'issue': 'No contingent beneficiary named on TFSA',
            'consequence': 'If your primary beneficiary dies before you and you have not updated the designation, the account falls to your estate. A contingent beneficiary is a backup that prevents this automatically.',
            'action': 'Name a contingent beneficiary on this account. Common choices are adult children, a sibling, or a trusted person.'
        })

    return findings

def check_rrsp_rules(account, client):
    findings = []

    # CHECK 1 — No beneficiary and no successor annuitant (Rule R1)
    has_successor_annuitant = safe_get(account, 'successor_annuitant') is not None
    has_beneficiary = safe_get(account, 'beneficiary_primary') is not None

    if not has_successor_annuitant and not has_beneficiary:
        findings.append({
            'severity': 'HIGH',
            'account_id': account.get('account_id'),
            'account_type': 'RRSP',
            'rule': 'R1',
            'issue': 'No beneficiary or successor annuitant named on RRSP',
            'consequence': 'Full RRSP value is added to your income in the year of death. On a $200,000 RRSP this could mean $80,000-$100,000 in unexpected taxes. Account also enters probate — delays and additional costs on top of the tax hit.',
            'action': 'If married or common-law: name your spouse as successor annuitant immediately. If single: name a beneficiary. Either is far better than nothing.'
        })

    # CHECK 2 — Married client but spouse named as beneficiary not successor annuitant (Rule R2)
    is_married = client.get('marital_status') == 'married'
    beneficiary_relationship = safe_get(account, 'beneficiary_primary', 'relationship')
    has_successor_annuitant = safe_get(account, 'successor_annuitant') is not None

    if is_married and beneficiary_relationship == 'spouse' and not has_successor_annuitant:
        findings.append({
            'severity': 'MEDIUM',
            'account_id': account.get('account_id'),
            'account_type': 'RRSP',
            'rule': 'R2',
            'issue': 'Spouse named as beneficiary instead of successor annuitant on RRSP',
            'consequence': 'Spouse receives the RRSP tax-free via spousal rollover — which is good. But the process is more complex than successor annuitant. The account closes and spouse receives a lump sum transfer rather than inheriting the account itself.',
            'action': 'Upgrade designation to successor annuitant. Cleaner transfer, same tax benefit, less administrative burden on your spouse during an already difficult time.'
        })

    # CHECK 3 — Ex-spouse still listed as successor annuitant (Rule R3)
    annuitant_is_current_spouse = safe_get(account, 'successor_annuitant', 'is_currently_spouse')

    if annuitant_is_current_spouse is False:
        findings.append({
            'severity': 'CRITICAL',
            'account_id': account.get('account_id'),
            'account_type': 'RRSP',
            'rule': 'R3',
            'issue': 'Ex-spouse still listed as successor annuitant on RRSP',
            'consequence': 'Ex-spouse legally receives the entire RRSP. This is ironclad — your will cannot override it, courts will generally not override it. The ex-spouse keeps the money. Divorce does not automatically remove this designation.',
            'action': 'Update this immediately. This is the highest priority fix for any recently divorced client.'
        })

    # CHECK 4 — Ex-spouse still listed as primary beneficiary (Rule R3 variant)
    beneficiary_is_current_spouse = safe_get(account, 'beneficiary_primary', 'is_currently_spouse')

    if beneficiary_is_current_spouse is False:
        findings.append({
            'severity': 'CRITICAL',
            'account_id': account.get('account_id'),
            'account_type': 'RRSP',
            'rule': 'R3',
            'issue': 'Ex-spouse still listed as primary beneficiary on RRSP',
            'consequence': 'Ex-spouse legally receives the full RRSP value. They will also owe income tax on the full amount that year — but that does not reduce what they receive. Your will cannot override this designation.',
            'action': 'Update beneficiary designation immediately.'
        })

    # CHECK 5 — Primary beneficiary is deceased (Rule R6 variant)
    beneficiary_is_alive = safe_get(account, 'beneficiary_primary', 'is_currently_alive')

    if beneficiary_is_alive is False:
        findings.append({
            'severity': 'CRITICAL',
            'account_id': account.get('account_id'),
            'account_type': 'RRSP',
            'rule': 'R6',
            'issue': 'Primary beneficiary on RRSP is deceased',
            'consequence': 'Designation has failed. Full RRSP value collapses into your estate as income in year of death — maximum tax exposure plus probate delays. Treated as if no beneficiary was ever named.',
            'action': 'Update beneficiary immediately. Consider naming a contingent beneficiary as a permanent backup.'
        })

    # CHECK 6 — Non-spouse adult named as beneficiary — tax surprise warning (Rule R4)
    beneficiary_relationship = safe_get(account, 'beneficiary_primary', 'relationship')
    non_spouse_relationships = ['brother', 'sister', 'sibling', 'friend', 'parent', 'mother', 'father']
    balance = account.get('balance', 0)

    if beneficiary_relationship in non_spouse_relationships and balance > 0:
        findings.append({
            'severity': 'MEDIUM',
            'account_id': account.get('account_id'),
            'account_type': 'RRSP',
            'rule': 'R4',
            'issue': f'Non-spouse ({beneficiary_relationship}) named as RRSP beneficiary — significant tax consequence',
            'consequence': f'Your {beneficiary_relationship} receives the full RRSP value but it is added entirely to their income that year. On this account balance of ${balance:,} they could owe ${int(balance * 0.40):,}+ in taxes the same year they receive it. This is often a complete surprise.',
            'action': 'Make sure your beneficiary understands this tax consequence. Consider life insurance as a strategy to cover the tax bill, or review whether this designation still reflects your intent.'
        })

    # CHECK 7 — Minor child named as beneficiary (Rule R5 context)
    beneficiary_name = safe_get(account, 'beneficiary_primary', 'name')
    children = client.get('children', [])
    beneficiary_is_minor = any(
        child['name'] == beneficiary_name and child.get('is_minor') is True
        for child in children
    )

    if beneficiary_name is not None and beneficiary_is_minor:
        findings.append({
            'severity': 'MEDIUM',
            'account_id': account.get('account_id'),
            'account_type': 'RRSP',
            'rule': 'R5',
            'issue': 'Minor child named as RRSP beneficiary',
            'consequence': 'Minor children cannot receive RRSP proceeds directly. A court-appointed trustee controls the funds until age of majority. However — if the child is financially dependent due to disability, there are favorable tax rules available that require specific documentation to claim.',
            'action': 'Confirm whether the child qualifies as a financially dependent minor or disabled dependent. If yes, ensure dependency is documented. If no, consider naming the other parent or establishing a trust.'
        })

    # CHECK 8 — No contingent beneficiary (Rule C6)
    has_primary = safe_get(account, 'beneficiary_primary') is not None
    has_contingent = safe_get(account, 'beneficiary_contingent') is not None

    if has_primary and not has_contingent:
        findings.append({
            'severity': 'MEDIUM',
            'account_id': account.get('account_id'),
            'account_type': 'RRSP',
            'rule': 'C6',
            'issue': 'No contingent beneficiary named on RRSP',
            'consequence': 'If your primary beneficiary dies before you and the designation is not updated, the full RRSP value collapses into your estate — maximum tax exposure and probate delays.',
            'action': 'Name a contingent beneficiary. On an RRSP this is especially important given the tax consequences of the account entering the estate.'
        })

    return findings


def check_rrif_rules(account, client):
    findings = []

    # CHECK 1 — No successor annuitant and no beneficiary (Rule R1 equivalent)
    has_successor_annuitant = safe_get(account, 'successor_annuitant') is not None
    has_beneficiary = safe_get(account, 'beneficiary_primary') is not None

    if not has_successor_annuitant and not has_beneficiary:
        findings.append({
            'severity': 'HIGH',
            'account_id': account.get('account_id'),
            'account_type': 'RRIF',
            'rule': 'R1',
            'issue': 'No beneficiary or successor annuitant named on RRIF',
            'consequence': 'Full RRIF value is added to your income in the year of death — potentially the largest single tax bill your estate will face. Account enters probate on top of the tax hit.',
            'action': 'Name your spouse as successor annuitant immediately. If no spouse, name a beneficiary. Do not leave this blank.'
        })

    # CHECK 2 — Successor annuitant is deceased (Rule T6 equivalent)
    annuitant_is_alive = safe_get(account, 'successor_annuitant', 'is_currently_alive')

    if annuitant_is_alive is False:
        findings.append({
            'severity': 'CRITICAL',
            'account_id': account.get('account_id'),
            'account_type': 'RRIF',
            'rule': 'R6',
            'issue': 'Successor annuitant on RRIF is deceased',
            'consequence': 'The designation has failed. The full RRIF balance collapses into your estate as income in the year of death. On large RRIFs this can mean a six-figure tax bill with no liquid assets to pay it.',
            'action': 'Update successor annuitant immediately. Review whether your estate has enough liquid assets to cover the potential tax liability.'
        })

    # CHECK 3 — Primary beneficiary is deceased (Rule T6 equivalent)
    beneficiary_is_alive = safe_get(account, 'beneficiary_primary', 'is_currently_alive')

    if beneficiary_is_alive is False:
        findings.append({
            'severity': 'CRITICAL',
            'account_id': account.get('account_id'),
            'account_type': 'RRIF',
            'rule': 'R6',
            'issue': 'Primary beneficiary on RRIF is deceased',
            'consequence': 'Designation has failed. Full RRIF value enters estate as taxable income in year of death. With no liquid assets to cover the bill, the executor may be forced to sell other estate assets.',
            'action': 'Update beneficiary immediately. Given the size of most RRIFs, also review estate liquidity — is there enough cash outside this account to pay the tax bill?'
        })

    # CHECK 4 — Ex-spouse still listed as successor annuitant (Rule R3)
    annuitant_is_current_spouse = safe_get(account, 'successor_annuitant', 'is_currently_spouse')

    if annuitant_is_current_spouse is False:
        findings.append({
            'severity': 'CRITICAL',
            'account_id': account.get('account_id'),
            'account_type': 'RRIF',
            'rule': 'R3',
            'issue': 'Ex-spouse still listed as successor annuitant on RRIF',
            'consequence': 'Ex-spouse steps into your RRIF and continues receiving payments as if the account were always theirs. This cannot be undone after death. Your will cannot override it.',
            'action': 'Update immediately. Highest priority fix.'
        })

    # CHECK 5 — Large RRIF with no liquid non-registered assets (Rule R7)
    balance = account.get('balance', 0)
    all_accounts = client.get('accounts', [])
    non_registered_balance = sum(
        a.get('balance', 0)
        for a in all_accounts
        if a.get('type') == 'non-registered'
    )

    if balance > 100000 and non_registered_balance < (balance * 0.30):
        findings.append({
            'severity': 'HIGH',
            'account_id': account.get('account_id'),
            'account_type': 'RRIF',
            'rule': 'R7',
            'issue': 'Large RRIF with insufficient liquid assets to cover potential estate tax bill',
            'consequence': f'This RRIF is worth ${balance:,}. If it collapses into the estate, the tax bill could reach ${int(balance * 0.40):,}+. Your non-registered assets total only ${non_registered_balance:,} — potentially not enough to cover it. The executor may be forced to sell assets or borrow.',
            'action': 'Review estate liquidity with a financial advisor. Life insurance is often used specifically to fund this tax liability.'
        })

    # CHECK 6 — No contingent beneficiary (Rule C6)
    has_primary = safe_get(account, 'beneficiary_primary') is not None
    has_contingent = safe_get(account, 'beneficiary_contingent') is not None

    if has_primary and not has_contingent:
        findings.append({
            'severity': 'MEDIUM',
            'account_id': account.get('account_id'),
            'account_type': 'RRIF',
            'rule': 'C6',
            'issue': 'No contingent beneficiary named on RRIF',
            'consequence': 'If primary beneficiary predeceases you and designation is not updated, the full RRIF value enters your estate as taxable income. The stakes on a RRIF are higher than most accounts given the tax exposure.',
            'action': 'Name a contingent beneficiary on this account as a permanent safety net.'
        })

    return findings


def check_life_events(client):
    findings = []

    # CHECK 1 — Recently married but no updates made (Rule L1)
    marital_status = client.get('marital_status')
    marriage_date = client.get('marriage_date')
    accounts = client.get('accounts', [])

    if marital_status == 'married' and marriage_date:
        any_account_names_spouse = any(
            safe_get(a, 'successor_holder', 'relationship') == 'spouse' or
            safe_get(a, 'successor_annuitant', 'relationship') == 'spouse' or
            safe_get(a, 'beneficiary_primary', 'relationship') == 'spouse'
            for a in accounts
        )

        if not any_account_names_spouse:
            findings.append({
                'severity': 'HIGH',
                'account_id': None,
                'account_type': 'ALL',
                'rule': 'L1',
                'issue': 'Recently married but spouse not named on any account',
                'consequence': 'Your new spouse has no legal claim to any of your registered accounts. In most provinces marriage does not automatically update beneficiary designations. If you die tomorrow your spouse may receive nothing from your investment accounts.',
                'action': 'Review and update all account designations to reflect your marriage. Update your will at the same time.'
            })

    # CHECK 2 — Recently divorced but designations not updated (Rule L2)
    if marital_status == 'divorced':
        any_account_names_ex = any(
            safe_get(a, 'successor_holder', 'is_currently_spouse') is False or
            safe_get(a, 'successor_annuitant', 'is_currently_spouse') is False or
            safe_get(a, 'beneficiary_primary', 'is_currently_spouse') is False
            for a in accounts
        )

        if any_account_names_ex:
            findings.append({
                'severity': 'CRITICAL',
                'account_id': None,
                'account_type': 'ALL',
                'rule': 'L2',
                'issue': 'Recently divorced but ex-spouse still named on one or more accounts',
                'consequence': 'Divorce does NOT automatically remove beneficiary designations in Canada. Your ex-spouse will legally inherit every account still named in their favour. Your will cannot override this. This is the most common and costly estate planning mistake Canadians make.',
                'action': 'Treat this as an emergency. Update every account designation today. Do not wait.'
            })

    # CHECK 3 — New child but no accounts updated (Rule L3)
    children = client.get('children', [])
    has_newborn = any(
        child.get('age_months') is not None and child.get('age_months') <= 12
        for child in children
    )

    if has_newborn:
        any_account_names_child = any(
            safe_get(a, 'beneficiary_primary', 'relationship') in ['child', 'son', 'daughter'] or
            safe_get(a, 'beneficiary_contingent', 'relationship') in ['child', 'son', 'daughter']
            for a in accounts
        )

        if not any_account_names_child:
            findings.append({
                'severity': 'MEDIUM',
                'account_id': None,
                'account_type': 'ALL',
                'rule': 'L3',
                'issue': 'New child not reflected in any account designations',
                'consequence': 'Your new child receives nothing from your registered accounts by default. If your will also predates the child, they may be inadequately provided for entirely. There is also no formal guardian named if both parents die.',
                'action': 'Review all account designations with your new child in mind. Update your will immediately and name a guardian.'
            })

    # CHECK 4 — Common-law partner not designated anywhere (Rule L5)
    current_partner = client.get('current_partner')
    if current_partner:
        months_together = current_partner.get('months_living_together', 0) or 0
        cohabitation_start = current_partner.get('cohabitation_start')

        if cohabitation_start:
            from datetime import datetime
            start = datetime.strptime(cohabitation_start, '%Y-%m-%d')
            months_together = (datetime.now() - start).days // 30

        if months_together >= 12:
            any_account_names_partner = any(
                safe_get(a, 'successor_holder', 'relationship') == 'common-law' or
                safe_get(a, 'successor_annuitant', 'relationship') == 'common-law' or
                safe_get(a, 'beneficiary_primary', 'relationship') == 'common-law'
                for a in accounts
            )

            if not any_account_names_partner:
                findings.append({
                    'severity': 'MEDIUM',
                    'account_id': None,
                    'account_type': 'ALL',
                    'rule': 'L5',
                    'issue': f'Common-law partner of {months_together} months not named on any account',
                    'consequence': 'Your common-law partner qualifies for the same tax advantages as a married spouse in Canada — but only if properly designated. Without any designation they receive nothing from your registered accounts.',
                    'action': 'Update designations to reflect your common-law relationship. Note that common-law rules vary by province — confirm your province\'s definition applies to your situation.'
                })

    # CHECK 5 — No will at all (Rule L1)
    has_will = client.get('has_will', False)

    if not has_will:
        findings.append({
            'severity': 'HIGH',
            'account_id': None,
            'account_type': 'ALL',
            'rule': 'L0',
            'issue': 'No will on file',
            'consequence': 'Without a will, provincial intestacy rules decide who gets everything — not you. For clients with children this also means no guardian is formally named. The courts decide. Registered accounts with named beneficiaries bypass this, but everything else does not.',
            'action': 'Create a will as soon as possible. This is especially urgent if you have children, a common-law partner, or significant non-registered assets.'
        })

    # CHECK 6 — Will is severely outdated
    will_last_updated = client.get('will_last_updated')

    if will_last_updated:
        from datetime import datetime
        updated = datetime.strptime(will_last_updated, '%Y-%m-%d')
        years_since_update = (datetime.now() - updated).days // 365

        if years_since_update >= 10:
            findings.append({
                'severity': 'MEDIUM',
                'account_id': None,
                'account_type': 'ALL',
                'rule': 'L0',
                'issue': f'Will has not been updated in {years_since_update} years',
                'consequence': 'A will that predates major life events — marriage, divorce, children, significant assets — may no longer reflect your wishes. Named executors or beneficiaries in the will may have died or become estranged.',
                'action': 'Review your will with an estate lawyer. At minimum confirm the executor is still willing and able, and that the beneficiaries still reflect your wishes.'
            })

    return findings


def check_cross_account(client):
    findings = []
    accounts = client.get('accounts', [])

    # CHECK 1 — Complete gap across all accounts (Rule C5)
    def account_has_any_designation(account):
        return (
            safe_get(account, 'successor_holder') is not None or
            safe_get(account, 'successor_annuitant') is not None or
            safe_get(account, 'beneficiary_primary') is not None
        )

    all_accounts_empty = not any(
        account_has_any_designation(a) for a in accounts
    )

    if all_accounts_empty and len(accounts) > 0:
        findings.append({
            'severity': 'CRITICAL',
            'account_id': None,
            'account_type': 'ALL',
            'rule': 'C5',
            'issue': 'No beneficiary named on any account — complete estate planning gap',
            'consequence': 'Your entire investment portfolio will go through probate. Maximum tax exposure on all registered accounts. Maximum delays for your family. Everything becomes public record through probate court. This is the worst possible estate planning outcome.',
            'action': 'This requires immediate attention across every account. Start with your RRSP or RRIF — the tax consequences there are the most severe.'
        })

    # CHECK 2 — Inconsistent designations across accounts (Rule C1)
    designated_accounts = [a for a in accounts if account_has_any_designation(a)]
    undesignated_accounts = [a for a in accounts if not account_has_any_designation(a)]

    if len(designated_accounts) > 0 and len(undesignated_accounts) > 0:
        undesignated_types = [a.get('type') for a in undesignated_accounts]
        findings.append({
            'severity': 'HIGH',
            'account_id': None,
            'account_type': 'ALL',
            'rule': 'C2',
            'issue': f'Beneficiaries named on some accounts but missing on others: {", ".join(undesignated_types)}',
            'consequence': 'Creates a two-tier distribution. Some accounts transfer quickly and tax-efficiently to your named beneficiaries. The undesignated accounts go through probate — slower, more expensive, and in the case of registered accounts, with full tax exposure.',
            'action': f'Complete beneficiary designations on: {", ".join(undesignated_types)}.'
        })

    return findings

def analyze_estate_gaps(client_profile):
    findings = []

    findings += check_province(client_profile)

    for account in client_profile.get("accounts", []):
        account_type = account.get('type')

        if account_type == 'TFSA':
            findings += check_tfsa_rules(account, client_profile)
        elif account_type == 'RRSP':
            findings += check_rrsp_rules(account, client_profile)
        elif account_type == 'RRIF':
            findings += check_rrif_rules(account, client_profile)
    
    findings += check_life_events(client_profile)

    findings += check_cross_account(client_profile)

    severity_order = {
        'CRITICAL': 0,
        'REQUIRES_SPECIALIST': 1,
        'HIGH': 2,
        'MEDIUM': 3,
        'LOW': 4
    }
    findings.sort(key = lambda f: severity_order.get(f['severity'], 99))

    return findings
    