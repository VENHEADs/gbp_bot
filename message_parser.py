import re
import logging

logger = logging.getLogger(__name__)

# Adjusted keywords to be more flexible with text between action and currency
SELL_GBP_KEYWORDS = [
    r"продам.*фунты", r"продам.*гбп", r"продам.*gbp", r"продам.*£",
    r"меняю.*фунты.*на.*рубли", r"меняю.*гбп.*на.*руб", r"меняю.*gbp.*на.*rub", r"меняю.*£.*на.*руб",
    r"обменяю.*фунты.*на.*рубли", r"обменяю.*гбп.*на.*руб", r"обменяю.*gbp.*на.*rub", r"обменяю.*£.*на.*руб",
    r"отдам.*фунты.*за.*рубли", r"отдам.*гбп.*за.*руб", r"отдам.*gbp.*за.*rub", r"отдам.*£.*за.*руб",
    # Simpler patterns if context is clear, but can be noisy. Retaining specific versions too.
    r"фунты.*на.*рубли", r"гбп.*на.*руб", r"gbp.*на.*rub", r"£.*на.*руб", # Order might matter
    r"продаю.*фунты", r"продаю.*гбп", r"продаю.*gbp", r"продаю.*£",
    r"есть.*фунты.*надо.*рубли", r"есть.*гбп.*надо.*руб", r"есть.*gbp.*надо.*rub", r"есть.*£.*надо.*руб",
    r"предлагаю.*фунты", r"предлагаю.*гбп", r"предлагаю.*gbp", r"предлагаю.*£", # Offering GBP
]

BUY_RUB_KEYWORDS = [
    r"куплю.*рубли", r"куплю.*руб", r"куплю.*rub",
    r"нужны.*рубли.*за.*фунты", r"нужны.*руб.*за.*гбп", r"нужны.*rub.*за.*gbp", r"нужны.*руб.*за.*£",
    r"возьму.*рубли.*за.*фунты", r"возьму.*руб.*за.*гбп", r"возьму.*rub.*за.*gbp", r"возьму.*руб.*за.*£",
    r"покупаю.*рубли", r"покупаю.*руб", r"покупаю.*rub",
    r"надо.*рубли.*есть.*фунты", r"надо.*руб.*есть.*гбп", r"надо.*rub.*есть.*gbp", r"надо.*руб.*есть.*£", 
    r"ищу.*рубли", # Looking for RUB
]

CURRENCY_GBP_REGEX = r"\b(gbp|гбп|фунт(?:ов|а|ы|ами|ах)?|£)\b" # Added £ and more endings for фунт
CURRENCY_RUB_REGEX = r"\b(rub|руб(?:л(?:ей|и|я|ь|ями|ях))?|р)\b" # Added more endings for рубль

def extract_amount(text: str, currency_regex_for_this_extraction: str) -> float | None:
    """ 
    Extracts an amount IF it's reasonably close to a specific currency mention defined by the regex.
    This is still basic but tries to link number to a specific currency type.
    """
    try:
        # Find all numbers
        potential_amounts = re.findall(r"(\d[\d\s.,]*\d|\d+)\s*(к|k)?", text, re.IGNORECASE)
        if not potential_amounts:
            return None

        # Find all occurrences of the specific currency we're looking for amount for
        currency_mentions = list(re.finditer(currency_regex_for_this_extraction, text, re.IGNORECASE))
        if not currency_mentions:
            return None

        for num_str, k_suffix in potential_amounts:
            num_val = float(re.sub(r"[\s.,]", "", num_str)) * (1000 if k_suffix.lower() in ['k', 'к'] else 1)
            
            # Check proximity: is this number near any of the currency_mentions?
            # This is a simple character distance check. More sophisticated checks are possible.
            num_match_obj = re.search(re.escape(num_str.split()[0]), text) # Get match object for the number part
            if not num_match_obj: continue
            num_pos = num_match_obj.start()

            for cur_match in currency_mentions:
                cur_pos_start = cur_match.start()
                cur_pos_end = cur_match.end()
                # Check if number is before or after currency mention within a certain window (e.g., 10 chars)
                # Or if currency symbol is directly attached (e.g. £50, 50gbp)
                if (abs(num_pos - cur_pos_end) < 10) or (abs(cur_pos_start - (num_match_obj.end())) < 10) or \
                   (cur_match.group().startswith('£') and num_match_obj.start() == cur_match.end()): # For £50 like patterns
                    return num_val
        return None # No number found close to the specified currency

    except Exception as e:
        logger.debug(f"Error during refined amount extraction: {e}")
    return None

