def generate_anchor(tab_type, email):
    """Generate 15 numeric anchor using hash of tab_type and email"""
    text = str(tab_type) + email
    return abs(hash(text)) % (10 ** 15)
