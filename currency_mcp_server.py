
import httpx

from mcp.server import MCPServer


mcp = MCPServer("Currency Converter MCP Server")


@mcp.tool()
def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str
) -> dict:
    """
    Convert an amount from one currency to another
    using the latest exchange rate.

    Args:
        amount: Amount of money to convert.
        from_currency: Source currency code such as USD, EUR, GBP or INR.
        to_currency: Target currency code such as USD, EUR, GBP or INR.
    """

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    url = (
        f"https://api.frankfurter.app/latest"
        f"?from={from_currency}"
        f"&to={to_currency}"
    )

    response = httpx.get(
        url,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if to_currency not in data["rates"]:
        raise ValueError(
            f"Currency '{to_currency}' was not found."
        )

    rate = data["rates"][to_currency]

    converted_amount = amount * rate

    return {
        "amount": amount,
        "from_currency": from_currency,
        "to_currency": to_currency,
        "exchange_rate": rate,
        "converted_amount": round(
            converted_amount,
            2
        ),
        "date": data["date"]
    }


if __name__ == "__main__":
    mcp.run()
