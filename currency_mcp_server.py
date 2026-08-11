
import httpx

from mcp.server import MCPServer


mcp = MCPServer(
    "Currency Converter MCP Server"
)


@mcp.tool()
def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str
) -> dict:
    """
    Convert money from one currency
    to another using the latest exchange rate.
    """

    if amount <= 0:
        raise ValueError(
            "Amount must be greater than zero."
        )

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    url = (
        f"https://api.frankfurter.dev/v1/latest"
        f"?from={from_currency}"
        f"&to={to_currency}"
    )

    response = httpx.get(
        url,
        timeout=10
    )

    if response.status_code != 200:
        raise Exception(
            f"Currency API Error "
            f"{response.status_code}: "
            f"{response.text}"
        )

    data = response.json()

    if to_currency not in data["rates"]:
        raise ValueError(
            f"Currency '{to_currency}' "
            f"not supported."
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


@mcp.tool()
def supported_currencies() -> list[str]:
    """
    Return commonly used currency codes.
    """

    return [
        "USD",
        "EUR",
        "GBP",
        "INR",
        "JPY",
        "AUD",
        "CAD",
        "CHF",
        "CNY",
        "SGD"
    ]


if __name__ == "__main__":
    mcp.run()
