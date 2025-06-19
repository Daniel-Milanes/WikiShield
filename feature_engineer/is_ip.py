import ipaddress  # Built-in Python module to work with IPv4 and IPv6 addresses


def is_IP(row):
    """
    Determine whether the 'user' field in a DataFrame
    row represents an IP address.

    Parameters:
        row (pandas.Series): A row from a DataFrame
        containing a 'user' field.

    Returns:
        bool: True if 'user' is a valid IPv4 or IPv6 address
        (indicating an anonymous user), False otherwise
        (likely a registered username).

    Notes:
        This function attempts to parse the 'user' value
        using the ipaddress module. If parsing fails, it assumes
        the value is not an IP address.
    """
    user = row["user"]
    try:
        ipaddress.ip_address(user)
        return True
    except ValueError:
        return False