def parse_message_for_offer(text: str) -> dict | None:
    original_text = text
    text_lower = text.lower()
    
    offer_type = None
    amount_gbp = None
    amount_rub = None
    confidence = "low"

    for pattern in SELL_GBP_KEYWORDS:
        if re.search(pattern, text_lower):
            offer_type = "counterparty_sells_gbp"
            confidence = "high"
            logger.info(f"SELL_GBP keyword match on pattern '{pattern}' for text: '{original_text[:70]}...'")
            amount_gbp = extract_amount(text_lower, CURRENCY_GBP_REGEX)
            # If RUB is also mentioned, try to get its amount. (Still simplistic)
            if re.search(CURRENCY_RUB_REGEX, text_lower):
                amount_rub = extract_amount(text_lower, CURRENCY_RUB_REGEX)
            break 

    if not offer_type:
        for pattern in BUY_RUB_KEYWORDS:
            if re.search(pattern, text_lower):
                offer_type = "counterparty_buys_rub"
                confidence = "high"
                logger.info(f"BUY_RUB keyword match on pattern '{pattern}' for text: '{original_text[:70]}...'")
                amount_rub = extract_amount(text_lower, CURRENCY_RUB_REGEX)
                if re.search(CURRENCY_GBP_REGEX, text_lower):
                    amount_gbp = extract_amount(text_lower, CURRENCY_GBP_REGEX)
                break

    if offer_type:
        # If only one currency was strongly identified by keywords, and an amount was extracted for it,
        # we can proceed. The other currency is implied by the context of the group.
        if (offer_type == "counterparty_sells_gbp" and amount_gbp is not None) or \
           (offer_type == "counterparty_buys_rub" and amount_rub is not None):
            # If the other currency wasn't mentioned, make sure its amount is None
            if not re.search(CURRENCY_RUB_REGEX, text_lower) and offer_type == "counterparty_sells_gbp":
                amount_rub = None
            if not re.search(CURRENCY_GBP_REGEX, text_lower) and offer_type == "counterparty_buys_rub":
                amount_gbp = None
            
            return {
                "offer_type": offer_type,
                "amount_gbp": amount_gbp,
                "amount_rub": amount_rub,
                "confidence": confidence,
                "original_message": original_text
            }
        else: # Strong keyword matched, but no amount found for the primary currency of the offer.
              # Or the logic above failed. This might become a potential_mention or None.
              logger.info(f"Offer type '{offer_type}' (high conf) matched, but failed to extract primary amount. Re-evaluating as potential_mention.")
              # Fall through to potential_mention logic if both currencies are present.
              pass # Let it fall through to the potential_mention check

    has_gbp_mention = re.search(CURRENCY_GBP_REGEX, text_lower)
    has_rub_mention = re.search(CURRENCY_RUB_REGEX, text_lower)

    if has_gbp_mention and has_rub_mention:
        logger.info(f"Weak signal (potential_mention): Both GBP & RUB mentioned but no strong keywords OR amount extraction failed for high confidence. Text: '{original_text[:70]}...'")
        # If it was a high confidence but amount extraction failed, it might become low here.
        # Ensure amounts are re-extracted if not already done, or if offer_type was reset.
        current_offer_type_for_potential = offer_type if offer_type else "potential_mention"
        if amount_gbp is None: amount_gbp = extract_amount(text_lower, CURRENCY_GBP_REGEX)
        if amount_rub is None: amount_rub = extract_amount(text_lower, CURRENCY_RUB_REGEX)
        
        return {
            "offer_type": current_offer_type_for_potential, # Could be existing high conf type or potential_mention
            "amount_gbp": amount_gbp,
            "amount_rub": amount_rub,
            "confidence": "low", # Always low if it reaches here due to no strong keywords or amount issues
            "original_message": original_text
        }
        
    # Case: Only GBP mentioned with a selling keyword (like "продаю £50")
    if not offer_type and has_gbp_mention and any(re.search(p,text_lower) for p in [r"продам.*£", r"продаю.*£", r"отдам.*£", r"предлагаю.*£"]):
        logger.info(f"Potential GBP sell (implied RUB): Only GBP mentioned with sell keyword. Text: '{original_text[:70]}...'")
        amount_gbp = extract_amount(text_lower, CURRENCY_GBP_REGEX)
        if amount_gbp:
            return {
                "offer_type": "counterparty_sells_gbp", # Implied RUB context
                "amount_gbp": amount_gbp,
                "amount_rub": None, # RUB is implied, not extracted
                "confidence": "medium", # Higher than potential_mention but lower than explicit two-currency match
                "original_message": original_text
            }

    logger.debug(f"No relevant offer found in text: '{original_text[:70]}...'")
    return None

