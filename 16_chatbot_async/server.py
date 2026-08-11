from fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("Calculator_Server")


@mcp.tool()
def addition(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@mcp.tool()
def subtraction(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


@mcp.tool()
def multiplication(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


@mcp.tool()
def division(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")

    return a / b


@mcp.tool()
def modulo(a: int, b: int) -> int:
    """Return the remainder when a is divided by b."""
    if b == 0:
        raise ValueError("Cannot perform modulo by zero")

    return a % b


@mcp.tool()
def power(a: float, b: float) -> float:
    """Return a raised to the power of b."""
    return a ** b


@mcp.tool()
def average(a: float, b: float) -> float:
    """Return the average of two numbers."""
    return (a + b) / 2


if __name__ == "__main__":
    mcp.run()