if __name__ == '__main__':
    test_messages = [
        "Продам 200 фунтов за рубли",
        "Продаю gbp 350, хочу рубли.", 
        "Куплю рубли на 50000.",
        "Нужно 120к рублей, есть фунты", 
        "Привет! Хочу поменять 600 фунтов на рубли",
        "всем привет! обменяю ваши 450к рублей на мои фунты завтра пишите в ЛС",
        "Продам 100к рублей куплю гбп", 
        "Ищу рубли, предлагаю gbp. Сумма 300.", 
        "Есть 1000 фунтов, нужны рубли.", 
        "Текст без конкретики фунты рубли просто так",
        "Тест сбщ: продаю £50.",                     # Test case for £ symbol
        "продам £150 за рубли сейчас",            # Test case for £ symbol with RUB
        "Хочу купить рубли на 100 gbp",             # Test case for buying RUB
        "просто текст с £ и рублями без продажи",  # Potential mention
        "Продам штуку баксов",                       # Irrelevant currency
        "£300 в наличии, нужны рубли",                # GBP sell
    ]
    print("--- Testing Message Parser ---")
    for msg in test_messages:
        result = parse_message_for_offer(msg)
        print(f"Message: '{msg}'") 
        if result:
            print(f"  Parsed: {result}")
        else:
            print("  Parsed: No offer found")
        print("-" * 20)

    print("\n--- Re-evaluating user goal and keywords ---")
    print("User wants to: SELL RUB to BUY GBP.")
    print("This means the bot should look for messages where:")
    print("1. Someone is SELLING GBP (user can buy their GBP with RUB). Keywords: Продам фунты, меняю gbp на rub, etc.")
    print("2. Someone is BUYING RUB (user can sell their RUB to them for GBP). Keywords: Куплю рубли, нужны рубли за gbp, etc.")
    print("The current SELL_GBP_KEYWORDS and BUY_RUB_KEYWORDS should align with this.")
    # SELL_GBP_KEYWORDS look for OTHERS selling GBP. This is correct.
    # BUY_RUB_KEYWORDS look for OTHERS buying RUB. This is also correct.

    # Test case: "Куплю фунты на 200 т.р."
    # This means: "I want to buy Pounds for 200k Rubles".
    # The other person is buying Pounds. The user also wants to buy Pounds. This is not a direct match for the user's *transaction*.
    # The user is looking for someone to transact *with*.
    # If someone says "Куплю фунты", they are on the same side as the user.
    # If someone says "Продам фунты", the user can buy from them. (MATCH)
    # If someone says "Куплю рубли", the user can sell their rubles to them. (MATCH)
    # If someone says "Продам рубли", they are on the same side as the user (selling rubles).
    
    print("\n--- Corrected perspective for test cases ---")
    # User wants to SELL RUB to BUY GBP.
    # Bot looks for:
    #   - Others SELLING GBP (user can buy their GBP) -> parse as "counterparty_sells_gbp"
    #   - Others BUYING RUB (user can sell RUB to them) -> parse as "counterparty_buys_rub"

    # Let's refine SELL_GBP_KEYWORDS for "нужно/надо рублей"
    # It should be "нужно/надо рублей *И* есть/предлагаю фунты/gbp"
    # The current regex `r"есть фунты.*надо рубли"` and `r"надо руб.*есть гбп"` handle this.

    # What about just "Нужно 120к рублей"?
    # If it doesn't mention GBP/фунты, we should probably ignore it or mark it as very low confidence / "potential_rub_needed".
    # For now, it won't be caught by SELL_GBP_KEYWORDS unless gbp/фунты are also in the message.
    # And it won't be caught by BUY_RUB_KEYWORDS.
    # It will be caught by `potential_mention` only if GBP is also mentioned.
    # If only RUB is mentioned, it will be `None`. This seems reasonable. 